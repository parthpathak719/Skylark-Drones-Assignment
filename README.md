# Skylark Drones - Business Intelligence Agent for Monday.com

A founder-level Business Intelligence Assistant built with **Streamlit**, **Google Gemini AI**, and **Monday.com GraphQL API**. The agent answers complex business, financial, and operational queries in real time by fetching live data directly from Monday.com **Work Orders** and **Deals** boards—with zero hardcoded data.

---

## 🌟 Key Features

- **Live Read-Only GraphQL Queries**: Fetches live data from Monday.com Work Orders and Deals boards dynamically.
- **Autonomous Tool Calling**: Powered by Gemini (`google-genai` SDK), which automatically decides when to fetch Work Orders, Deals, or both based on user queries.
- **Cross-Board Intelligence**: Seamlessly correlates sales pipeline metrics with actual operational delivery and receivables by normalizing client code variations across boards.
- **Real-World Data Resilience**: Automatically handles broken Excel formulas (`#VALUE!`), unit labels in numeric fields (e.g., `5360 HA`, `7 mines`), leaked header rows, and missing values without crashing.
- **Modern High-Contrast Dark UI**: Built with Streamlit featuring a customized dark theme, live board status indicators, responsive starting prompt cards, and readable Markdown formatting.
- **Production Cloud Deployment**: Fully configured and deployed on **Streamlit Community Cloud** with secret management and automatic rebuilds.

---

## ☁️ Deployment on Streamlit Community Cloud

The application is deployed live on **Streamlit Community Cloud**.

### Deploying Your Own Instance on Streamlit Cloud

