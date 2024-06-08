# chatbot.py
import streamlit as st
from langchain_core.messages import ChatMessage
from utils import print_messages, StreamHandler
from langchain.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from pymilvus import connections, db
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Milvus




st.set_page_config(page_title="오늘 뭐 먹지?")
st.title("당신의 메뉴를 골라드립니다.")

# Initialize page

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "store" not in st.session_state:
    st.session_state["store"] = dict()

print_messages()

def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state["store"]:
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids]

#llm model select

OLLAMA_LOCAL_URL = "http://localhost:11434"
llm = Ollama(model="evee-Q5")

#loader for RAG system
loader = TextLoader("./restaurantlist.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

#select embedding model
model_name = "jhgan/ko-sbert-nli"
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    encode_kwargs=encode_kwargs
)

#vector db
vector_db = Milvus.from_documents(
    docs,
    embeddings,
    connection_args={"host": "127.0.0.1", "port": "19530"},
)



if user_input := st.chat_input("무슨 음식을 원하시나요?"):
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

    with st.chat_message("assistant"):
        
        ref = vector_db.similarity_search(user_input)
        llm = Ollama(model="evee-Q5")
        prompt = ChatPromptTemplate.from_messages(
            [
                (""" "system", "질문에 두 문장 이하로 친근하게 답해줘. 추천 메뉴는 세 가지를 넘지 않게 리스트 형식으로 제시해줘. 양식이나 일식 같이 별다른 지정이 없으면 한식으로 추천해줘.
                 
                 Here is context to help : {context}
                 
                 and this is the question u have to answer : {question}
                 """),
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
            {"question": user_input, "history": session_history.messages, "context": ref},
            config={"configurable": {"session_id": "abc123"}},
        )

        st.write(response)
        st.session_state["messages"].append(ChatMessage(role="assistant", content=response))
