import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="VLC AI - Legal Assistant",
    page_icon="⚖️",
    layout="centered"
)

st.title("VLC AI - Trợ lý Ảo Pháp luật")
st.markdown("Hệ thống hỏi đáp dựa trên Bộ luật Lao động Việt Nam.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("Trích dẫn luật (Citations)"):
                for cite in message["citations"]:
                    st.markdown(f"- {cite}")

if prompt := st.chat_input("Nhập câu hỏi về Bộ luật Lao động..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Đang suy nghĩ...")
        
        try:
            response = requests.post(API_URL, json={"question": prompt, "k": 5})
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "Không có câu trả lời.")
                citations = data.get("verified_citations", [])
                
                message_placeholder.markdown(answer)
                if citations:
                    with st.expander("Trích dẫn luật (Citations)"):
                        for cite in citations:
                            st.markdown(f"- {cite}")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "citations": citations
                })
            else:
                error_msg = f"Lỗi từ server: {response.text}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except requests.exceptions.ConnectionError:
            error_msg = "Không thể kết nối đến Backend. Vui lòng đảm bảo FastAPI đã được chạy."
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
