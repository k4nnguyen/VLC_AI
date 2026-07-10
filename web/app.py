import streamlit as st
import requests
import os
import re

API_URL = "http://127.0.0.1:8000/ask"

# Path to data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PDF_PATH = os.path.join(DATA_DIR, "lao_dong.pdf")
DOCX_PATH = os.path.join(DATA_DIR, "lao_dong.docx")

# Map internal doc_name to display name
DOCS_MAP = {
    "lao_dong": "Bộ luật Lao động 2019",
    "giao_thong": "Nghị định 168/2024 (Xử phạt Giao thông)"
}

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
st.markdown('<div class="sub-header">Hệ thống Hỏi Đáp thông minh dựa trên Pháp luật Việt Nam</div>', unsafe_allow_html=True)

# Sidebar Design
with st.sidebar:
    st.markdown("### 📚 Chọn Bộ Luật")
    selected_doc_name = st.selectbox(
        "Vui lòng chọn bộ luật để tra cứu:",
        options=list(DOCS_MAP.keys()),
        format_func=lambda x: DOCS_MAP[x]
    )
    
    st.markdown(f"Hệ thống hiện tại đang sử dụng dữ liệu từ **{DOCS_MAP[selected_doc_name]}** để trả lời các câu hỏi của bạn.")
    st.markdown("---")
    
    st.markdown("### ⚙️ Cài đặt Phân tích")
    enable_reasoning = st.toggle("Bật phân tích chuyên sâu (Reasoning)", value=True, help="Nếu bật, AI sẽ giải thích từng bước cách nó tìm ra và áp dụng luật (sẽ chậm hơn khoảng 3-5 giây).")
    st.markdown("---")
    
    # Update paths dynamically based on selection
    pdf_path = os.path.join(DATA_DIR, f"{selected_doc_name}.pdf")
    docx_path = os.path.join(DATA_DIR, f"{selected_doc_name}.docx")
    
    with st.expander("📁 Tải xuống tài liệu tham khảo"):
        st.markdown("Bạn có thể tải bộ luật gốc về máy để tham khảo thêm khi cần thiết.")
        # PDF Download
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Tải xuống PDF",
                    data=pdf_file,
                    file_name=f"{selected_doc_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
        # DOCX Download
        if os.path.exists(docx_path):
            with open(docx_path, "rb") as docx_file:
                st.download_button(
                    label="📝 Tải xuống Word (DOCX)",
                    data=docx_file,
                    file_name=f"{selected_doc_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
        if not os.path.exists(pdf_path) and not os.path.exists(docx_path):
            st.warning("⚠️ Không tìm thấy file tài liệu nào trong thư mục data/raw.")

    st.markdown("---")
    st.markdown("### 💡 Hướng dẫn sử dụng")
    st.info(
        "1. Nhập câu hỏi tình huống hoặc pháp lý vào ô chat.\n"
        "2. Đợi AI phân tích và trả lời.\n"
        "3. Xem các **Trích dẫn luật** để đối chiếu với tài liệu gốc."
    )

# Clear chat history when switching docs
if "current_doc" not in st.session_state or st.session_state.current_doc != selected_doc_name:
    st.session_state.current_doc = selected_doc_name
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Xin chào! Tôi là Trợ lý AI chuyên về **{DOCS_MAP[selected_doc_name]}**. Bạn cần tôi giúp gì hôm nay?"
    })

# Helper to render assistant messages with reasoning
def render_assistant_message(content, citations):
    # Try to extract <reasoning> block
    reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', content, re.DOTALL | re.IGNORECASE)
    
    if reasoning_match:
        reasoning_text = reasoning_match.group(1).strip()
        final_answer = re.sub(r'<reasoning>.*?</reasoning>', '', content, flags=re.DOTALL | re.IGNORECASE).strip()
        
        with st.expander("💭 Xem quá trình suy luận của AI (Reasoning)"):
            st.markdown(reasoning_text)
            
        if final_answer:
            st.markdown(final_answer)
        else:
            st.info("⚠️ AI đã vô tình gộp câu trả lời vào bên trong phần suy luận. Vui lòng đọc kết luận ở phần suy luận phía trên.")
    else:
        # Trong trường hợp AI mở thẻ mà không đóng thẻ
        if "<reasoning>" in content.lower():
            content = content.replace("<reasoning>", "").replace("<Reasoning>", "")
            with st.expander("💭 Xem quá trình suy luận của AI (Reasoning)"):
                st.markdown(content)
            st.info("⚠️ AI đã vô tình gộp câu trả lời vào bên trong phần suy luận. Vui lòng đọc kết luận ở phần suy luận phía trên.")
        else:
            st.markdown(content)
        
    if citations:
        with st.expander("📌 Trích dẫn luật chi tiết"):
            for cite in citations:
                st.info(cite)

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_assistant_message(message["content"], message.get("citations", []))
        else:
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Nhập câu hỏi của bạn...", max_chars=500):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Đang tra cứu luật..."):
            try:
                response = requests.post(API_URL, json={
                    "question": prompt, 
                    "k": 15,
                    "doc_name": selected_doc_name,
                    "enable_reasoning": enable_reasoning
                })
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Xin lỗi, tôi không thể tìm thấy câu trả lời.")
                    citations = data.get("verified_citations", [])
                    
                    # Temporarily clear placeholder since render_assistant_message handles markdown
                    message_placeholder.empty()
                    render_assistant_message(answer, citations)
                    
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
