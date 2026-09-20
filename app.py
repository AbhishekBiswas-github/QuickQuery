"""
app.py
====================
Streamlit frontend for QuickQuery — a RAG-based natural language to SQL application.

Responsibilities:
- Render the full UI: sidebar configuration, tab navigation, chat interface,
  table browser, and query result display
- Manage all session state (connection status, selected database, message history,
  query counter)
- Pass user inputs and session context to the generation pipeline
- Display results returned by the pipeline

UI Structure:
    Sidebar
        ├── Database server configuration dialog
        ├── Database selector
        └── System info cards (tables, index, queries, model)

    Main Area
        ├── Header (title + subtitle)
        ├── Fixed tab bar (Tables | Chat | Query)
        └── Tab content (scrollable)
            ├── Tables  — browse any table in the connected database
            ├── Chat    — natural language → SQL chatbot
            └── Query   — execute and display the last generated query

Author: Abhishek Biswas
"""

import streamlit as st
from dotenv import set_key
from global_veriables import DATABASE_NAME, MESSAGE_HISTORY, INDEX_NAME, MODEL
from mysql_connection import (
    list_of_databases,
    get_tables,
    get_all_records,
    run_generated_query
)
from generation import generation

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="QuickQuery",
    page_icon="⚡"
)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
# All persistent values are declared here with defaults.
# The guard `if var not in st.session_state` ensures they are only set
# on the very first run — Streamlit reruns preserve existing values.

SESSION_VARIABLES = {
    "database_type":  None,     # DB engine selected in the config dialog
    "db_connection":  False,    # True once credentials are saved
    "database_name":  None,     # Active database chosen from the selector
    "active_tab":     "tables", # Which of the 3 main tabs is currently shown
    "message_history": [{       # Chatbot message list — dicts with type + message
        "type":    "system",
        "message": "Welcome to QuickQuery. I am your AI Assistant. How can I help you."
    }],
    "user_query":     None,     # Most recent raw user question
    "query_count":    0,        # Running total of SQL queries generated this session
    "generating":     False,    # Spinner flag — True while pipeline is running
}

for var, value in SESSION_VARIABLES.items():
    if var not in st.session_state:
        st.session_state[var] = value


# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
# Single <style> block injected once.  All colours use CSS variables so
# the dark theme can be adjusted from one place.

st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Design tokens ────────────────────────────────────────────────── */
:root {
    --bg-base:        #0a0d14;
    --bg-surface:     #111520;
    --bg-elevated:    #181d2e;
    --bg-card:        #1c2236;
    --accent:         #00d4ff;
    --accent-dim:     #0099bb;
    --accent-glow:    rgba(0, 212, 255, 0.15);
    --accent-2:       #7b5ea7;
    --success:        #00e5a0;
    --warning:        #ffb347;
    --danger:         #ff5c72;
    --text-primary:   #e8edf8;
    --text-secondary: #8a94b0;
    --text-muted:     #4a5270;
    --border:         #252d45;
    --border-bright:  #2e3a58;
    --radius-sm:      6px;
    --radius-md:      10px;
    --radius-lg:      16px;
    --font-mono:      'JetBrains Mono', monospace;
    --font-sans:      'Syne', sans-serif;
    --shadow-sm:      0 2px 8px rgba(0,0,0,0.4);
    --shadow-md:      0 4px 20px rgba(0,0,0,0.5);
    --shadow-glow:    0 0 20px rgba(0, 212, 255, 0.12);
}

/* ── Global resets ────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .main {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
}

/* Hide Streamlit default chrome — but keep the sidebar collapse button */
# MainMenu { visibility: hidden !important; }
footer    { visibility: hidden !important; }
/* Hide the top header bar content without touching the collapse toggle */
[data-testid="stHeader"]          { background: transparent !important; }
# [data-testid="stToolbar"]         { visibility: hidden !important; }
[data-testid="stDecoration"]      { display: none !important; }
[data-testid="stStatusWidget"]    { visibility: hidden !important; }
/* Ensure the sidebar collapse/expand arrow stays fully visible */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"]  { visibility: visible !important; opacity: 0 !important; }

