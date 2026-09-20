
"""
prompt_creation.py
====================
Prompt builder functions for the QuickQuery SQL generation pipeline.
 
Responsibilities:
- Build the initial generation prompt with few-shot examples,
  database schema context, and conversation history
- Build the regeneration (error-correction) prompt when a generated
  SQL query fails validation
 
Pipeline position:
    content_extraction → schema chunks
                              ↓
                    [prompt_creation]  ←  few_shot_examples (global_veriables.py)
                              ↓            history (generation.py)
                          generation
 
Two prompt types:
    build_prompt()              — used on attempt 1; includes few-shot
                                  examples and conversation history so
                                  the LLM understands prior context.
    build_regeneration_prompt() — used on attempts 2+; focused purely
                                  on fixing the error in the previous
                                  SQL; history intentionally excluded
                                  to keep the correction prompt tight.
 
LangChain invoke keys:
    build_prompt()              → dialect, schema, user_question, history
    build_regeneration_prompt() → schema, sql_query, error, user_query
"""

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder
)


# ---------------------------------------------------------------------------
# Initial generation prompt
# ---------------------------------------------------------------------------
def build_prompt(few_shot_examples: list[dict]):
    """
    Build the initial SQL generation prompt.
 
    Prompt structure (in message order):
        1. System message  — role definition, rules, dialect, schema context
        2. Few-shot block  — example (user query → SQL) pairs from FEW_SHOT_EXAMPLES
        3. History block   — prior conversation turns (sliding window of last N turns)
                             injected via MessagesPlaceholder; empty list on first query
        4. Human message   — the current user question
 
    The history block lets the LLM resolve references to prior queries,
    e.g. "same query but filter by last month" or "now group that by category".
 
    Args:
        few_shot_examples: List of {"user_query": ..., "response": ...} dicts
                           from global_veriables.py FEW_SHOT_EXAMPLES.
 
    Returns:
        ChatPromptTemplate ready to pipe into the LLM:
            chain = build_prompt(FEW_SHOT_EXAMPLES) | MODEL
            response = chain.invoke({
                "dialect":       "MySQL",
                "schema":        schema_chunks,
                "user_question": user_query,
                "history":       lc_message_history   # list of HumanMessage/AIMessage
            })
    """

    # Defines how each few-shot example is rendered as a (human, ai) turn
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{user_query}"),
            ("ai", "{response}")
        ]
    )

    # Wraps the examples list into a reusable few-shot block
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        examples=few_shot_examples,
        example_prompt=example_prompt
    )

    # Full prompt: system → few-shot → history → current question
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are an expert SQL query generator.
Rules:
1. Generate only a valid SQL query — no explanation, no preamble.
2. Use only the tables and columns present in the provided schema.
3. SQL dialect: {dialect}
4. Return optimized SQL only.
5. If the user refers to a previous query or result (e.g. "same query \
but for last month", "now group that by category"), use the conversation \
history to understand the full context before generating the query.
 
Database Schema:
{schema}
"""),
            few_shot_prompt,
            MessagesPlaceholder(
                variable_name="history",
                optional=True
            ),
            ("human", "{user_question}")
        ]
    )

    return final_prompt



# ---------------------------------------------------------------------------
# Regeneration (error-correction) prompt
# ---------------------------------------------------------------------------
def build_regeneration_prompt():
    """
    Build the SQL error-correction prompt used on retry attempts.
 
    Called by generation.py on attempt 2 and beyond when the previously
    generated SQL query failed validation. The prompt provides the LLM
    with the original schema, the broken query, and the exact error
    message so it can produce a corrected version.
 
    History is intentionally excluded here — this is a focused
    correction loop, not a conversational turn. Adding history would
    only increase token usage and risk distracting the model from
    the specific syntax or logic error it needs to fix.
 
    Returns:
        ChatPromptTemplate ready to pipe into the LLM:
            chain = build_regeneration_prompt() | MODEL
            response = chain.invoke({
                "schema":     schema_chunks,
                "sql_query":  previously_generated_sql,
                "error":      error_message_from_validation,
                "user_query": original_user_question
            })
    """

    return ChatPromptTemplate.from_messages([
        ("system", """You are an expert SQL query generator.
 
Database schema:
{schema}
 
The following SQL query was generated:
{sql_query}
 
It produced this error:
{error}
 
Rewrite the query to fix the error. Use correct syntax, valid column \
names from the schema, and correct logic.
 
NO PREAMBLE. Return only the corrected SQL query.
"""),
("human", "{user_query}")
    ])