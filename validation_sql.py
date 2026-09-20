"""
validation_sql.py
====================
SQL validation layer for the QuickQuery generation pipeline.
 
Responsibilities:
- Execute a generated SQL query against the active MySQL database
- Return a structured result dict indicating success or failure
- On failure, capture the exact database error message so the generation pipeline can feed it back into the regeneration prompt
 
Pipeline position:
    generation.py (generated SQL string)
        ↓
    [validation_sql]
        ↓
    result dict → generation.py (retry decision)
                → app.py (display to user)
 
Decoupling note:
    This module does NOT import streamlit. The active database name is received as a parameter from the caller (generation.py), which gets it from st.session_state in app.py. 
    This keeps the DB/validation layer independently usable outside Streamlit (e.g. scripts, tests, CLI tools).
"""
from mysql_connection import get_connection



# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validation_sql(query: str, user_query: str, database_name:str, attempt: int = 1) -> dict:
    """
    Execute a generated SQL query and return a structured result dict.
 
    Opens a fresh MySQL connection, selects the active database, executes the query, and 
    returns either a success dict with the result rows or a failure dict with the error message.
 
    The error message on failure is consumed by generation.py and
    injected into the regeneration prompt so the LLM can self-correct on the next attempt.
 
    Args:
        query:         The SQL query string to execute.
        user_query:    The original natural language question from the user — included in the result dict for traceability.
        database_name: The MySQL database to run the query against. Passed in by generation.py from the active session.
        attempt:       The current retry attempt number (1-indexed). Included in the result dict for logging/debugging.
 
    Returns:
        On success:
            {
                "User Query":      str,   # original natural language question
                "Generated Query": str,   # SQL that was executed
                "Result":          list,  # list of row tuples from fetchall()
                "Attempts":        int,   # attempt number that succeeded
                "Status":          "Success"
            }
 
        On failure:
            {
                "User Query":      str,   # original natural language question
                "Generated Query": str,   # SQL that was attempted
                "Error":           str,   # database error message for regeneration prompt
                "Attempts":        int,   # attempt number that failed
                "Status":          "Failed"
            }
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Select the active database before executing the query.
        # get_connection() connects to the server without a default
        # database, so USE must be called explicitly each time.
        cursor.execute(f"USE {database_name}")
        cursor.execute(query)
        result = cursor.fetchall()
        return {
            "User Query": user_query,
            "Generated Query": query,
            "Result": result,
            "Attempts": attempt,
            "Status": "Success"
        }
    except Exception as e:
        # Capture the full error string — this is passed directly into
        # the regeneration prompt so the LLM knows exactly what went wrong.
        return {
            "User Query": user_query,
            "Generated Query": query,
            "Error": str(e),
            "Attempts": attempt,
            "Status": "Failed"
        }
    finally:
        # Always close cursor and connection regardless of outcome
        cursor.close()
        connection.close()
