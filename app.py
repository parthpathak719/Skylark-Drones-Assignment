import streamlit as st
from dotenv import load_dotenv

from agent import get_agent_reply
from monday_client import fetch_work_orders, fetch_deals

load_dotenv()

st.set_page_config(
    page_title="Monday.com BI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Complete Styling System & CSS Overrides
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    /* 1. FORCE ENTIRE ROOT APP & BOTTOM CONTAINER DARK */
    html, body, .stApp, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stToolbar"],
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"],
    footer,
    .stChatInputContainer {
        background-color: #0B0D14 !important;
        background: #0B0D14 !important;
        color: #F1F5F9 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Header background transparent */
    [data-testid="stHeader"] {
        background: transparent !important;
        color: #F1F5F9 !important;
    }

    /* Hide Deploy button and toolbar clutter */
    [data-testid="stToolbar"],
    [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* Ensure Sidebar Expand & Collapse Control Arrow is always visible & styled */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #F1F5F9 !important;
        background: #141722 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        margin-top: 8px !important;
        margin-left: 8px !important;
        z-index: 999999 !important;
    }

    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button {
        color: #F1F5F9 !important;
        background: transparent !important;
        border: none !important;
    }

    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #F1F5F9 !important;
        color: #F1F5F9 !important;
    }

    /* 2. SIDEBAR DARK SHADE */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #121520 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* 3. MAIN CONTENT CONTAINER LAYOUT */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1050px !important;
    }

    /* 4. HERO BANNER HEADER */
    .hero-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #141722;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0073EA 0%, #00C875 33%, #FDAB3D 66%, #E2445C 100%);
    }
    .hero-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .logo-box {
        width: 44px;
        height: 44px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .logo-grid {
        display: grid;
        grid-template-columns: 12px 12px;
        grid-template-rows: 12px 12px;
        gap: 3px;
    }
    .logo-grid span { border-radius: 2px; display: block; }

    .hero-title {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    .hero-sub {
        font-size: 0.84rem !important;
        color: #94A3B8 !important;
        margin: 4px 0 0 0 !important;
    }

    /* 5. SIDEBAR BRANDING & CARDS */
    .sb-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }
    .sb-logo {
        width: 34px;
        height: 34px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logo-grid-sm {
        display: grid;
        grid-template-columns: 9px 9px;
        grid-template-rows: 9px 9px;
        gap: 2px;
    }
    .logo-grid-sm span { border-radius: 2px; display: block; }
    .sb-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .sb-sub {
        font-size: 0.72rem;
        color: #94A3B8;
    }

    .sb-section-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: #CBD5E1;
        margin-bottom: 10px;
    }

    .board-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .board-card-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .board-card-name {
        font-size: 0.85rem;
        font-weight: 500;
        color: #F1F5F9;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot.live { background: #00C875; box-shadow: 0 0 6px #00C875; }
    .status-dot.down { background: #E2445C; box-shadow: 0 0 6px #E2445C; }

    .board-card-pill {
        font-size: 0.73rem;
        font-weight: 600;
        color: #38BDF8;
        background: rgba(0, 115, 234, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 2px 8px;
        border-radius: 12px;
    }

    /* 6. SIDEBAR STARTING PROMPT CARDS (MULTI-LINE AUTO FIT) */
    [data-testid="stSidebar"] .stButton button {
        width: 100% !important;
        height: auto !important;
        min-height: 48px !important;
        max-height: none !important;
        display: block !important;
        text-align: left !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.4 !important;
        padding: 10px 12px !important;
        background: #141722 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #E2E8F0 !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(0, 115, 234, 0.15) !important;
        border-color: #0073EA !important;
        color: #38BDF8 !important;
        transform: translateY(-1px);
    }

    /* 7. CAPABILITY CARDS UNIFORM HEIGHT */
    .section-title {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: #E2E8F0 !important;
        margin-bottom: 14px !important;
    }
    .cap-card {
        background: #141722;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        height: 155px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .cap-icon {
        font-size: 1.3rem;
        margin-bottom: 8px;
    }
    .cap-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 6px;
    }
    .cap-desc {
        font-size: 0.78rem;
        color: #94A3B8;
        line-height: 1.4;
    }

    /* 8. CHAT INPUT BAR STYLING */
    [data-testid="stChatInput"] {
        background-color: #161924 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 0.9rem !important;
        font-family: 'Inter', sans-serif !important;
        background-color: transparent !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #0073EA !important;
        box-shadow: 0 0 0 2px rgba(0, 115, 234, 0.25) !important;
    }
    [data-testid="stChatInput"] button {
        color: #0073EA !important;
    }

    /* 9. CHAT MESSAGES & HIGH CONTRAST TEXT FIX */
    [data-testid="stChatMessage"] {
        background-color: #141722 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #0F223D !important;
        border-color: rgba(0, 115, 234, 0.4) !important;
    }

    /* FORCE ALL CHAT TEXT ELEMENTS TO BRIGHT WHITE/CYAN */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] ol,
    [data-testid="stChatMessage"] ul,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        font-size: 0.92rem !important;
        line-height: 1.6 !important;
    }

    [data-testid="stChatMessage"] strong, 
    [data-testid="stChatMessage"] b {
        color: #38BDF8 !important;
        -webkit-text-fill-color: #38BDF8 !important;
        font-weight: 700 !important;
    }

    [data-testid="stChatMessage"] code {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #38BDF8 !important;
        -webkit-text-fill-color: #38BDF8 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
    }

    /* 10. RESPONSE TABLES */
    [data-testid="stChatMessage"] table {
        border-collapse: collapse !important;
        width: 100% !important;
        margin: 14px 0 !important;
        font-size: 0.86rem !important;
    }
    [data-testid="stChatMessage"] th {
        background: rgba(0, 115, 234, 0.25) !important;
        color: #38BDF8 !important;
        -webkit-text-fill-color: #38BDF8 !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        text-align: left !important;
    }
    [data-testid="stChatMessage"] td {
        padding: 9px 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=300, show_spinner=False)
def _board_status():
    try:
        work_orders = fetch_work_orders()
        deals = fetch_deals()
        return {"ok": True, "work_orders": len(work_orders), "deals": len(deals)}
    except Exception:
        return {"ok": False, "work_orders": None, "deals": None}


status = _board_status()

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="sb-header">
            <div class="sb-logo">
                <div class="logo-grid-sm">
                    <span style="background:#0073EA;"></span>
                    <span style="background:#00C875;"></span>
                    <span style="background:#FDAB3D;"></span>
                    <span style="background:#E2445C;"></span>
                </div>
            </div>
            <div>
                <div class="sb-title">Monday.com BI</div>
                <div class="sb-sub">Intelligence Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-section-title">🔌 Connected Boards</div>', unsafe_allow_html=True)

    dot_status = "live" if status["ok"] else "down"
    wo_label = f"{status['work_orders']} items" if status["ok"] else "Not connected"
    deal_label = f"{status['deals']} items" if status["ok"] else "Not connected"

    st.markdown(
        f"""
        <div class="board-card">
            <div class="board-card-left">
                <span class="status-dot {dot_status}"></span>
                <span class="board-card-name">Work Orders</span>
            </div>
            <span class="board-card-pill">{wo_label}</span>
        </div>
        <div class="board-card">
            <div class="board-card-left">
                <span class="status-dot {dot_status}"></span>
                <span class="board-card-name">Deals</span>
            </div>
            <span class="board-card-pill">{deal_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not status["ok"]:
        st.caption("⚠️ Check your `.env` file — `MONDAY_API_TOKEN` or board IDs missing.")

    st.markdown('<div class="sb-section-title" style="margin-top:24px;">💡 Suggested Starting Prompts</div>', unsafe_allow_html=True)

    sb_prompts = [
        ("📈 How is our pipeline for the energy sector this quarter?", "How is our pipeline for the energy sector this quarter?"),
        ("⚠️ Which work orders have overdue receivables?", "Which work orders have overdue receivables?"),
        ("📊 What's our sector mix across open deals?", "What's our sector mix across open deals?"),
        ("⭐ Is COMPANY009 a good customer?", "Is COMPANY009 a good customer?"),
    ]

    for i, (label, question) in enumerate(sb_prompts):
        if st.button(label, use_container_width=True, key=f"sb_prompt_{i}"):
            st.session_state.pending_question = question
            st.rerun()

    if st.session_state.get("messages"):
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Conversation", use_container_width=True, key="clear_chat_sb"):
            st.session_state.messages = []
            st.rerun()

# Main Header Banner (Without model badge)
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-left">
            <div class="logo-box">
                <div class="logo-grid">
                    <span style="background:#0073EA;"></span>
                    <span style="background:#00C875;"></span>
                    <span style="background:#FDAB3D;"></span>
                    <span style="background:#E2445C;"></span>
                </div>
            </div>
            <div>
                <h1 class="hero-title">Monday.com Business Intelligence Agent</h1>
                <p class="hero-sub">Ask about Work Orders and Deals, pulled live from Monday.com GraphQL.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle user input FIRST so state updates before checking if welcome screen should render
typed_input = st.chat_input("Ask a question, for example: How is our pipeline for the energy sector this quarter?")
pending = st.session_state.pop("pending_question", None)
user_input = typed_input or pending

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

# Capabilities Overview (ONLY when no messages exist)
if len(st.session_state.messages) == 0:
    st.markdown('<div class="section-title">🚀 Capabilities Overview</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="cap-card">
                <div class="cap-icon">📋</div>
                <div class="cap-title">Work Orders & Operations</div>
                <div class="cap-desc">Track project delivery health, PO quantities, execution status, and overdue receivables.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="cap-card">
                <div class="cap-icon">📈</div>
                <div class="cap-title">Sales Pipeline & Deals</div>
                <div class="cap-desc">Analyze deal stages, sector distributions, win probabilities, and close date forecasts.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="cap-card">
                <div class="cap-icon">💡</div>
                <div class="cap-title">Cross-Board Intelligence</div>
                <div class="cap-desc">Correlate live sales pipeline metrics with execution history per normalized client code.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Render Chat History
for message in st.session_state.messages:
    avatar = "📊" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Generate assistant reply if the latest turn is from user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="📊"):
        with st.spinner("Querying Monday.com and generating intelligence report..."):
            try:
                reply = get_agent_reply(st.session_state.messages)
            except Exception as exc:
                reply = f"Something went wrong talking to Monday.com or Gemini: {exc}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()