/* ── Sidebar ──────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font-sans) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Typography ───────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}
p, li, span, label, div {
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
}

/* ── Streamlit buttons (global) ───────────────────────────────────── */
[data-testid="baseButton-primary"],
[data-testid="baseButton-secondary"] {
    font-family: var(--font-sans) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.03em !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, var(--accent-dim), var(--accent)) !important;
    color: #000 !important;
    border: none !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.25) !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,212,255,0.4) !important;
}
[data-testid="baseButton-secondary"] {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-bright) !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-glow) !important;
}

/* ── Sidebar button hover ─────────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="baseButton-primary"]:hover {
    transform: translateX(3px) translateY(-1px) !important;
}

/* ── Inputs ───────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* ── Selectbox dropdown ───────────────────────────────────────────── */
[data-baseweb="popover"] ul {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-bright) !important;
}
[data-baseweb="popover"] li {
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    font-size: 13px !important;
}
[data-baseweb="popover"] li:hover {
    background: var(--accent-glow) !important;
}

/* ── Alerts ───────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-sans) !important;
    font-size: 13px !important;
}

/* ── Code blocks (SQL output) ─────────────────────────────────────── */
[data-testid="stCode"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-mono) !important;
    font-size: 13px !important;
}
[data-testid="stCode"] code {
    color: var(--accent) !important;
    font-family: var(--font-mono) !important;
}

/* ── Chat messages ────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 10px !important;
    padding: 12px 16px !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* ── Table styling ────────────────────────────────────────────────── */
[data-testid="stTable"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-family: var(--font-sans) !important;
    font-size: 13px !important;
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}
[data-testid="stTable"] th {
    background: var(--bg-base) !important;
    color: var(--accent) !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 12px 16px !important;
    border-bottom: 2px solid var(--accent-dim) !important;
    white-space: nowrap !important;
}
[data-testid="stTable"] td {
    padding: 10px 16px !important;
    border-bottom: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-size: 13px !important;
}
[data-testid="stTable"] tr:hover td {
    background: var(--accent-glow) !important;
}
[data-testid="stTable"] tr:last-child td {
    border-bottom: none !important;
}

/* ── Divider ──────────────────────────────────────────────────────── */
hr {
    border-color: var(--border) !important;
    margin: 16px 0 !important;
}

/* ── Spinner ──────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--accent) !important;
}

/* ── Sticky tab bar ───────────────────────────────────────────────── */
.tab-bar-sticky {
    position: sticky;
    top: 0;
    z-index: 999;
    background: var(--bg-base);
    padding: 12px 0 0 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0;
}

/* Active tab button override */
.tab-active button {
    background: var(--accent-glow) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
}
.tab-active button:hover {
    transform: none !important;
}

/* ── Info cards ───────────────────────────────────────────────────── */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border-bright);
    border-radius: var(--radius-md);
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.info-card:hover {
    border-color: var(--accent);
    box-shadow: var(--shadow-glow);
}
.info-card-icon {
    font-size: 18px;
    min-width: 24px;
    text-align: center;
}
.info-card-body { flex: 1; }
.info-card-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 2px;
}
.info-card-value {
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
}

/* ── Chat alignment ───────────────────────────────────────────────── */
.user-message-wrap {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
}
.user-message-bubble {
    background: linear-gradient(135deg, #1a2a3a, #0f2030);
    border: 1px solid var(--accent-dim);
    border-radius: var(--radius-md) var(--radius-md) var(--radius-sm) var(--radius-md);
    padding: 10px 16px;
    max-width: 70%;
    font-size: 14px;
    color: var(--text-primary);
    font-family: var(--font-sans);
}
.assistant-message-wrap {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
}
.assistant-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 6px;
    font-family: var(--font-mono);
}
.system-message-wrap {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
}
.system-bubble {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 8px 14px;
    font-size: 13px;
    color: var(--text-secondary);
    font-style: italic;
    font-family: var(--font-sans);
}

/* ── Section subheaders ───────────────────────────────────────────── */
.section-header {
    font-family: var(--font-sans);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 20px 0 12px 0;
    padding-left: 2px;
    border-left: 3px solid var(--accent);
    padding-left: 10px;
}

/* ── Table section header ─────────────────────────────────────────── */
.table-section-title {
    font-family: var(--font-sans);
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
}
.table-section-sub {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 20px;
}

/* ── Query result header ──────────────────────────────────────────── */
.query-result-header {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}
.row-badge {
    display: inline-block;
    background: var(--accent-glow);
    border: 1px solid var(--accent-dim);
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-left: 8px;
}

