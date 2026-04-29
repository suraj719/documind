import config  # need to import for config initialization # noqa: F401
import streamlit as st
from pages import home_page, login_page, register_page
from sidebar import display_sidebar
from state_management import Page, initialize_state

st.set_page_config(
    page_title="DocuMind | Enterprise Document Intelligence",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background-color: #0b0f19;
            color: #e2e8f0;
        }

        header[data-testid="stHeader"] {
            background-color: rgba(11, 15, 25, 0.85) !important;
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        .documind-hero {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.08) 50%, rgba(16, 185, 129, 0.05) 100%);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 16px;
            padding: 24px 30px;
            margin-bottom: 24px;
        }

        .documind-hero h1 {
            color: #ffffff;
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 2.1rem;
        }

        .documind-hero p {
            color: #94a3b8;
            font-size: 1.05rem;
            margin-bottom: 0;
        }

        .documind-feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 16px;
            margin-bottom: 24px;
        }

        .documind-feature-card {
            background: #1e293b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 18px;
            transition: all 0.2s ease-in-out;
        }

        .documind-feature-card:hover {
            border-color: #6366f1;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.15);
        }

        .documind-card-title {
            font-weight: 600;
            font-size: 1.05rem;
            color: #f8fafc;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .documind-card-desc {
            font-size: 0.88rem;
            color: #94a3b8;
            line-height: 1.4;
        }

        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .documind-pill {
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 8px;
        }

        /* Custom ChatGPT-style Sidebar Chat Cards */
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.chat-item),
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.active-chat-item) {
            margin-bottom: -10px !important;
            margin-top: 0px !important;
        }

        .chat-item [data-testid="stHorizontalBlock"],
        .active-chat-item [data-testid="stHorizontalBlock"] {
            border-radius: 8px;
            padding: 2px 4px;
            margin-bottom: 2px !important;
            transition: all 0.2s ease-in-out;
            align-items: center;
            gap: 2px !important;
        }


        .chat-item [data-testid="stHorizontalBlock"] {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }

        .chat-item [data-testid="stHorizontalBlock"]:hover {
            background: rgba(30, 41, 59, 0.8);
            border-color: rgba(99, 102, 241, 0.4);
        }

        .active-chat-item [data-testid="stHorizontalBlock"] {
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid #6366f1;
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
        }

        .chat-item [data-testid="stHorizontalBlock"] button,
        .active-chat-item [data-testid="stHorizontalBlock"] button {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 4px 6px !important;
            font-size: 0.84rem !important;
            text-align: left !important;
            color: #cbd5e1 !important;
            line-height: 1.3 !important;
        }

        .active-chat-item [data-testid="stHorizontalBlock"] button {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        .chat-item [data-testid="stHorizontalBlock"] button:hover,
        .active-chat-item [data-testid="stHorizontalBlock"] button:hover {
            color: #818cf8 !important;
        }

        .chat-item [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button,
        .active-chat-item [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button {
            font-size: 0.78rem !important;
            opacity: 0.6;
            padding: 4px 2px !important;
            text-align: center !important;
        }

        .chat-item [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button:hover,
        .active-chat-item [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button:hover {
            opacity: 1.0;
            color: #ef4444 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



def main():
    initialize_state()
    inject_custom_css()
    display_sidebar()
    if st.session_state["page"] == Page.HOME:
        home_page()
    elif st.session_state["page"] == Page.LOGIN:
        login_page()
    elif st.session_state["page"] == Page.REGISTER:
        register_page()


if __name__ == "__main__":
    main()

