"""
generation.py
====================
Top-level SQL generation pipeline for QuickQuery.

Responsibilities:
- Convert the raw session message history into LangChain message objects
  for conversation context (sliding window)
- Retrieve relevant schema chunks from Pinecone via content_extraction()
- Build and invoke the appropriate LangChain prompt chain
- Strip markdown fencing from the LLM response
- Validate the generated SQL via validation_sql()
- Retry up to MAX_ATTEMPTS times using the error-correction prompt
  if validation fails

Pipeline position:
    app.py (user query + message history + database_name + dialect)
        ↓
    [generation]
        ├── content_extraction()        → schema chunks (once, before retry loop)
        ├── build_history_message()     → LangChain message history
        ├── build_prompt()              → attempt 1 chain
        ├── build_regeneration_prompt() → attempt 2+ chain
        └── validation_sql()            → execute and validate each attempt

Return value:
    dict with keys:
        "User Query"      — original natural language question
        "Generated Query" — final SQL string (success or last attempt)
        "Result"          — query result rows (on success only)
        "Attempts"        — number of attempts made
        "Status"          — "Success" or "Failed"
        "Error"           — error message (on failure only)
"""

import re
from langchain_core.messages import HumanMessage, AIMessage
from global_veriables import MODEL, FEW_SHOT_EXAMPLES, CANDIDATE_K, FINAL_TOP_K
from prompt_creation import build_prompt, build_regeneration_prompt
from content_extraction import content_extraction
from validation_sql import validation_sql


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Maximum number of generation + validation attempts before giving up.
# On each failed attempt the error is fed back into the regeneration
# prompt so the LLM can self-correct. 3 is a good balance between
# thoroughness and latency.
MAX_ATTEMPTS = 3

# Number of prior conversation turns to include as context.
# Each "turn" is one user message + one assistant (SQL) response.
# Multiplied by 2 when slicing the flat message list (user + assistant = 2 items).
# Increase for longer conversation memory; decrease to save tokens.
MAX_CONTEXT_WINDOW = 5


# ---------------------------------------------------------------------------
# History builder
# ---------------------------------------------------------------------------

def build_history_message(message_history: list[dict]) -> list:
    """
    Convert the Streamlit session message history into a list of
    LangChain message objects suitable for MessagesPlaceholder injection.

    Filters out:
        - System messages (welcome text, status messages)
        - "Generating......" placeholder messages added while the
          pipeline is running (these should not appear as turns)

    Applies a sliding window of the last MAX_CONTEXT_WINDOW turns
    (MAX_CONTEXT_WINDOW * 2 items, since each turn has a user
    message and an assistant message).

    Args:
        message_history: List of session message dicts, each with keys:
                         "type"    — "user", "assistant", or "system"
                         "message" — the message content string

    Returns:
        list: LangChain HumanMessage and AIMessage objects in
              chronological order, ready for MessagesPlaceholder.
              Returns [] if no eligible messages exist.
    """
    # Keep only user/assistant turns; drop system messages and
    # the "Generating......" status placeholder added by app.py
    clean = [
        m for m in message_history
        if m["type"] in ("user", "assistant")
        and m["message"] != "Generating......"
    ]

    # Slide the window: keep only the most recent N complete turns
    windowed = clean[-(MAX_CONTEXT_WINDOW * 2):]

    lc_messages = []
    for m in windowed:
        if m["type"] == "user":
            lc_messages.append(HumanMessage(content=m["message"]))
        elif m["type"] == "assistant":
            lc_messages.append(AIMessage(content=m["message"]))

    return lc_messages


# ---------------------------------------------------------------------------
# Main generation pipeline
# ---------------------------------------------------------------------------

