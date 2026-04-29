import api_utils
import streamlit as st
from chat_components import authenticated_user_chat_interface_component, unauthenticated_user_chat_interface_component
from state_management import Page, authenticate_user


def home_page():
    st.markdown(
        """
        <div class="documind-hero">
            <span class="documind-pill">DocuMind Enterprise Copilot v2.4</span>
            <h1>🧠 Autonomous Intelligence Workspace</h1>
            <p>Upload PDF, DOCX, or TXT documents for deep semantic indexing, hybrid vector retrieval, and live reasoning stream.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state["user"].is_authenticated:
        st.markdown(
            """
            <div class="documind-feature-grid">
                <div class="documind-feature-card">
                    <div class="documind-card-title">📄 Document Parsing</div>
                    <div class="documind-card-desc">Automatic chunking & vector indexing over uploaded PDFs, Word documents, and text files.</div>
                </div>
                <div class="documind-feature-card">
                    <div class="documind-card-title">🤖 ReAct Agent Engine</div>
                    <div class="documind-card-desc">LangGraph state graph with adaptive tool selection and strict privacy guardrails.</div>
                </div>
                <div class="documind-feature-card">
                    <div class="documind-card-title">🌐 Hybrid Web Synthesis</div>
                    <div class="documind-card-desc">Integrates Tavily live search engine for up-to-the-minute real-world queries.</div>
                </div>
                <div class="documind-feature-card">
                    <div class="documind-card-title">💾 Persistent Checkpointer</div>
                    <div class="documind-card-desc">Per-user isolated database state checkpointing and history retention.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("##### 💡 Ask a Query (Public Sandbox Mode)")
        unauthenticated_user_chat_interface_component()
    else:
        st.markdown("##### 💡 Ask DocuMind Copilot")
        authenticated_user_chat_interface_component()


def login_page():
    st.markdown(
        """
        <div style="padding: 10px 0px 20px 0px;">
            <h2 style="color: #ffffff; font-weight: 700; margin-bottom: 4px;">🔐 Sign In to DocuMind</h2>
            <p style="color: #94a3b8; font-size: 0.95rem;">Enter your credentials to access saved knowledge threads and vector stores.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="name@company.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Authenticate Workspace", type="primary")

    back_to_home_component()

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
            return
        with st.spinner("Authenticating session..."):
            login_response = api_utils.login_user(email, password)
            if message := login_response.get("message"):
                st.success(message)
                st.session_state["page"] = Page.HOME
                authenticate_user(login_response)
                st.rerun()
            else:
                st.error(api_utils.format_auth_error(login_response, "Authentication failed. Please check credentials."))


def register_page():
    st.markdown(
        """
        <div style="padding: 10px 0px 20px 0px;">
            <h2 style="color: #ffffff; font-weight: 700; margin-bottom: 4px;">✨ Create Workspace Account</h2>
            <p style="color: #94a3b8; font-size: 0.95rem;">Register to enable isolated document stores, multi-thread checkpointers, and custom models.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        email = col1.text_input("Email Address *", placeholder="name@company.com")
        password = col1.text_input("Password *", type="password", max_chars=32, placeholder="••••••••")
        first_name = col2.text_input("First Name", max_chars=50, placeholder="John")
        last_name = col2.text_input("Last Name", max_chars=50, placeholder="Doe")

        submitted = st.form_submit_button("Register Account", type="primary")

    back_to_home_component()

    if submitted:
        if not email or not password:
            st.error("Please complete all required fields (*).")
            return
        
        register_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        }

        with st.spinner("Creating workspace..."):
            register_response = api_utils.register_user(register_data)
            if message := register_response.get("message"):
                st.success(message)
                st.session_state["page"] = Page.LOGIN
                st.rerun()
            else:
                st.error(api_utils.format_auth_error(register_response, "Registration failed. Please check inputs."))




def back_to_home_component():
    if st.button("⬅️ Return to Workspace"):
        st.session_state["page"] = Page.HOME
        st.rerun()

