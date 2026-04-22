import api_utils
import streamlit as st
from config import settings
from state_management import Page, change_thread, logout_user, new_chat, update_document_list, update_user_threads


def display_sidebar():
    st.sidebar.markdown(
        """
        <div style="text-align: left; padding: 10px 0px 15px 0px;">
            <div style="font-size: 1.6rem; font-weight: 700; color: #ffffff; display: flex; align-items: center; gap: 8px;">
                <span>🧠</span> <span>DocuMind</span>
            </div>
            <div style="font-size: 0.78rem; color: #818cf8; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">
                Autonomous Document Intelligence Copilot
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state["user"].is_authenticated:
        greeting_component()
        model_selection_component()
        chat_history_component()
        document_list_component()
        logout_component()
    else:
        authentication_component()


def authentication_component():
    st.sidebar.markdown("### 🔐 Workspace Access")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("🔑 Login", use_container_width=True):
        st.session_state["page"] = Page.LOGIN
    if col2.button("✨ Register", use_container_width=True):
        st.session_state["page"] = Page.REGISTER
    st.sidebar.caption("Sign in to save conversation threads and index custom files.")


def greeting_component():
    st.sidebar.markdown(f"### 👤 {st.session_state['user'].username}")
    if st.sidebar.button("➕ New Thread", use_container_width=True, type="primary"):
        new_chat()


def model_selection_component():
    st.sidebar.markdown("### 🤖 Intelligence Model")
    st.session_state["model_name"] = st.sidebar.selectbox(
        "Select Model",
        options=settings.model_names,
        key="model",
        label_visibility="collapsed",
    )


def chat_history_component():
    st.sidebar.markdown("### 💬 Saved Conversations")
    threads = st.session_state["user"].threads

    if threads:
        for thread in threads:
            col1, col2, col3 = st.sidebar.columns([0.15, 0.70, 0.15])
            with col1:
                if st.button("📌", key=f"select_{thread['id']}"):
                    change_thread(thread["id"])
            with col2:
                st.markdown(f"**{thread['title']}**")
            with col3:
                if st.button("🗑️", key=f"delete_{thread['id']}"):
                    with st.spinner(""):
                        delete_response = api_utils.delete_thread(thread["id"])
                        if delete_response.get("status") == "ok":
                            st.sidebar.success("Thread removed.")
                            update_user_threads()
                            new_chat()
                            st.rerun()
                        else:
                            st.sidebar.error("Failed to remove thread.")
    else:
        st.sidebar.caption("No saved conversations yet.")


def document_list_component():
    st.sidebar.markdown("### 📄 Indexed Knowledge Base")
    documents = st.session_state["thread"].documents
    if documents:
        for number, doc in enumerate(documents, start=1):
            col1, col2 = st.sidebar.columns([0.85, 0.15])
            with col1:
                st.markdown(f"**{number}.** `{doc['file_name']}`")
            with col2:
                if st.button("🗑️", key=f"delete_{doc['id']}"):
                    with st.spinner(""):
                        delete_response = api_utils.delete_document(doc["id"])
                        if delete_response:
                            st.sidebar.success("Document removed.")
                            update_document_list(st.session_state["thread"].id)
                            st.rerun()
                        else:
                            st.sidebar.error("Failed to remove document.")
    else:
        st.sidebar.caption("No documents indexed in current session.")


def logout_component():
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        logout_user()
        st.rerun()

