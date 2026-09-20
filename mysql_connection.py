"""
mysql_connection.py
===================
Database access layer for QuickQuery.

Responsibilities
- Open and Close MySQL connections.
- Fetch database/table metadata for the sidebar UI
- Fetch full schema details (columns, FK relationships, row counts)
  used by vector_db_config.py to build Pinecode embeddings.
- Execute generated SQL queries and return results as DataFrames.

All functions open as fresh connection, perform their work and close the connection in a finally block - no persistant connection is held.

Note: streamlit is NOT imported here. Functions that need the active database name recieve it as a parameter, keeping this module decoupled from the UI layer.
"""
from dotenv import load_dotenv
import os
import mysql.connector
from global_veriables import DATABASE_NAME
from column_description import COLUMN_DESCRIPTIONS
import pandas as pd

# load_dotenv() is already called in global_veriable.py which is imported above, but calling it again here is safe and 
# makes this module independently usable in non Streamlit contexts (e.g. scripts)
load_dotenv()

# ----------------------------------------------------------
# Connections
# ----------------------------------------------------------
def get_connection() -> mysql.connector.MySQLConnection:
    """
    Create and return a new MySQL connection (no database selected).

    Credentials are read from environment variables set in .env:
        HOST, DB_USER, DATABASE_PASSWORD, PORT
    
    Returns:
        mysql.connector.MySQLConnection: An open connection to the server.
    
    Raises:
        mysql.connection.Error: If the connection cannot be established.
    """
    return mysql.connector.connect(
        host= os.environ.get("HOST"),
        user= os.environ.get("DB_USER"),
        password = os.environ.get("DATABASE_PASSWORD"),
        port = int(os.environ.get("PORT"))
    )




# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
def key_type_describe(key_type:str) -> str:
    """
    Convert a MySQL DESCRIBE key-type code into a human-readable label.
 
    MySQL DESCRIBE returns single-letter codes in the 'Key' column:
        PRI → PRIMARY KEY
        UNI → UNIQUE KEY
        MUL → MULTIPLE KEY (non-unique index)
        ''  → No key constraint
 
    Args:
        key_type: The raw key code string returned by DESCRIBE.
 
    Returns:
        A descriptive string label, or "None" if no key applies.
    """
    mapping = {
        "PRI": "PRIMARY KEY",
        "UNI" : "UNIQUE KEY",
        "MUL" : "MULTIPLE KEY"
    }
    return mapping.get(key_type, "None")


