import json
from pathlib import Path

from src.verification.citation_verifier import CitationVerifier


GENERATOR_SYSTEM_PROMPT = """
Bạn là bộ sinh dữ liệu đánh giá cho hệ thống hỏi đáp về Bộ luật Lao động Việt Nam.
Hãy tạo các câu hỏi ngắn, tự nhiên, đúng nghĩa pháp lý và bám sát nội dung của đoạn luật được cung cấp.

Ưu tiên đa dạng cách hỏi. Với cùng một đoạn luật, các câu hỏi phải khác nhau về cấu trúc:
- câu hỏi định nghĩa
- câu hỏi diễn giải lại
- câu hỏi hỏi ngược / yes-no
- câu hỏi tình huống ngắn
- câu hỏi về điều kiện / nghĩa vụ / quyền

Chỉ trả về JSON hợp lệ, không có markdown, không có giải thích.

Mỗi phần tử trong mảng JSON phải có các khóa:
- category: tên nhóm câu hỏi, ví dụ definition, contract, salary
- question: câu hỏi tiếng Việt
- expected_articles: mảng số điều luật, ví dụ [3]
- citation: chuỗi trích dẫn ngắn, ví dụ "Điều 3 Khoản 1"

Yêu cầu:
- question phải đủ ngắn để dùng làm câu đánh giá.
- Không tạo nhiều câu có cùng một cách diễn đạt; mỗi câu trong cùng một chunk phải khác kiểu hỏi.
- expected_articles phải khớp với nội dung luật trong chunk.
- Nếu không chắc, vẫn ưu tiên trích đúng từ metadata của chunk.
"""


class EvaluationGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.citation_verifier = CitationVerifier()

    def _question_styles(self, n: int) -> list[str]:
        styles = [
            "định nghĩa trực tiếp",
            "diễn giải lại bằng từ khác",
            "hỏi yes/no ngắn gọn",
            "tình huống áp dụng thực tế",
            "hỏi về điều kiện/quyền/nghĩa vụ",
            "hỏi theo cách so sánh/đối chiếu",
        ]
        if n <= len(styles):
            return styles[:n]

        repeated = []
        while len(repeated) < n:
            repeated.extend(styles)
        return repeated[:n]

    def _build_messages(self, chunk, questions_per_chunk: int = 1) -> list[dict]:
        metadata = chunk.metadata or {}
        styles_text = "\n".join(
            f"- Câu {index + 1}: {style}"
            for index, style in enumerate(self._question_styles(questions_per_chunk))
        )
        prompt = f"""
Đoạn luật:
[Citation] {metadata.get('citation', '')}
[Article] {metadata.get('article', '')}
[Clause] {metadata.get('clause', '')}

Nội dung:
{chunk.text}

Hãy tạo {questions_per_chunk} câu hỏi đánh giá bám sát đoạn luật trên.
Mỗi câu phải theo một kiểu hỏi khác nhau theo danh sách sau:
{styles_text}

Ràng buộc:
- Không dùng lại cùng cấu trúc câu hỏi giữa các phần tử.
- Không copy nguyên văn nội dung luật.
- Ưu tiên câu hỏi tự nhiên như người thật hỏi.

Trả về một mảng JSON gồm {questions_per_chunk} phần tử.
"""
        return [
            {
                "role": "system",
                "content": GENERATOR_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

    def _parse_json(self, text: str):
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1)

        return json.loads(cleaned)

    def generate_from_chunks(
        self,
        chunks,
        questions_per_chunk: int = 1,
        limit: int | None = None,
    ) -> list[dict]:
        samples = []
        selected_chunks = chunks if limit is None else chunks[:limit]

        for chunk in selected_chunks:
            response = self.llm.chat(
                self._build_messages(chunk, questions_per_chunk=questions_per_chunk)
            )
            generated = self._parse_json(response)

            if isinstance(generated, dict):
                generated = [generated]

            metadata = chunk.metadata or {}
            for item in generated[:questions_per_chunk]:
                question = item.get("question")
                if not question:
                    continue

                self.citation_verifier.verify_generated_item(item, metadata)

                samples.append({
                    "category": item.get("category", metadata.get("category", "generated")),
                    "question": question,
                    "expected_articles": item.get(
                        "expected_articles",
                        [metadata.get("article")],
                    ),
                    "citation": item.get("citation", metadata.get("citation", "")),
                })

        return samples

    def save(self, samples: list[dict], output_path: str | Path):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(samples, file, ensure_ascii=False, indent=4)