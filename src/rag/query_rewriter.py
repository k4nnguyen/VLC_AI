class QueryRewriter:
    def __init__(self, llm):
        self.llm = llm

    def rewrite(self, question: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là bộ viết lại truy vấn cho hệ thống truy hồi văn bản luật. "
                    "Nhiệm vụ của bạn là viết lại câu hỏi của người dùng thành một truy vấn ngắn, "
                    "rõ nghĩa, giữ nguyên ý định pháp lý, tối ưu cho tìm kiếm tài liệu. "
                    "Không trả lời câu hỏi. Không thêm giải thích. Chỉ trả về đúng một câu truy vấn đã viết lại."
                ),
            },
            {
                "role": "user",
                "content": f"Câu hỏi gốc: {question}",
            },
        ]

        rewritten = self.llm.chat(messages).strip()
        rewritten = rewritten.strip("\"'")
        if not rewritten:
            raise ValueError("Query rewrite returned an empty string.")
        return rewritten