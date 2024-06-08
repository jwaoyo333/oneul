from typing import Any
from uuid import UUID
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk
import streamlit as st
from langchain_core.callbacks.base import BaseCallbackHandler


def print_messages():
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0 :
        for chat_message in st.session_state["messages"]:
            st.chat_message(chat_message.role).write(chat_message.content)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
    
    def on_llm_new_token(self, token: str, **kwargs) -> Any:
        self.text += token
        self.container.markdown(self.text)