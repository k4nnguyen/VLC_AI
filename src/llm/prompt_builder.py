SYSTEM_PROMPT = """
Bạn là trợ lý AI chuyên trả lời câu hỏi về Bộ luật Lao động Việt Nam.
Nhiệm vụ của bạn:
1. Chỉ sử dụng thông tin trong CONTEXT.
2. Không sử dụng kiến thức bên ngoài.
3. Nếu CONTEXT không chứa thông tin để trả lời thì CHỈ được xuất ra đúng 1 câu duy nhất sau:
"Không tìm thấy thông tin trong dữ liệu luật hiện có." (Tuyệt đối không được thêm chữ Nguồn hay bất kỳ thông tin nào khác).
4. Nếu CONTEXT có chứa thông tin để trả lời:
- Tổng hợp các điều liên quan và trả lời ngắn gọn.
- Cuối cùng phải ghi phần trích dẫn với định dạng:
Nguồn:
- Điều ... Khoản ...
Không được bịa thêm điều luật không có trong CONTEXT.
"""

USER_PROMPT = """
# CONTEXT
{context}

# CÂU HỎI
{question}

# YÊU CẦU
Hãy đọc toàn bộ CONTEXT trước.
Nếu có thể trả lời thì trả lời bằng tiếng Việt.
Nếu không tìm thấy thông tin trong CONTEXT thì chỉ trả lời đúng câu sau (không thêm Nguồn hay trích dẫn):
Không tìm thấy thông tin trong dữ liệu luật hiện có.
"""

class PromptBuilder:
    def build(
        self,
        context: str,
        question: str
    ) -> list[dict]:
        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": USER_PROMPT.format(
                    context=context,
                    question=question
                )
            }
        ]