import asyncio
import json

import api_utils
import streamlit as st
from loguru import logger
from state_management import new_chat, update_document_list, update_thread, update_user_threads


def authenticated_user_chat_interface_component():
    is_first_message = False
    for message in st.session_state["thread"].messages:
        avatar = "👤" if message["role"] == "human" else "🧠"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input(
        "Ask DocuMind Copilot or attach files (PDF, DOCX, TXT)...",
        accept_file="multiple",
        key="prompt",
        file_type=["pdf", "docx", "txt"],
    ):
        if st.session_state["thread"].id is None:
            is_first_message = True
            thread_id = api_utils.create_new_thread().get("id")
            if thread_id is None:
                raise ValueError("Failed to create chat thread session.")
            st.session_state["thread"].id = thread_id

        text = prompt.text or ""
        files = prompt.files or []
        if text:
            st.session_state["thread"].messages.append({"role": "human", "content": text})

        if is_first_message:
            update_thread(st.session_state["thread"].id, f"{text[:30]}")
            update_user_threads()

        with st.chat_message("human", avatar="👤"):
            st.markdown(text or "*[File attached for processing]*")
            for up in files:
                st.caption(f"📄 Attached: `{up.name}`")

        for file in files:
            with st.spinner(f"Indexing `{file.name}` into Vector Store..."):
                resp = api_utils.upload_document(st.session_state["thread"].id, file)
                if resp and "document_id" in resp:
                    if resp.get("warning"):
                        st.warning(f"⚠️ {resp.get('message')}")
                    else:
                        st.success(f"✅ Indexed `{file.name}` ➔ Document ID: `{resp['document_id']}`")
                else:
                    detail = resp.get("detail") if isinstance(resp, dict) else None
                    st.error(f"Failed to index `{file.name}`: {detail or 'Unknown error'}")


        if files:
            update_document_list(st.session_state["thread"].id)

        with st.chat_message("ai", avatar="🧠"):
            steps_container = st.container()
            answer_placeholder = st.empty()
            full_response = ""

            async def fetch_stream():
                nonlocal full_response
                try:
                    chat_data = {"prompt": text, "model_name": st.session_state["model_name"]}
                    async for line in api_utils.chat_stream(chat_data, st.session_state["thread"].id):
                        try:
                            event: dict = json.loads(line)
                            event_type = event.get("type")

                            if event_type == "tool_call":
                                with steps_container:
                                    st.info(
                                        f"⚙️ **Executing Tool:** `{event['name']}` | Parameters: `{event['args']}`"
                                    )

                            elif event_type == "tool_result":
                                with steps_container:
                                    with st.expander(f"📊 Tool Retrieval Payload (`{event['name']}`)", expanded=False):
                                        st.code(event["content"], language="json")

                            elif event_type == "llm_chunk":
                                full_response += event.get("content", "")
                                answer_placeholder.markdown(full_response + "▌")

                            else:
                                logger.warning(f"Unknown stream event payload: {event_type}")

                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Could not parse stream line: {line} - Error: {e}")

                    answer_placeholder.markdown(full_response)
                    if full_response:
                        st.session_state["thread"].messages.append({"role": "ai", "content": full_response})

                except Exception as e:
                    logger.error(f"Error in fetch_stream: {e}")
                    err_str = str(e).lower()
                    if "connect" in err_str or "connection" in err_str or "httpx" in err_str:
                        user_friendly_err = "⚠️ **Cannot connect to DocuMind backend server.** Please verify the server is running at http://127.0.0.1:8000."
                    elif "429" in err_str or "rate limit" in err_str:
                        user_friendly_err = "⚠️ **Model Rate Limit Exceeded.** Please switch to another model from the sidebar or try again in a minute."
                    elif "404" in err_str or "model" in err_str:
                        user_friendly_err = "⚠️ **Selected AI model unavailable.** Please choose a different model from the sidebar dropdown."
                    else:
                        clean_err = str(e).split("\n")[0] if e else "Connection lost."
                        user_friendly_err = f"⚠️ **Communication Error**: {clean_err}"

                    st.error(user_friendly_err)
                    if is_first_message:
                        api_utils.delete_thread(st.session_state["thread"].id)
                        logger.info(f"Thread {st.session_state['thread'].id} cleaned up.")
                        new_chat()


        with st.spinner("DocuMind Copilot reasoning..."):
            asyncio.run(fetch_stream())

        if is_first_message:
            update_user_threads()
            st.rerun()



def unauthenticated_user_chat_interface_component():
    for message in st.session_state["thread"].messages:
        avatar = "👤" if message["role"] == "human" else "🧠"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a general query in public sandbox...", key="prompt"):
        st.session_state["thread"].messages.append({"role": "human", "content": prompt})

        with st.chat_message("human", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("ai", avatar="🧠"):
            placeholder = st.empty()
            full_response = ""

            async def fetch_stream():
                nonlocal full_response
                try:
                    chat_data = {"prompt": prompt, "model_name": st.session_state["model_name"]}
                    async for line in api_utils.simple_chat_stream(chat_data):
                        try:
                            chunk = json.loads(line).get("content")
                            full_response += chunk
                            placeholder.markdown(full_response + "▌")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Could not parse stream event: {line} - Error: {e}")

                    placeholder.markdown(full_response)
                    st.session_state["thread"].messages.append({"role": "ai", "content": full_response})
                except Exception:
                    st.error("An error occurred while processing your request. Please try again.")

            with st.spinner("Generating response..."):
                asyncio.run(fetch_stream())

