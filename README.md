# VLC AI - Hệ Thống Trợ Lý Ảo Pháp Luật (Bộ Luật Lao Động)

Dự án này là một hệ thống Hỏi Đáp thông minh (RAG - Retrieval-Augmented Generation) chuyên biệt cho Bộ Luật Lao Động Việt Nam. Hệ thống sử dụng kết hợp giữa tìm kiếm ngữ nghĩa (Semantic Search - Vector Embeddings) và tìm kiếm từ khóa (BM25) để truy xuất chính xác các điều khoản pháp luật, sau đó dùng Large Language Model (LLM) để tổng hợp và trả lời cho người dùng.

## Kiến Trúc Hệ Thống (RAG Pipeline)
Hệ thống được xây dựng với các thành phần chính:
1. **Document Parsers & Chunkers**: Phân tách file `lao_dong.docx` thành cấu trúc phân cấp (Chương, Mục, Điều, Khoản, Điểm) để chia nhỏ (chunk) thành các đơn vị tra cứu hợp lý.
2. **Hybrid Retriever (RRF)**: Sử dụng phương pháp Reciprocal Rank Fusion kết hợp giữa:
   - **Vector Retriever**: `multilingual-e5-small` qua ChromaDB.
   - **BM25 Retriever**: Phân tích từ khóa truyền thống.
   - *Heuristic Reranking*: Tăng 20% điểm cho các văn bản tìm thấy ở cả 2 bên, và 10% cho các văn bản chỉ tìm thấy bằng Vector để tối ưu thứ hạng.
3. **Query Preprocessor**: Xử lý câu hỏi người dùng (chuẩn hóa, xóa khoảng trắng thừa) và ánh xạ từ điển đồng nghĩa (Synonyms) như "bầu bí" -> "thai sản", "đuổi việc" -> "sa thải"... để tăng độ bắt dính của BM25.
4. **LLM Generation**: OpenAI LLM dựa trên `prompt_builder` chặt chẽ để chống Hallucination (tuyệt đối không bịa luật) và tự động xuất trích dẫn kèm toàn văn điều khoản.

## Kết Quả Đánh Giá (Evaluation Results)

Hệ thống được đánh giá tự động trên bộ 120 câu hỏi test (`evaluations/evaluate.py`), đo lường khả năng truy xuất chính xác điều luật ở **Top-5 (k=5)**.

| Phương Pháp (Retriever) | Recall@5 | Hit Rate (Success) | MRR (Mean Reciprocal Rank) |
|-------------------------|----------|---------------------|----------------------------|
| **BM25 (Từ khóa)** | ~76.67% | 92 / 120 | - |
| **Vector (Embeddings)** | 90.00% | 108 / 120 | 0.805 |
| **Hybrid RRF (Kết hợp)** | **91.67%** | **110 / 120** | **0.786** |

### Phân tích chi tiết:
- Tổng số câu hỏi: **120**
- Số câu chỉ Vector tìm thấy (BM25 trượt): **18**
- Số câu chỉ BM25 tìm thấy (Vector trượt): **2**
- Trượt cả 2 bên: **10**
- Thuật toán **Hybrid RRF** kết hợp với **Heuristic Scoring** đã bắt được **toàn bộ 110 câu** mà ít nhất 1 trong 2 thuật toán tìm thấy. Điều này chứng minh sức mạnh của mô hình lai so với việc chỉ dùng 1 phương pháp đơn lẻ.

## Cài Đặt & Chạy Ứng Dụng

**1. Khởi tạo Database (ChromaDB + BM25)**
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