# ---------------------------------------------------------------------------
# Server / database discovery
# ---------------------------------------------------------------------------
def list_of_databases() -> list[str]:
    """
    Return a list of all database names available on the MySQL server.
 
    Used by the Streamlit sidebar to populate the database selector.
 
    Returns:
        list[str]: Database names (e.g. ['ecommerce_db', 'sys', ...]).
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW DATABASES")
        return [db for row in cursor.fetchall() for db in row]
    finally:
        cursor.close()
        connection.close()



def check_connection(database_name:str) -> str:
    """
    Verify that a specific database exists on the connected MySQL server.
 
    Used by get_main_sql() before attempting schema extraction.
 
    Args:
        database_name: The database name to look for.
 
    Returns:
        "Connected"  — if the database exists on the server.
        "Database <name> Absent" — if it does not exist.
        "Connection Error: <detail>" — if the server itself is unreachable.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"show databases")
        databases = [database for row in cursor.fetchall() for database in row]
        return "Connected" if database_name in databases else f"Database {database_name} Absent"
    except Exception as e:
        return f"Connection Error: {e}"
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Table data
# ---------------------------------------------------------------------------
def get_tables(database_name:str) -> list[str]:
    """
    Return all table names in the specified database.
 
    Used by the Streamlit UI to populate the table selector,
    and by get_main_sql() to drive schema extraction.
 
    Args:
        database_name: The target database name.
 
    Returns:
        list[str]: Table names (e.g. ['customers', 'orders', ...]).
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"Show tables from {database_name}")
        return [table for row in cursor.fetchall() for table in row]
    finally:
        cursor.close()
        connection.close()


def get_all_records(table_name:str, database_name:str):
    """
    Fetch the first 5 rows of a table for preview in the Streamlit UI.
 
    Args:
        table_name:    The table to preview.
        database_name: The database that contains the table.
 
    Returns:
        pd.DataFrame: Up to 5 rows with column names as headers.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"USE {database_name}")
        cursor.execute(f"""SELECT * FROM {table_name}
LIMIT 5;""")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Schema extraction (used by vector_db_config to build Pinecone index)
# ---------------------------------------------------------------------------
# get complete schema of all tables
def get_schemas(database_name:str, tables:list[str]) -> list[dict]:
    """
    Extract full schema metadata for each table in the database.
 
    For every table this collects:
        - column_details : list of enriched column description strings
          (name, semantic description from COLUMN_DESCRIPTIONS, data type,
          nullability, key type, default value, extra constraints)
        - total_records  : row count as a human-readable string
        - foreign_key_details : FK relationships or a "no FK" message
 
    The returned structure is consumed by vector_db_config.py to build
    the text that gets embedded and upserted into Pinecone.
 
    Args:
        database_name: The database to extract schema from.
        tables:        List of table names to process.
 
    Returns:
        list[dict]: One dict per table with keys:
            "table_name", "column_details", "total_records",
            "foreign_key_details"
    """
    connection = get_connection()
    cursor = connection.cursor()
    schemas = []

    try: 
        cursor.execute(f"Use {database_name}")
    
        for table in tables:
            table_schema = {
                'table_name': table,
                'column_details': [],
                'total_records': 0,
                'foreign_key_details': []
            }

            # --- Column details ---
            # DESCRIBE returns: Field, Type, Null, Key, Default, Extra
            cursor.execute(f"DESCRIBE {table}")
            for col in cursor.fetchall():
                col_desc = COLUMN_DESCRIPTIONS.get(f"{table}.{col[0]}", "No Description available")
                table_schema['column_details'].append(
                    f"Column: {col[0]}, Description: {col_desc}, Data Type: {col[1]}, Null Constraint: {col[2]}, Key Type: {key_type_describe(col[3])}, Default Value: {col[4]}, Extra Contraints: {col[5]}"
                )

            # --- Row count ---
            cursor.execute(f"select COUNT(*) FROM {table}")
            table_schema["total_records"] =  f"There are {cursor.fetchall()[0][0]} records."

            # --- Foreign key relationships ---
            # Queries INFORMATION_SCHEMA to find which columns reference
            # other tables, giving the LLM JOIN context.
            cursor.execute(f"""
                           SELECT 
                                TABLE_NAME, 
                                COLUMN_NAME, 
                                CONSTRAINT_NAME, 
                                REFERENCED_TABLE_NAME, 
                                REFERENCED_COLUMN_NAME 
                            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                            WHERE REFERENCED_TABLE_NAME IS NOT NULL 
                            AND TABLE_NAME = "{table}";""")
            
            foreign_key_list = cursor.fetchall()
            if foreign_key_list:
                for col in foreign_key_list:
                    table_schema["foreign_key_details"].append(f"{col[0]}'s table ({col[1]}) column is referencing {col[3]}'s table ({col[4]}) column")
            else:
                table_schema["foreign_key_details"] = "No Relationship exists for this table"

            schemas.append(table_schema)

    finally:
        cursor.close()
        connection.close()
    
    return schemas 




# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------
def run_generated_query(generated_query:str, database_name:str) -> pd.DataFrame:
    """
    Execute a generated SQL SELECT query and return the results as a DataFrame.
 
    Called by app.py's "Sample Display" tab to preview query results.
 
    DECOUPLING FIX: Previously read st.session_state.database_name directly,
    tightly coupling this module to Streamlit. Now receives database_name
    as a parameter — the caller (app.py) passes st.session_state.database_name.
 
    Args:
        generated_query: A validated SQL SELECT query string.
        database_name:   The database to run the query against.
 
    Returns:
        pd.DataFrame: Query results with column names as headers.
 
    Raises:
        mysql.connector.Error: If the query fails at the database level.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(f"USE {database_name}")
        cursor.execute(generated_query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------
def get_main_sql(database_name:str = DATABASE_NAME) -> list[dict] | None:
    """
    Top-level entry point for schema extraction.
 
    Verifies the database exists, fetches all table names, then extracts
    full schema metadata for each table.
 
    Called by vector_db_config.py during the one-time Pinecone index
    build to get the schema data that will be embedded and upserted.
 
    Args:
        database_name: The database to extract. Defaults to the value
                       of DATABASE_NAME from global_veriables.py,
                       which is None at startup and set at runtime.
 
    Returns:
        list[dict]: Schema metadata for all tables, or None on failure.
    """
    status = check_connection(database_name)
    if status.lower() == 'connected':
        tables = get_tables(database_name)
        return get_schemas(database_name, tables)
    else:
        print(f"[ERROR] {status}")
        return None





