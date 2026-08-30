"""
monday_client.py

Handles all communication with monday.com.
Everything here is READ-ONLY, per the assignment's integration requirements.

This module never hardcodes board data. Every call goes out to the
monday.com API live, so the agent always sees the current state of the boards.
"""

import os
import requests

MONDAY_API_URL = "https://api.monday.com/v2"


def _get_headers():
    token = os.environ.get("MONDAY_API_TOKEN")
    if not token:
        raise RuntimeError(
            "MONDAY_API_TOKEN is not set. Add it to your .env file."
        )
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "API-Version": "2024-10",
    }


def _run_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(MONDAY_API_URL, json=payload, headers=_get_headers(), timeout=30)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise RuntimeError(f"monday.com API error: {data['errors']}")

    return data["data"]


def _flatten_item(item):
    """
    Turns a raw monday.com item into a simple flat dict.
    Column titles become dict keys, so downstream code and the LLM
    can work with human readable field names instead of column ids.
    """
    flat = {"id": item["id"], "name": item["name"]}
    for col in item.get("column_values", []):
        title = col["column"]["title"]
        # "text" is the human readable rendering of the value.
        # It is blank/null-safe, which matters a lot given how messy this data is.
        flat[title] = col.get("text") or None
    return flat


def fetch_board_items(board_id, limit_per_page=100, max_pages=50):
    """
    Fetches every item on a board, handling pagination automatically.
    Returns a list of flat dicts, one per row/item.
    """
    items = []

    query = """
    query ($boardId: [ID!], $limit: Int!) {
        boards(ids: $boardId) {
            name
            items_page(limit: $limit) {
                cursor
                items {
                    id
                    name
                    column_values {
                        id
                        text
                        value
                        column {
                            title
                        }
                    }
                }
            }
        }
    }
    """

    variables = {"boardId": [str(board_id)], "limit": limit_per_page}
    data = _run_query(query, variables)

    boards = data.get("boards", [])
    if not boards:
        raise RuntimeError(f"No board found with id {board_id}. Check the id and your API token's access.")

    board = boards[0]
    page = board["items_page"]
    cursor = page["cursor"]

    for item in page["items"]:
        items.append(_flatten_item(item))

    # Follow the cursor until monday.com stops returning one.
    next_query = """
    query ($cursor: String!, $limit: Int!) {
        next_items_page(cursor: $cursor, limit: $limit) {
            cursor
            items {
                id
                name
                column_values {
                    id
                    text
                    value
                    column {
                        title
                    }
                }
            }
        }
    }
    """

    pages_fetched = 1
    while cursor and pages_fetched < max_pages:
        next_data = _run_query(next_query, {"cursor": cursor, "limit": limit_per_page})
        next_page = next_data["next_items_page"]
        for item in next_page["items"]:
            items.append(_flatten_item(item))
        cursor = next_page["cursor"]
        pages_fetched += 1

    return items


def fetch_work_orders():
    board_id = os.environ.get("WORK_ORDERS_BOARD_ID")
    if not board_id:
        raise RuntimeError("WORK_ORDERS_BOARD_ID is not set in your .env file.")
    return fetch_board_items(board_id)


def fetch_deals():
    board_id = os.environ.get("DEALS_BOARD_ID")
    if not board_id:
        raise RuntimeError("DEALS_BOARD_ID is not set in your .env file.")
    return fetch_board_items(board_id)


if __name__ == "__main__":
    # Quick manual test: run "python monday_client.py" to sanity check your setup.
    from dotenv import load_dotenv
    load_dotenv()

    print("Fetching Work Orders...")
    work_orders = fetch_work_orders()
    print(f"Got {len(work_orders)} work orders. First row:")
    print(work_orders[0] if work_orders else "No rows found.")

    print("\nFetching Deals...")
    deals = fetch_deals()
    print(f"Got {len(deals)} deals. First row:")
    print(deals[0] if deals else "No rows found.")
