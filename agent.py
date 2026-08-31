"""
agent.py

The "brain" of the assistant. Uses Gemini's automatic function calling:
we hand it plain Python functions as tools, and the SDK decides when to
call them, runs them, and loops internally until it has a final answer.
No hand-written tool loop needed.
"""

import os

from google import genai
from google.genai import types

from monday_client import fetch_work_orders, fetch_deals
from data_cleaning import (
    data_quality_report,
    find_leaked_header_rows,
    normalize_client_code,
    summarize_amounts,
)

MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """You are a business intelligence assistant that answers questions
about a company's Work Orders (project execution data) and Deals (sales pipeline
data), pulled live from monday.com.

Ground rules:
- Always use the tools to get real data before answering. Never make up numbers.
- The data is real-world messy: fields can be missing, dates can be malformed,
  and some numeric fields contain stray text (like "#VALUE!" or units such as "5360 HA").
  Handle this gracefully, mention data quality caveats when they affect your answer,
  and do not silently drop or ignore rows, tell the user what you excluded and why.
- Some rows may be flagged as "corrupted_rows" in the tool results, meaning a header
  row got accidentally pasted into the data instead of real values. Exclude these rows
  from your analysis and mention that they were excluded, do not try to parse them.
- Each row includes a "Client Code (normalized)" field. Use this field, not the raw
  "Customer Name Code" or "Client Code" fields, to match the same client between
  Work Orders and Deals, since the two boards format the same client differently.
- Each tool result includes an "amount_summary" with a pre-computed, reliable total
  (and a breakdown by status or stage) for the main money field on that board. Use
  these pre-computed totals when reporting sums across many rows, instead of adding
  the row amounts yourself, since manually summing many decimal numbers in-context
  is error-prone. You can still reference individual row amounts for row-level detail.
- If a question is ambiguous (for example, unclear time period or sector), ask a short
  clarifying question instead of guessing.
- Give business context and takeaways, not just raw numbers. Someone asking wants
  insight, not a spreadsheet dump.
- When useful, query both boards and connect the two (for example, work order execution
  health next to pipeline health for the same sector).
"""


def get_work_orders() -> dict:
    """Fetches all Work Orders data from monday.com. Work Orders track project
    execution: sector, type of work, billing status, amounts, quantities, dates,
    and collection status. Use this for questions about operations, execution,
    billing, or delivery.
    """
    rows = fetch_work_orders()
    for row in rows:
        row["Client Code (normalized)"] = normalize_client_code(row.get("Customer Name Code"))

    quality = data_quality_report(
        rows,
        fields_to_check=["Amount in Rupees (Excl of GST) (Masked)", "Quantities as per PO"],
    )
    corrupted = find_leaked_header_rows(rows)
    amount_summary = summarize_amounts(
        rows,
        amount_field="Amount in Rupees (Excl of GST) (Masked)",
        group_by_field="Execution Status",
    )

    return {
        "rows": rows,
        "row_count": len(rows),
        "data_quality_notes": quality,
        "corrupted_rows": corrupted,
        "amount_summary": amount_summary,
    }


def get_deals() -> dict:
    """Fetches all Deals data from monday.com. Deals track the sales pipeline:
    deal stage, status, probability, value, sector, and dates. Use this for
    questions about pipeline, sales, sectors, or forecasted revenue.
    """
    rows = fetch_deals()
    for row in rows:
        row["Client Code (normalized)"] = normalize_client_code(row.get("Client Code"))

    quality = data_quality_report(
        rows,
        fields_to_check=["Masked Deal value", "Close Date (A)"],
    )
    corrupted = find_leaked_header_rows(rows)
    amount_summary = summarize_amounts(
        rows,
        amount_field="Masked Deal value",
        group_by_field="Deal Status",
    )

    return {
        "rows": rows,
        "row_count": len(rows),
        "data_quality_notes": quality,
        "corrupted_rows": corrupted,
        "amount_summary": amount_summary,
    }


def _to_gemini_history(conversation_history):
    """Converts our simple {"role": "user"|"assistant", "content": str} list
    into Gemini Content objects. Gemini calls the assistant role "model".
    """
    history = []
    for message in conversation_history:
        role = "model" if message["role"] == "assistant" else "user"
        history.append(types.Content(role=role, parts=[types.Part(text=message["content"])]))
    return history


def get_agent_reply(conversation_history):
    """
    conversation_history: list of {"role": "user"|"assistant", "content": str}
    Returns the assistant's final text reply as a string.

    The Gemini SDK handles the tool-call loop internally (automatic function
    calling), so this just needs to send the latest message with the prior
    turns as history.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    *history, latest = _to_gemini_history(conversation_history)

    chat = client.chats.create(
        model=MODEL,
        history=history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_work_orders, get_deals],
        ),
    )

    try:
        response = chat.send_message(latest.parts[0].text)
    except Exception as exc:
        return f"Something went wrong talking to monday.com or Gemini: {exc}"

    return response.text or "I wasn't able to come up with an answer to that. Try rephrasing your question."