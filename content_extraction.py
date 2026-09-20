"""
content_extraction.py
======================
Retrieval layer for the QuickQuery RAG pipeline.
 
Responsibilities:
- Embed the user's natural language query using SentenceTransformer
- Query Pinecone for the top-K most semantically similar schema chunks
- Re-rank the candidates using a cross-encoder model for higher precision
- Filter out low-confidence results using a minimum score threshold
- Return the final top chunks as structured dicts for prompt construction
 
Pipeline position:
    User query → [content_extraction] → schema chunks
                                             ↓
                                       prompt_creation
                                             ↓
                                          generation
 
Models used:
    Bi-encoder  : SentenceTransformer (set via EMBEDDING_MODEL in .env)
                  Produces the query vector for fast Pinecone ANN search.
    Cross-encoder: cross-encoder/ms-marco-MiniLM-L6-v2
                  Re-scores (query, schema) pairs for higher precision.
                  Slower but more accurate than the bi-encoder alone.
 
Two-stage retrieval:
    Stage 1 — Pinecone ANN search fetches top_k candidates quickly.
    Stage 2 — Cross-encoder re-ranks candidates by relevance score,
              then the bottom results are filtered by MIN_SCORE_THRESHOLD
              before the final top final_k chunks are returned.
"""

import json
from sentence_transformers import SentenceTransformer, CrossEncoder
import os
from dotenv import load_dotenv
from global_veriables import PINECONE_CLIENT, INDEX_NAME, CANDIDATE_K, FINAL_TOP_K


# load_dotenv() is already called in global_veriables.py (imported above), but kept here so this module also works in standalone/test contexts.
load_dotenv()

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

# Module-level model references — initialised lazily on first use via _get_models() to avoid loading heavy model weights at import time.
_EMBEDDING_MODEL: SentenceTransformer | None = None
_RERANKER_MODEL: CrossEncoder | None = None



def _get_models() -> tuple[SentenceTransformer, CrossEncoder]:
    """
    Lazy-initialise and return the embedding and reranker models.
 
    Models are loaded into memory only on the first call to content_extraction(), not at import time. Subsequent calls reuse the already-loaded instances (module-level singletons).
 
    Returns:
        tuple: (SentenceTransformer instance, CrossEncoder instance)
    """
    global _EMBEDDING_MODEL, _RERANKER_MODEL

    if _EMBEDDING_MODEL is None:
        print("[INFO] Loading embedding model...")
        _EMBEDDING_MODEL = SentenceTransformer(
            os.environ.get("EMBEDDING_MODEL"),
            token=os.environ.get("HUGGINGFACE_API_KEY")
        )
    
    if _RERANKER_MODEL is None:
        print("[INFO] Loading reranker model...")
        # cross-encoder/ms-marco-MiniLM-L6-v2 is a lightweight but accurate cross-encoder trained on MS MARCO passage ranking.
        # It scores (query, document) pairs directly rather than comparing independent embeddings.
        _RERANKER_MODEL = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L6-v2"
        )
    
    return _EMBEDDING_MODEL, _RERANKER_MODEL


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def content_extraction(
        user_query:str, 
        top_k:int = 5, 
        final_k:int = 3
) -> list[dict]:
    """
    Retrieve the most relevant schema chunks for a given user query
    using two-stage retrieval: ANN search followed by cross-encoder reranking.
 
    Stage 1 — Pinecone ANN search:
        The user query is embedded and used to query Pinecone for the top_k most similar schema vectors by cosine similarity.
 
    Stage 2 — Cross-encoder reranking:
        Each (query, candidate_metadata) pair is scored by the cross-encoder.
        Candidates are re-sorted by rerank score (descending).
        Candidates below MIN_SCORE_THRESHOLD are discarded.
        The best final_k survivors are returned.
 
    Args:
        user_query: The natural language question from the user
                    (e.g. "which customer spent the most money").
        top_k:      Number of candidates to fetch from Pinecone before
                    reranking. More candidates = better reranking pool
                    but slower inference. Default: 5.
        final_k:    Number of top-ranked chunks to return after reranking
                    and threshold filtering. Default: 3.
 
    Returns:
        list[dict]: Up to final_k schema chunks, each with keys:
            "semantic_score" — cosine similarity score from Pinecone (0 to 1)
            "rerank_score"   — cross-encoder score (higher = more relevant)
            "content"        — JSON string of the schema metadata
        Returns [] if Pinecone returns no matches or all candidates
        fall below MIN_SCORE_THRESHOLD.
    """

    embedding_model, reranker_model = _get_models()

    index = PINECONE_CLIENT.Index(name=INDEX_NAME)

    # --- Stage 1: Embed query and search Pinecone ---
    query_embedding = embedding_model.encode(user_query).tolist()

    response = index.query(
        vector=query_embedding,
        top_k= top_k,
        include_metadata= True
    )

    if not response.matches:
        return []
    
    candidates = response.matches


    # --- Stage 2: Cross-encoder reranking ---
    # Build (query, serialised_metadata) pairs for the cross-encoder.
    # The metadata JSON is used as the "document" text because it contains the full column descriptions, types, and FK details the model needs to judge relevance.
    pairs = [
        (user_query, json.dumps(c.metadata, indent=2)) for c in candidates
    ]

    rerank_scores = reranker_model.predict(pairs)

    # Combine Pinecone scores and rerank scores into one list for sorting
    scored = [
        {
            "semantic_score": round(candidates[i].score, 4),
            "rerank_score": round(float(rerank_scores[i]), 4),
            "metadata": candidates[i].metadata
        }
        for i in range(len(candidates))
    ]

    # Sort by rerank score descending — rerank score is the primary signal
    scored.sort(
        key=lambda x: x['rerank_score'], reverse=True
    )
    
    # Return the best final_k chunks that passed the threshold
    top_chunks = scored[:final_k]

    return [
        {
            "semantic_score": res["semantic_score"],
            "rerank_score": res["rerank_score"],
            "content": json.dumps(res["metadata"], indent=4)
        } 
        for res in top_chunks
    ]