1. **Push your code to GitHub**: Ensure all project files (`app.py`, `agent.py`, `monday_client.py`, `data_cleaning.py`, `requirements.txt`, `.streamlit/config.toml`) are pushed to your repository.
2. **Connect to Streamlit Cloud**:
   - Log in to [share.streamlit.io](https://share.streamlit.io/).
   - Click **New app**, select your repository, branch (`main`), and set the main file path to `app.py`.
3. **Configure Environment Secrets**:
   - In your app dashboard on Streamlit Cloud, go to **Settings** -> **Secrets**.
   - Add your API keys and Board IDs in TOML format:
     ```toml
     MONDAY_API_TOKEN = "your_monday_api_token_here"
     GEMINI_API_KEY = "your_gemini_api_key_here"
     WORK_ORDERS_BOARD_ID = "5030975082"
     DEALS_BOARD_ID = "5030975111"
     ```
   - Click **Save**. Streamlit Cloud will automatically inject these secrets into environment variables for live API connectivity.

---

## 🏗️ Architecture Overview

```
                        +------------------------------------+
                        |       Streamlit Chat UI            |
                        |            (app.py)                |
                        +------------------------------------+
                                          |
                                          v
                        +------------------------------------+
                        |   Gemini Agent Engine              |
                        |           (agent.py)               |
                        | - Model: gemini-3.5-flash-lite     |
                        | - SDK Function Calling Tools       |
                        +------------------------------------+
                               /                    \
                              v                      v
        +----------------------------+  +----------------------------+
        |     get_work_orders()      |  |        get_deals()         |
        +----------------------------+  +----------------------------+
                               \                    /
                                v                  v
                        +------------------------------------+
                        |    Monday.com GraphQL Client       |
                        |        (monday_client.py)          |
                        |  - Read-Only GraphQL Queries       |
                        +------------------------------------+
                                          |
                                          v
                        +------------------------------------+
                        |     Data Cleaning & Metrics        |
                        |        (data_cleaning.py)          |
                        | - Client Code Normalization        |
                        | - Safe Numeric/Date Parsing        |
                        | - Pre-computed Amount Summaries    |
                        +------------------------------------+
```

### Component Breakdown

| Module | File | Responsibility |
| :--- | :--- | :--- |
| **Frontend UI** | [app.py](file:///e:/College%20Stuff/Sem-7/Placements/Skylark%20Drones/Assignment_skylark/app.py) | Streamlit dashboard, sidebar status indicators, starting prompt cards, custom CSS styling, and message loop. |
| **Agent Engine** | [agent.py](file:///e:/College%20Stuff/Sem-7/Placements/Skylark%20Drones/Assignment_skylark/agent.py) | Gemini AI integration, system prompt definition, autonomous tool execution (`get_work_orders`, `get_deals`). |
| **GraphQL Client** | [monday_client.py](file:///e:/College%20Stuff/Sem-7/Placements/Skylark%20Drones/Assignment_skylark/monday_client.py) | Communicates with `api.monday.com/v2`, executing live read-only GraphQL queries for boards and column values. |
| **Data Cleaning** | [data_cleaning.py](file:///e:/College%20Stuff/Sem-7/Placements/Skylark%20Drones/Assignment_skylark/data_cleaning.py) | Cleans messy raw data, normalizes client codes (`normalize_client_code`), parses numbers with units (`safe_float`), detects leaked header rows, and computes totals. |

---

## 🛠️ Monday.com Configuration Guide

To connect the BI Agent to your Monday.com workspace, you need an **API v2 Token** and the **Board IDs** for both Work Orders and Deals.

### 1. How to Generate a Monday.com API Token

1. Log in to your **Monday.com** account.
2. Click your **profile picture** in the bottom-left corner and select **Administration** (or **Developers**).
3. Navigate to the **API** section under **Developers**.
4. Click **Generate** (or copy your existing **Personal API Token**).
5. Copy this token—you will set it as `MONDAY_API_TOKEN` in your `.env` file (or Streamlit Cloud Secrets).

> [!NOTE]
> All queries executed by `monday_client.py` are strictly **read-only** (`query { boards { items_page ... } }`). The application never modifies, creates, or deletes any Monday.com data.

---

### 2. How to Find Board IDs

1. Open Monday.com in your web browser.
2. Navigate to your **Work Orders** board.
3. Look at the browser URL:
   ```
   https://yourcompany.monday.com/boards/5030975082
   ```
   The numeric string at the end (`5030975082`) is your `WORK_ORDERS_BOARD_ID`.
4. Navigate to your **Deals** board and copy the numeric ID from the URL (e.g., `5030975111`) for `DEALS_BOARD_ID`.

---

## 🚀 Environment Setup & Local Installation

### Prerequisites

- **Python 3.9+** installed on your system.
- A **Google Gemini API Key** (free tier available at [Google AI Studio](https://aistudio.google.com/)).
- A **Monday.com API Token** and board IDs (as configured above).

---

### Step-by-Step Installation

1. **Clone or navigate to the repository directory**:
   ```bash
   cd Assignment_skylark
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create your `.env` file**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

5. **Fill in your environment variables** inside `.env`:
   ```env
   MONDAY_API_TOKEN=your_actual_monday_api_token_here
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   WORK_ORDERS_BOARD_ID=5030975082
   DEALS_BOARD_ID=5030975111
   ```

---

## 🧪 Verification & Running the App

### 1. Test Monday.com Connectivity

Run the standalone client test script to verify that your API token and board IDs are working:
```bash
python monday_client.py
```
**Expected Output**:
Prints total item counts and a sample row from both the Work Orders and Deals boards.

### 2. Launch the Streamlit Web Application Locally

Start the interactive Business Intelligence Agent UI:
```bash
streamlit run app.py
```
The application will open automatically in your default browser at `http://localhost:8501`.

---

## 🧹 Data Quality & Resilience Handling

Real-world operational data contains quirks and irregularities. The agent handles these automatically:

- **Excel Formula Errors (`#VALUE!`)**: Occurs when corrupted formula strings exist in Monday.com text columns. `data_cleaning.safe_float` converts `#VALUE!` to `None` instead of crashing.
- **Numbers with Unit Labels**: Fields like `Quantities as per PO` mix plain numbers with units (`5360 HA`, `7 mines`). `data_cleaning.safe_float` extracts the numeric portion while preserving units.
- **Leaked Header Rows**: Rows where header names (e.g. `Close Date (A)`) were mistakenly pasted as data values are detected via `data_cleaning.find_leaked_header_rows` and excluded from calculations.
- **Normalized Client Codes**: Work Orders and Deals format client names differently. `data_cleaning.normalize_client_code` strips punctuation, standardizes casing, and maps client variants to enable seamless cross-board correlation.

---

## 📝 Documentation & Decision Log

Comprehensive analysis, design assumptions, architectural decisions, and trade-offs (such as selecting Gemini AI over Claude for standing daily quota limits and automatic function calling SDK loops) are documented in **`Decision_Log.docx`**.

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Not connected" badge in sidebar** | Missing or invalid `MONDAY_API_TOKEN` / Board IDs. | Check `.env` file (or Streamlit Cloud Secrets) for typos and verify token permissions in Monday.com. |
| **Gemini API Error** | Missing `GEMINI_API_KEY` or quota exceeded. | Get a free API key at [Google AI Studio](https://aistudio.google.com/) and verify it in `.env` / Streamlit Secrets. |
| **Empty tool results** | Incorrect `WORK_ORDERS_BOARD_ID` or `DEALS_BOARD_ID`. | Check the board URL in Monday.com to confirm the numeric board ID. |

---

## 📄 License

This project is built for Skylark Drones Business Intelligence Assignment.
