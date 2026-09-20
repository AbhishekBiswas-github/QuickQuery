"""
global_veriables.py
===================
Central configuration module for QuickQuery

Responsibilities
- Load and validate all required environment variables at startup
- Initialize the Pinecode client and index configuration
- Initialize the Langchain / Groq LLM
- Define shared contants used across the pipeline
(retrieval settings, few-shot examples, default state)

Every other module imports from here - This files must be imported before any pipeline code runs.
"""

from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import sys

# ----------------------------------------------------
# Environment Variables
# ----------------------------------------------------

# Load .env file into os.environ before any variable is read
load_dotenv()

# All keys that must be present for the application to start.
# If any are missing the process exists imidiately with a clear message
# instead of failing silently deeo inside the pipeline
REQUIRED_ENV_VARS = [
    "PINECONE_API_KEY",
    "EMBEDDING_MODEL",
    "HUGGINGFACE_API_KEY",
    "GROQ_API_KEY",
    "HOST",
    "DB_USER",
    "DATABASE_PASSWORD",
    "PORT"
]

def validate_env_vars() -> None:
    """
    Checks thet every required environment variable is set.
    Exists the process immediately with a description error if any are missing.
    Calls once at module load time.
    """
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        sys.exit(f"[ERROR] Missing environment variables: {" ".join(missing)}")

# Run validation on import so any misconfiguration is caught immediately
validate_env_vars()




# ----------------------------------------------------------
# Pinecone Configuration
# ----------------------------------------------------------

# Authentication Pinecone client - shared across vector_db_config and 
# content_extraction to avoid creating multiple clients.
PINECONE_CLIENT = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")
)

# Cerverless index deployment specification.
# Change cloud/region here if your Pinecone project used a different steup
CLOUD_SPECS = ServerlessSpec(
    cloud='aws',
    region='us-east-1'
)

# Name of the Pinecone Index that stores embedded schema chunks
INDEX_NAME = "index-quickquery"




# ----------------------------------------------------------
# Retribal (RAG) Settings
# ----------------------------------------------------------

# Number of condidate schema schunks to fetch Pinecone before reranking.
# Fetching more candidates gives the cross-encoder rerank a better pool to select from, improving final retrieval quality.
CANDIDATE_K = 5     

# Numver of top-ranked chunks to keep reranking and pass to the LLM.
# Lower = fewer token in the prompt; higher = more context for the LLM.
FINAL_TOP_K = 3     




# ----------------------------------------------------------
# Few Shot Examples
# ----------------------------------------------------------

# Example (user_query, SQL response) pairs injected into the generation.
# prompt to guide the LLM's output format and style.
# Add more examples here to improve accuracy and common query patterns.
FEW_SHOT_EXAMPLES = [
    {
        'user_query': "List names all products",
        'response': "select name from products;"
    },
    {
        "user_query": "Customer name with max order amount",
        'response': """SELECT * from customers
WHERE customer_id = (
            Select customer_id from orders
            GROUP BY customer_id
            ORDER BY SUM(total_amount) DESC
            LIMIT 1
);"""
    }
]



# ----------------------------------------------------------
# LLM 
# ----------------------------------------------------------


# Langchain-wrapper Groq used for SQL generation.
# temperature = 0 ensures dererministic, reproductible SQL output.
# Switch model name here to trade speed vs capabilites:
#   faster -> "llama-3.1-8b-instant"
#   smarter -> "llama-3.3-70b-versatile"
MODEL = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0
)


# ----------------------------------------------------------
# Application state defaults
# ----------------------------------------------------------

# Currently selected database name.
# Set to None to Startup; overwritten by the streamlit session at runtime
DATABASE_NAME = None

# Default message history for the chatbot session.
# Stored as a list of dicts with keys: "type" and "message"
# Matches the structure used in app.py's st.session_state.message_history
MESSAGE_HISTORY = []

