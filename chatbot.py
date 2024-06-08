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

#모델 생성
OLLAMA_LOCAL_URL = "http://localhost:11434"
llm = Ollama(model="evee-Q5")

#기록해야 하는 부분 session state에 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "store" not in st.session_state:
    st.session_state["store"] = dict()

#이전 대화 내역 출력
print_messages()


def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state["store"]:  # 세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids]  # 해당 세션 ID에 대한 세션 기록 반환



if user_input:= st.chat_input("Say something"):
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())

            #1. 모델 생성
        llm = Ollama(model="evee-Q5")

        #2. 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "질문에 두 문장 이하로 친근하게 답하세요. 추천 메뉴는 세 가지를 넘어가지 말 것.",
            ),
            # 대화 기록을 변수로 사용, history 가 MessageHistory 의 key 가 됨
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),  # 사용자 입력을 변수로 사용
        ]
        )
                                                
        # 3. chain 구성
        chain = prompt | llm 

        session_history = get_session_history("abc123")

        chain_with_memory = RunnableWithMessageHistory(  # RunnableWithMessageHistory 객체 생성
            chain,  # 실행할 Runnable 객체
            get_session_history,  # 세션 기록을 가져오는 함수
            input_messages_key="question",  # 사용자 질문의 키
            history_messages_key="history",  # 기록 메시지의 키
        )

        response = chain_with_memory.invoke(
            {
                "question": user_input,
                "history": session_history.messages,  # 여기서 history를 전달
            },
            # 세션 정보
            config={"configurable": {"session_id": "abc123"}},
        )
        
        st.write(response)
        st.session_state["messages"].append(ChatMessage(role="assistant", content=response))