def generation(
    user_query: str,
    database_name: str,
    message_history: list = None,
    dialect: str = "MySQL"
) -> dict:
    """
    Generate a validated SQL query for the user's natural language question.

    Attempt 1 — Initial generation:
        Uses build_prompt() with few-shot examples, retrieved schema,
        conversation history, and the SQL dialect. The history gives the
        LLM context for follow-up questions that reference prior queries.

    Attempt 2+ — Error correction:
        Uses build_regeneration_prompt() with the failed SQL and its
        error message. History is excluded here to keep the correction
        prompt focused on the specific syntax or logic error.

    Schema retrieval:
        content_extraction() is called ONCE before the retry loop.
        The same schema chunks are reused across all attempts —
        re-fetching on every attempt would be wasteful since the
        query intent hasn't changed between retries.

    Args:
        user_query:      The natural language question from the user.
        database_name:   The active MySQL database name. Passed through
                         to validation_sql() to keep the DB layer
                         decoupled from Streamlit's session state.
        message_history: The full session message history list from
                         st.session_state.message_history in app.py.
                         Pass [] or None on the first ever message.
        dialect:         SQL dialect string injected into the prompt
                         (e.g. "MySQL", "PostgreSQL"). Defaults to "MySQL".
                         Sourced from st.session_state.database_type in app.py.

    Returns:
        dict: The result from validation_sql() for the successful attempt,
              or the last failed result if all attempts are exhausted.
              Keys: "User Query", "Generated Query", "Result",
                    "Attempts", "Status", "Error" (on failure)
    """
    print(f"[INFO] Generating SQL for: '{user_query}'")

    # Fetch schema chunks ONCE — reused across all retry attempts.
    # Re-fetching inside the loop was a previous bug; the query intent
    # does not change between retries so the schema is stable.
    schema = content_extraction(user_query, CANDIDATE_K, FINAL_TOP_K)

    # Build LangChain message history ONCE for the initial prompt.
    # Only used on attempt 1 — regeneration prompt does not use history.
    history = build_history_message(message_history or [])

    previous_result = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"[INFO] Attempt {attempt}/{MAX_ATTEMPTS}")

        if attempt == 1:
            # --- Initial generation ---
            # Includes few-shot examples and conversation history so the
            # LLM can resolve follow-up references like "same query but
            # for last month" or "now sort by total descending".
            chain = build_prompt(FEW_SHOT_EXAMPLES) | MODEL

            response = chain.invoke({
                "dialect":       dialect,
                "schema":        schema,
                "user_question": user_query,
                "history":       history
            })

        else:
            # --- Error correction ---
            # Feeds the broken SQL and its error back to the LLM so it
            # can produce a corrected version. History excluded here to
            # keep the prompt tightly focused on the fix.
            chain = build_regeneration_prompt() | MODEL

            response = chain.invoke({
                "schema":     schema,
                "sql_query":  previous_result["Generated Query"],
                "error":      previous_result["Error"],
                "user_query": user_query
            })

        # Strip markdown code fences the LLM sometimes wraps output in
        # e.g. ```sql SELECT ... ``` → SELECT ...
        sql_query = re.sub(r"```sql|```", "", response.content).strip()

        # Pass database_name through to validation so that layer stays
        # decoupled from Streamlit's session state
        result = validation_sql(
            query=sql_query,
            user_query=user_query,
            database_name=database_name,
            attempt=attempt
        )

        if result["Status"] == "Success":
            print(f"[INFO] Query succeeded on attempt {attempt}.")
            return result

        print(f"[WARN] Attempt {attempt} failed: {result.get('Error')}")
        previous_result = result

    print("[ERROR] All attempts exhausted. Returning last failed result.")
    return previous_result


# ---------------------------------------------------------------------------
# Manual test entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run a quick end-to-end test without starting Streamlit.
    # Requires a live MySQL connection and a populated Pinecone index.
    # Set test_db to your local database name before running.
    test_query = "Which customer spent the most money?"
    test_db    = "ecommerce_db"

    result = generation(
        user_query=test_query,
        database_name=test_db,
        dialect="MySQL"
    )

    if result["Status"] == "Failed":
        print(f"\n[FAILED] Generated query:\n{result['Generated Query']}")
        print(f"[ERROR]  {result['Error']}")
    else:
        print(f"\n[SUCCESS] Generated query:\n{result['Generated Query']}")