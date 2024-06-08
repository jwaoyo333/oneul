# chatbot.py
import streamlit as st
from langchain_core.messages import ChatMessage
from utils import print_messages, StreamHandler
from langchain.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

st.set_page_config(page_title="오늘 뭐 먹지?")
st.title("당신의 메뉴를 골라드립니다.")

# Check if user is authenticated
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.warning("Please log in through the Flask app to access this feature.")
    st.stop()

# Initialize the chatbot
OLLAMA_LOCAL_URL = "http://localhost:11434"
llm = Ollama(model="evee-Q5")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "store" not in st.session_state:
    st.session_state["store"] = dict()

print_messages()

def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state["store"]:
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids]

if user_input := st.chat_input("Say something"):
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())

        llm = Ollama(model="evee-Q5")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "질문에 두 문장 이하로 친근하게 답하세요. 추천 메뉴는 세 가지를 넘어가지 말 것."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )

        chain = prompt | llm
        session_history = get_session_history("abc123")

        chain_with_memory = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        response = chain_with_memory.invoke(
            {"question": user_input, "history": session_history.messages},
            config={"configurable": {"session_id": "abc123"}},
        )

        st.write(response)
        st.session_state["messages"].append(ChatMessage(role="assistant", content=response))
