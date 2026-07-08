import streamlit as st
import requests
import os

API_URL = "http://127.0.0.1:8000/ask"

# Path to data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PDF_PATH = os.path.join(DATA_DIR, "lao_dong.pdf")
DOCX_PATH = os.path.join(DATA_DIR, "lao_dong.docx")

st.set_page_config(
    page_title="VLC AI - Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Enhancement
st.markdown("""
<style>
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Header styling */
    .main-header {
        color: #555;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1e3c72;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<div class="main-header">⚖️ VLC AI - Trợ lý AI Pháp luật</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hệ thống Hỏi Đáp thông minh dựa trên Bộ luật Lao động Việt Nam</div>', unsafe_allow_html=True)

# Sidebar Design
with st.sidebar:
    st.markdown("### 📚 Tài liệu Pháp luật")
    st.markdown("Hệ thống hiện tại đang sử dụng dữ liệu từ **Bộ luật Lao động** để trả lời các câu hỏi của bạn. Bạn có thể tải xuống tài liệu gốc bên dưới để tham khảo.")
    
    st.markdown("---")
    
    with st.expander("📁 Tải xuống tài liệu tham khảo"):
        st.markdown("Bạn có thể tải bộ luật gốc về máy để tham khảo thêm khi cần thiết.")
        # PDF Download
        if os.path.exists(PDF_PATH):
            with open(PDF_PATH, "rb") as pdf_file:
                st.download_button(
                    label="📄 Tải xuống PDF",
                    data=pdf_file,
                    file_name="bo_luat_lao_dong.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
        # DOCX Download
        if os.path.exists(DOCX_PATH):
            with open(DOCX_PATH, "rb") as docx_file:
                st.download_button(
                    label="📝 Tải xuống Word (DOCX)",
                    data=docx_file,
                    file_name="bo_luat_lao_dong.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
        if not os.path.exists(PDF_PATH) and not os.path.exists(DOCX_PATH):
            st.warning("⚠️ Không tìm thấy file tài liệu nào trong thư mục data/raw.")

    st.markdown("---")
    st.markdown("### 💡 Hướng dẫn sử dụng")
    st.info(
        "1. Nhập câu hỏi tình huống hoặc pháp lý vào ô chat.\n"
        "2. Đợi AI phân tích và trả lời.\n"
        "3. Xem các **Trích dẫn luật** để đối chiếu với tài liệu gốc."
    )

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Xin chào! Tôi là Trợ lý AI chuyên về Bộ luật Lao động. Bạn cần tôi giúp gì hôm nay?"
    })

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("📌 Trích dẫn luật chi tiết"):
                for cite in message["citations"]:
                    st.info(cite)

# Chat input
if prompt := st.chat_input("Nhập câu hỏi của bạn (VD: Thời gian nghỉ thai sản?)...", max_chars=500):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Đang tra cứu luật..."):
            try:
                response = requests.post(API_URL, json={"question": prompt, "k": 15})
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Xin lỗi, tôi không thể tìm thấy câu trả lời.")
                    citations = data.get("verified_citations", [])
                    
                    message_placeholder.markdown(answer)
                    if citations:
                        with st.expander("📌 Trích dẫn luật chi tiết"):
                            for cite in citations:
                                st.info(cite)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations
                    })
                else:
                    error_msg = f"❌ Lỗi từ máy chủ: {response.status_code} - {response.text}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.ConnectionError:
                error_msg = "🔌 Không thể kết nối đến hệ thống xử lý. Vui lòng kiểm tra lại server (FastAPI)."
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