/* ── Footer ───────────────────────────────────────────────────────── */
.app-footer {
    margin-top: 48px;
    padding: 20px 0 12px 0;
    border-top: 1px solid var(--border);
    text-align: center;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.05em;
}
.app-footer span {
    color: var(--accent);
}
.app-footer .heart { color: #ff5c72; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper: sidebar info card
# ---------------------------------------------------------------------------

def info_card(icon: str, label: str, value: str) -> None:
    """
    Render a single styled info card in the sidebar.

    Cards display system metadata (table count, index name, etc.)
    in a consistent icon + label + value layout.

    Args:
        icon:  Emoji or symbol shown on the left.
        label: Short uppercase descriptor (e.g. "Tables").
        value: The data value to display (e.g. "8").
    """
    st.markdown(f"""
    <div class="info-card">
        <div class="info-card-icon">{icon}</div>
        <div class="info-card-body">
            <div class="info-card-label">{label}</div>
            <div class="info-card-value">{value}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Database configuration dialog
# ---------------------------------------------------------------------------

@st.dialog("Database Configuration")
def display_dialog() -> None:
    """
    Modal dialog for entering and saving database connection credentials.

    Writes all credentials to the .env file via python-dotenv's set_key()
    so they persist across sessions. Sets st.session_state.db_connection = True
    on submission and triggers a rerun to refresh the sidebar state.

    Fields:
        - Database type (MySQL / PostgreSQL / Oracle)
        - Host, User, Password, Port
    """
    with st.form("db_config_form"):
        db_type = st.selectbox(
            "Database Type",
            ["MySQL", "PostgreSQL", "Oracle"]
        )
        db_host = st.text_input(
            "Host",
            placeholder="e.g. localhost or 127.0.0.1",
            value="localhost"
        )
        db_user = st.text_input(
            "Username",
            placeholder="Database username"
        )
        db_pass = st.text_input(
            "Password",
            placeholder="Database password",
            type="password"
        )
        db_port = st.text_input(
            "Port",
            placeholder="e.g. 3306",
            value="3306"
        )
        submitted = st.form_submit_button("Connect", type="primary")

        if submitted:
            # Persist credentials to .env
            set_key(".env", "HOST",              db_host, quote_mode="never")
            set_key(".env", "DB_USER",           db_user, quote_mode="never")
            set_key(".env", "DATABASE_PASSWORD", db_pass, quote_mode="never")
            set_key(".env", "PORT",              db_port, quote_mode="never")
            set_key(".env", "TYPE",              db_type, quote_mode="never")
            st.session_state.database_type = db_type
            st.session_state.db_connection = True
            st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    # ── Logo / branding ─────────────────────────────────────────────
    st.markdown("""
    <div style="padding: 8px 0 16px 0;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:22px;
                    font-weight:700; color:#00d4ff; letter-spacing:-0.02em;">
            ⚡ QuickQuery
        </div>
        <div style="font-size:11px; color:#4a5270; margin-top:2px;
                    font-family:'Syne',sans-serif; letter-spacing:0.05em;">
            NL → SQL · RAG Pipeline
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── DB config button ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Connection</div>',
                unsafe_allow_html=True)

    if st.button("⚙️  Configure Database", type="primary", use_container_width=True):
        display_dialog()

    # ── DB selector (only shown after connection is established) ─────
    if st.session_state.db_connection:
        st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)

        selected_db = st.selectbox(
            "Available Databases",
            list_of_databases()
        )

        if st.button("✅  Use This Database", use_container_width=True, type="primary"):
            st.session_state.database_name = selected_db
            # Reset query count when database changes
            st.session_state.query_count = 0
            st.rerun()

        # Connection status badge
        if st.session_state.database_name:
            st.success(f"Connected → {st.session_state.database_name}")
        else:
            st.info("No database selected yet")
    else:
        st.error("No active connection")

    st.divider()

    # ── System info cards ────────────────────────────────────────────
    # Only shown once a database is connected so we can count tables
    st.markdown('<div class="section-header">System Info</div>',
                unsafe_allow_html=True)

    if st.session_state.database_name:
        # Count tables in the active database
        try:
            table_count = len(get_tables(st.session_state.database_name))
        except Exception:
            table_count = "—"

        info_card("🗄️",  "Database",      st.session_state.database_name)
        info_card("📋",  "Total Tables",  str(table_count))
        info_card("🔍",  "Pinecone Index", INDEX_NAME)
        info_card("💬",  "Queries Made",  str(st.session_state.query_count))
        info_card("🤖",  "LLM Model",     MODEL.model_name)
        info_card("⚙️",  "DB Type",       st.session_state.database_type or "MySQL")
    else:
        info_card("🔍",  "Pinecone Index", INDEX_NAME)
        info_card("🤖",  "LLM Model",     MODEL.model_name)
        st.markdown("""
        <div style="font-size:12px; color:#4a5270; text-align:center;
                    padding:16px 0; font-family:'Syne',sans-serif;">
            Connect a database to see<br>full system details
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main area — header
# ---------------------------------------------------------------------------

st.markdown("""
<div style="padding: 24px 0 8px 0;">
    <div style="font-family:'Syne',sans-serif; font-size:32px; font-weight:800;
                color:#e8edf8; letter-spacing:-0.03em; line-height:1.1;">
        QuickQuery
        <span style="color:#00d4ff;">.</span>
    </div>
    <div style="font-size:14px; color:#8a94b0; margin-top:6px;
                font-family:'Syne',sans-serif;">
        Ask questions in plain English — get SQL instantly
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tab bar + content (only shown once a database is selected)
# ---------------------------------------------------------------------------

if not st.session_state.database_name:
    # Prompt to connect when no database is active
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px; color:#4a5270;">
        <div style="font-size:48px; margin-bottom:16px;">🔌</div>
        <div style="font-family:'Syne',sans-serif; font-size:18px;
                    font-weight:600; color:#8a94b0; margin-bottom:8px;">
            No database connected
        </div>
        <div style="font-size:13px;">
            Use the sidebar to configure and select a database to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    DATABASE_NAME = st.session_state.database_name

    # ── Sticky tab bar ───────────────────────────────────────────────
    # Rendered as a fixed sticky bar so it stays visible while the
    # content below scrolls. Active tab gets an accent border + glow.

    st.markdown('<div class="tab-bar-sticky">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        is_tables = st.session_state.active_tab == "tables"
        wrap_cls = "tab-active" if is_tables else ""
        st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
        if st.button("📋  Tables", use_container_width=True):
            st.session_state.active_tab = "tables"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        is_chat = st.session_state.active_tab == "chat"
        wrap_cls = "tab-active" if is_chat else ""
        st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
        if st.button("🤖  Chat", use_container_width=True):
            st.session_state.active_tab = "chat"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        is_query = st.session_state.active_tab == "query"
        wrap_cls = "tab-active" if is_query else ""
        st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
        if st.button("🖥️  Results", use_container_width=True):
            st.session_state.active_tab = "query"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close tab-bar-sticky

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # ====================================================================
    # TAB: Tables
    # ====================================================================
    if st.session_state.active_tab == "tables":
        """
        Table Browser tab.

        Renders a dropdown to select any table from the connected database
        and displays up to 5 preview rows in a styled table.
        """
        st.markdown(f"""
        <div class="table-section-title">Table Browser</div>
        <div class="table-section-sub">
            Browsing <span style="color:#00d4ff; font-weight:600;">{DATABASE_NAME}</span>
             — select a table to preview its first 5 rows
        </div>
        """, unsafe_allow_html=True)

        tables = get_tables(database_name=DATABASE_NAME)

        table_name = st.selectbox(
            "Select Table",
            tables,
            help="Choose a table from the connected database to preview"
        )

        if table_name:
            st.markdown(f"""
            <div class="query-result-header">
                Table: <span style="color:#00d4ff;">{table_name}</span>
                <span class="row-badge">PREVIEW · 5 ROWS</span>
            </div>
            """, unsafe_allow_html=True)
            st.table(get_all_records(table_name, DATABASE_NAME))

    # ====================================================================
    # TAB: Chat
    # ====================================================================
    elif st.session_state.active_tab == "chat":
        """
        Chat tab — natural language to SQL.

        Renders the conversation history with:
            - System / assistant messages aligned left
            - User messages aligned right as bubbles
        Appends a spinner while the pipeline is running, then replaces it
        with the generated SQL code block on completion.
        """

        # ── Conversation history ──────────────────────────────────────
        for message in st.session_state.message_history:
            msg_type = message["type"]
            msg_text = message["message"]

            if msg_type == "user":
                # User messages → right-aligned bubble
                st.markdown(f"""
                <div class="user-message-wrap">
                    <div class="user-message-bubble">{msg_text}</div>
                </div>
                """, unsafe_allow_html=True)

            elif msg_type == "assistant":
                # Assistant SQL → left-aligned with label + code block
                st.markdown(
                    '<div class="assistant-message-wrap">'
                    '<div style="max-width:90%; width:100%;">'
                    '<div class="assistant-label">⚡ QuickQuery</div>',
                    unsafe_allow_html=True
                )
                st.code(msg_text, language="sql")
                st.markdown("</div></div>", unsafe_allow_html=True)

            else:
                # System messages (welcome, generating...) → muted left bubble
                if msg_text != "Generating......":
                    st.markdown(f"""
                    <div class="system-message-wrap">
                        <div class="system-bubble">🤖 {msg_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Generation spinner ────────────────────────────────────────
        # Shown after user submits a query, before the response arrives.
        if st.session_state.generating:
            with st.spinner("⚡ Generating SQL query..."):
                response = generation(
                    user_query=st.session_state.user_query,
                    database_name=st.session_state.database_name,
                    message_history=st.session_state.message_history,
                    dialect=st.session_state.database_type or "MySQL"
                )

            # Remove the "Generating......" placeholder from history
            st.session_state.message_history = [
                m for m in st.session_state.message_history
                if m["message"] != "Generating......"
            ]

            # Append the generated SQL as an assistant message
            st.session_state.message_history.append({
                "type":    "assistant",
                "message": response["Generated Query"]
            })

            # Increment session query counter
            st.session_state.query_count += 1

            # Clear spinner flag and rerun to display the response
            st.session_state.generating = False
            st.rerun()

        # ── Chat input ────────────────────────────────────────────────
        user_query = st.chat_input("Ask anything about your data…")
        if user_query:
            st.session_state.user_query = user_query

            # Add user message to history
            st.session_state.message_history.append({
                "type":    "user",
                "message": user_query
            })

            # Add generating placeholder to history
            st.session_state.message_history.append({
                "type":    "system",
                "message": "Generating......"
            })

            # Set flag so the spinner block runs on next rerun
            st.session_state.generating = True
            st.rerun()

    # ====================================================================
    # TAB: Query Results
    # ====================================================================
    elif st.session_state.active_tab == "query":
        """
        Query Results tab.

        Executes the last generated SQL query against the connected database
        and displays the result in the same styled table as the Table Browser.
        Shows all rows if ≤10, otherwise caps at 10 with a row count notice.
        """
        last_message = st.session_state.message_history[-1]

        if last_message["type"] != "assistant":
            st.markdown("""
            <div style="text-align:center; padding: 60px 20px; color:#4a5270;">
                <div style="font-size:40px; margin-bottom:12px;">🖥️</div>
                <div style="font-family:'Syne',sans-serif; font-size:16px;
                            font-weight:600; color:#8a94b0; margin-bottom:8px;">
                    No query generated yet
                </div>
                <div style="font-size:13px;">
                    Switch to the <span style="color:#00d4ff;">🤖 Chat</span> tab
                    and ask a question to generate a SQL query first.
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            generated_sql = last_message["message"]

            # Show the SQL that will be executed
            st.markdown('<div class="section-header">Executing Query</div>',
                        unsafe_allow_html=True)
            st.code(generated_sql, language="sql")

            # Execute and display results
            resulted_table = run_generated_query(
                generated_query=generated_sql,
                database_name=st.session_state.database_name
            )
            rows, cols = resulted_table.shape
            display_rows = min(rows, 10)

            st.markdown(f"""
            <div class="query-result-header" style="margin-top:20px;">
                Results
                <span class="row-badge">{display_rows} / {rows} ROWS</span>
            </div>
            """, unsafe_allow_html=True)

            if rows > 10:
                st.info(
                    f"Showing first 10 rows of {rows} total. "
                    "Export the full result set directly from your database client."
                )
                st.table(resulted_table.head(10))
            else:
                st.table(resulted_table)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("""
<div class="app-footer">
    <span>© 2025 QuickQuery</span>
    &nbsp;·&nbsp;
    Built with <span class="heart">♥</span> by
    <span>Abhishek Biswas</span>
    &nbsp;·&nbsp;
    Powered by LangChain · Groq · Pinecone
</div>
""", unsafe_allow_html=True)