# VLC AI - Hệ Thống Trợ Lý Ảo Pháp Luật Việt Nam (Multi-Domain RAG)

Dự án này là một hệ thống Hỏi Đáp thông minh (RAG - Retrieval-Augmented Generation) chuyên biệt cho Pháp luật Việt Nam, hiện đang hỗ trợ đa tên miền (Multi-Domain): **Bộ Luật Lao Động** và **Luật Giao Thông**. 

Hệ thống ứng dụng các kỹ thuật tiên tiến nhất hiện nay như Hybrid Retrieval (Vector + BM25), Graph RAG (Knowledge Graph), Query Rewriting (dịch từ lóng), Semantic Caching, và Chain-of-Thought (CoT) Reasoning để đưa ra các tư vấn pháp lý chính xác và chặn đứng hiện tượng "bịa luật" (Hallucination).

## 🌟 Các Tính Năng Nổi Bật
1. **Multi-Domain Knowledge**: Hỗ trợ tra cứu chéo hoặc độc lập giữa nhiều bộ luật khác nhau thông qua cơ chế phân luồng dữ liệu chuẩn xác.
2. **Graph RAG (Knowledge Graph)**: Trích xuất và xây dựng Đồ thị Tri thức để liên kết các Điều/Khoản có tính chất "tham chiếu chéo" hoặc "loại trừ" (Ví dụ: "Phạt 500k trừ các trường hợp quy định tại điểm c khoản 7").
3. **Intelligent Query Rewriting**: Tự động nhận diện và phiên dịch "từ lóng" của người dùng thành "thuật ngữ pháp lý" (Ví dụ: "vượt đèn đỏ" -> "không chấp hành hiệu lệnh của đèn tín hiệu", "thổi nồng độ cồn" -> "trong máu có nồng độ cồn") nhằm tối ưu hóa công cụ tìm kiếm.
4. **Chain-of-Thought (CoT) Reasoning**: Ép buộc LLM phải suy luận theo từng bước, đối chiếu đối tượng, phân tích các khoản loại trừ, và rẽ nhánh điều kiện trước khi đưa ra kết luận. Có nút Bật/Tắt tính năng suy luận trên UI.
5. **Semantic Caching**: Lưu trữ các câu trả lời dựa trên độ tương đồng ngữ nghĩa (Cosine Similarity), giúp giảm 90% độ trễ (latency) và tiết kiệm token OpenAI cho các câu hỏi trùng lặp, hỗ trợ phân tách Cache theo cấu hình người dùng.

## ⚙️ Kiến Trúc Hệ Thống (Pipeline)
1. **Document Parsers & Chunkers**: Phân tách file `*.docx` thành cấu trúc phân cấp (Chương, Mục, Điều, Khoản, Điểm) để bảo toàn ngữ cảnh pháp lý.
2. **Hybrid Retriever (RRF)**: Sử dụng phương pháp Reciprocal Rank Fusion kết hợp giữa:
   - **Vector Retriever**: Mô hình `multilingual-e5-small` qua ChromaDB.
   - **BM25 Retriever**: Phân tích từ khóa truyền thống (Lexical Search).
3. **Graph Expansion**: Retriever mở rộng tập kết quả bằng cách duyệt qua đồ thị tri thức để lấy các điều khoản tham chiếu ẩn.
4. **LLM Generation**: Sử dụng OpenAI LLM với Prompt Chain chặt chẽ, luôn có thẻ `<reasoning>` để suy luận và kết xuất trích dẫn minh bạch.

## 📊 Kết Quả Đánh Giá (Evaluation)
Hệ thống được đánh giá tự động trên bộ **270 câu hỏi test** đa tên miền (`evaluations/evaluate.py`), đo lường khả năng truy xuất chính xác điều luật ở **Top-5 (k=5)**.

| Phương Pháp (Retriever) | Recall@5 | Hit Rate (Success) | MRR |
|-------------------------|----------|---------------------|----------------|
| **BM25 (Từ khóa)** | ~90.74% | 245 / 270 | 0.783 |
| **Vector (Embeddings)** | 92.22% | 249 / 270 | 0.839 |
| **Hybrid RRF (Kết hợp)** | **95.93%** | **259 / 270** | **0.818** |

*Thuật toán Hybrid RRF kết hợp với Heuristic Scoring đã bắt được tới 259 câu, đạt độ chính xác lên đến 95.93% trên nhiều tập luật khác nhau.*

## 🚀 Cài Đặt & Chạy Ứng Dụng

**1. Khởi tạo Database (ChromaDB + BM25 + Knowledge Graph)**
```bash
python db_init.py
```

**2. Chạy Backend API (FastAPI)**
```bash
cd web
fastapi dev api.py
```

**3. Chạy Giao Diện Người Dùng (Streamlit)**
```bash
cd web
streamlit run app.py
```
