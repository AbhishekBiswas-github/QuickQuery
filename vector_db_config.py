"""
vector_db_config.py
====================
One-time setup script for the QuickQuery Pinecone vector index.

Responsibilities:
- Create the Pinecone index if it does not already exist
- Fetch full schema metadata from MySQL via get_main_sql()
- Convert each table's schema dict into a plain-text string for embedding
- Embed each schema string using SentenceTransformer
- Upsert all schema vectors (with metadata) into Pinecone in batches

When to run:
    Run this script ONCE after setting up the MySQL database, or any time
    the database schema changes (new tables, renamed columns, etc.).
    It is NOT imported by the main application at runtime — it is a
    standalone setup utility.

    Run with:
        python vector_db_config.py

Skipped automatically:
    If the Pinecone index already exists, the script exits without
    re-embedding or re-upserting anything. To force a full rebuild,
    delete the index manually from the Pinecone console first.
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from mysql_connection import get_main_sql
from global_veriables import PINECONE_CLIENT, INDEX_NAME, CLOUD_SPECS

# load_dotenv() is already called in global_veriables.py (imported above),
# but kept here so this script also works when run standalone without
# going through the normal import chain.
load_dotenv()


# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------

# SentenceTransformer model used to embed schema text into dense vectors.
# Model name and HuggingFace token are read from .env.
# The same model name must be used in content_extraction.py for query
# embeddings — mismatched models will produce incompatible vector spaces.
EMBEDDING_MODEL = SentenceTransformer(
    os.environ.get("EMBEDDING_MODEL"),
    token=os.environ.get("HUGGINGFACE_API_KEY")
)


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def creating_index(index_name: str) -> bool:
    """
    Create a Pinecone serverless index if it does not already exist.

    Uses cosine similarity as the distance metric, which is standard
    for SentenceTransformer embeddings.

    Args:
        index_name: The name of the Pinecone index to create.

    Returns:
        True  — index was newly created; caller should proceed with upsert.
        False — index already exists; upsert can be skipped.
    """
    existing_indexes = [index.name for index in PINECONE_CLIENT.list_indexes()]

    # BUG FIX: was using the global INDEX_NAME constant instead of the
    # index_name parameter, making the parameter completely ignored.
    if index_name not in existing_indexes:
        PINECONE_CLIENT.create_index(
            name=index_name,
            dimension=EMBEDDING_MODEL.get_sentence_embedding_dimension(),
            metric="cosine",
            spec=CLOUD_SPECS
        )
        print(f"[INFO] Index '{index_name}' created successfully.")
        return True
    else:
        print(f"[INFO] Index '{index_name}' already exists. Skipping creation.")
        return False


# ---------------------------------------------------------------------------
# Schema serialisation
# ---------------------------------------------------------------------------

def schema_to_string(schema: dict) -> str:
    """
    Serialise a single table's schema dict into a plain-text string
    suitable for embedding.

    The output string concatenates:
        - Table name header
        - One line per column (with description, type, key info, etc.)
        - Total record count
        - Foreign key relationship(s) or a "no FK" message

    This text is what gets encoded by the embedding model, so the
    quality and completeness of this string directly affects retrieval
    accuracy during RAG.

    Args:
        schema: A table schema dict as returned by get_schemas() in
                mysql_connection.py. Expected keys:
                    "table_name", "column_details",
                    "total_records", "foreign_key_details"

    Returns:
        A newline-joined string representation of the schema.
    """
    lines = [f"TABLE_NAME: {schema['table_name']}"]

    # Each column detail is already a formatted string from get_schemas()
    for col in schema["column_details"]:
        lines.append(col)

    lines.append(schema["total_records"])

    # foreign_key_details is either a list of FK strings (if FKs exist)
    # or a single "No foreign key..." string (if none exist)
    fk = schema["foreign_key_details"]
    if isinstance(fk, list):
        lines.extend(fk)
    else:
        lines.append(fk)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Embedding and upsert
# ---------------------------------------------------------------------------

def schema_upsert(schemas: list[dict], batch_size: int = 100) -> None:
    """
    Embed each schema dict and upsert its vector + metadata into Pinecone.

    Processes schemas in batches to stay within Pinecone's upsert size
    limits and avoid holding all vectors in memory at once.

    Metadata stored per vector:
        table         — table name string (used for metadata filtering)
        columns       — list of column detail strings
        total_records — row count string
        foreign_key   — FK relationship list or "no FK" string

    Note on metadata key naming:
        Keys use underscores (e.g. "total_records", "foreign_key") to
        avoid spaces, which can cause issues with Pinecone metadata filters.

    Args:
        schemas:    List of schema dicts from get_schemas().
        batch_size: Maximum number of vectors per upsert call.
                    Default 100 is well within Pinecone's limits.
    """
    index = PINECONE_CLIENT.Index(name=INDEX_NAME)

    # Build vectors one batch at a time to avoid holding everything in memory
    for batch_start in range(0, len(schemas), batch_size):
        batch_schemas = schemas[batch_start:batch_start + batch_size]
        batch_vectors = []

        for i, schema in enumerate(batch_schemas):
            vector_id = f"quickquery_{batch_start + i}"
            embedding = EMBEDDING_MODEL.encode(
                schema_to_string(schema)
            ).tolist()

            batch_vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "table":         schema["table_name"],
                    "columns":       schema["column_details"],
                    "total_records": schema["total_records"],
                    "foreign_key":   schema["foreign_key_details"]
                }
            })

        index.upsert(vectors=batch_vectors)
        batch_num = batch_start // batch_size + 1
        print(f"[INFO] Upserted batch {batch_num} ({len(batch_vectors)} vectors).")

    print(f"[INFO] {len(schemas)} schema vectors upserted successfully.")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def vector_creation() -> None:
    """
    Orchestrate the full one-time index creation and schema upsert pipeline.

    Steps:
        1. Check if the Pinecone index exists — create it if not.
        2. If newly created, fetch schema metadata from MySQL.
        3. Embed and upsert all schema vectors into the new index.

    If the index already exists, this function exits early without
    making any changes to Pinecone or MySQL.
    """
    is_new = creating_index(INDEX_NAME)

    if not is_new:
        print(f"[INFO] '{INDEX_NAME}' already populated. Nothing to do.")
        return

    schemas = get_main_sql()

    if not schemas:
        print("[ERROR] No schemas returned from MySQL. Upsert skipped.")
        return

    schema_upsert(schemas=schemas)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    vector_creation()