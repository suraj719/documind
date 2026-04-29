import json
from typing import Any, AsyncGenerator, AsyncIterable

from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from loguru import logger
from pydantic import BaseModel


class PromptInput(BaseModel):
    prompt: str
    model_name: str


class Message(BaseModel):
    role: str
    content: str


def humanize_error_message(err: Any) -> str:
    err_str = str(err).lower()

    if "429" in err_str or "rate_limit" in err_str or "tokens" in err_str or "otpm" in err_str or "tpm" in err_str:
        return (
            "⚠️ **Model Rate Limit Exceeded**\n\n"
            "The selected AI model has temporarily reached its usage limit on Groq.\n\n"
            "👉 **Solution**: Please switch to a different model in the sidebar dropdown (e.g., `openai/gpt-oss-120b` or `groq/compound`) or wait 1 minute before trying again."
        )
    elif "404" in err_str or "model_not_found" in err_str or "does not exist" in err_str:
        return (
            "⚠️ **Selected Model Unavailable**\n\n"
            "The chosen AI model is currently offline or unreachable.\n\n"
            "👉 **Solution**: Please select an active model from the sidebar dropdown."
        )
    elif "401" in err_str or "403" in err_str or "invalid_api_key" in err_str or "unauthorized" in err_str:
        return (
            "⚠️ **AI Provider Authentication Failed**\n\n"
            "Could not authenticate with the AI provider service.\n\n"
            "👉 **Solution**: Please check your backend API key configuration."
        )
    elif "connection" in err_str or "timeout" in err_str or "closed" in err_str or "operationalerror" in err_str:
        return (
            "⚠️ **Network / Server Interruption**\n\n"
            "Lost connection to the backend database or AI service.\n\n"
            "👉 **Solution**: Please try sending your message again."
        )
    elif "nul" in err_str or "0x00" in err_str:
        return (
            "⚠️ **Document Processing Error**\n\n"
            "The uploaded file contains corrupted null-byte characters.\n\n"
            "👉 **Solution**: Please try re-uploading a clean text or PDF document."
        )
    else:
        clean_msg = str(err).split("\n")[0] if err else "An unexpected error occurred."
        return f"⚠️ **Unable to Complete Request**\n\n{clean_msg}"


class ChatStreamResponse(StreamingResponse):
    """
    It processes the LangGraph stream in different stream modes ("updates", "messages") and formats the data
    into JSON objects before sending them to the client.
    """

    def __init__(self, astream: AsyncIterable[dict[str, Any | Any]], **kwargs):
        super().__init__(content=self.process_stream(astream), **kwargs)

    async def process_stream(self, astream: AsyncIterable[dict[str, Any | Any]]) -> AsyncGenerator[str, Any]:
        try:
            async for stream_mode, chunk in astream:
                if stream_mode == "messages":
                    yield self._handle_messages_stream(chunk)  # type: ignore

                elif stream_mode == "updates":
                    async for formatted_chunk in self._handle_updates_stream(chunk):  # type: ignore
                        yield formatted_chunk
        except Exception as e:
            logger.exception("Error during process_stream generation")
            user_msg = humanize_error_message(e)
            err_resp = {"type": "llm_chunk", "content": f"\n\n{user_msg}"}
            yield json.dumps(err_resp) + "\n"



    def _handle_messages_stream(self, chunk: tuple[AIMessageChunk | AIMessage, Any]) -> str:
        message = chunk[0]
        if isinstance(message, (AIMessageChunk, AIMessage)) and message.content:
            response = {"type": "llm_chunk", "content": str(message.content)}
            return json.dumps(response) + "\n"
        return ""

    async def _handle_updates_stream(self, chunk: dict[str, Any]) -> AsyncGenerator[str, Any]:
        for node_output in chunk.values():
            if "messages" not in node_output:
                continue

            message = node_output["messages"][-1]

            if isinstance(message, AIMessage):
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        response = {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
                        yield json.dumps(response) + "\n"

            elif isinstance(message, ToolMessage):
                response = {"type": "tool_result", "name": message.name, "content": message.content}
                yield json.dumps(response) + "\n"

            else:
                response = {"type": message.type, "content": message.content}
                logger.debug(f"Unknown message type: {message.type} - {json.dumps(response)}")
