import json
from pathlib import Path

CONCEPT_PROMPT = """
Bạn là một chuyên gia pháp lý. Hãy đọc nội dung điều luật dưới đây và trích xuất ra từ 2 đến 4 khái niệm (concepts/keywords) trọng tâm nhất.
Các concept phải là những cụm danh từ ngắn gọn, phổ biến trong ngành luật (vd: "hợp đồng lao động", "thời gian thử việc", "sa thải", "tiền lương").
CHỈ TRẢ VỀ ĐÚNG MỘT MẢNG JSON CÁC CHUỖI, tuyệt đối không giải thích gì thêm, không thêm markdown.
Ví dụ đầu ra chuẩn: ["tiền lương", "làm thêm giờ", "làm việc ban đêm"]

Nội dung Điều luật:
{text}
"""

class ConceptExtractor:
    def __init__(self, llm, cache_file="data/processed/concepts_cache.json"):
        self.llm = llm
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def extract(self, article_id: str, text: str) -> list[str]:
        # Nếu đã extract rồi thì lấy từ cache cho nhanh và không tốn tiền API
        if article_id in self.cache:
            return self.cache[article_id]

        messages = [
            {"role": "system", "content": "You are a strict data extractor that only outputs valid JSON arrays of strings."},
            {"role": "user", "content": CONCEPT_PROMPT.format(text=text)}
        ]

        try:
            print(f"Đang gọi LLM trích xuất concept cho {article_id}...")
            response = self.llm.chat(messages).strip()
            import time
            time.sleep(1) 
            
            # Xử lý text LLM trả về để lấy chuẩn JSON (đề phòng có dấu ```json)
            if response.startswith("```"):
                response = response.strip("`").replace("json\n", "", 1).strip()
                
            concepts = json.loads(response)
            
            # Chuẩn hóa về chữ thường để tránh trùng lặp "Thai sản" vs "thai sản"
            clean_concepts = [str(c).lower().strip() for c in concepts]
            
            self.cache[article_id] = clean_concepts
            self._save_cache()
            return clean_concepts
            
        except Exception as e:
            print(f"[!] Lỗi khi extract concept cho {article_id}: {e}")
            return []