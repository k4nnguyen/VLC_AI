import re 

class ReferenceParser:
    ARTICLE_PATTERN = re.compile(r"Điều\s+(\d+)", flags=re.IGNORECASE)
    CLAUSE_PATTERN = re.compile(r"Khoản\s+(\d+)\s+Điều\s+(\d+)", flags=re.IGNORECASE)

    def parse(self, text:str):
        references = []
        if not text:
            return references

        # Khoản x Điều y
        for clause, article in self.CLAUSE_PATTERN.findall(text):
            references.append({
                "type": "clause",
                "article": int(article),
                "clause": int(clause)
            })

        # Xóa các cụm "Khoản x Điều y" đã tìm thấy để tránh trùng lặp khi tìm "Điều y"
        text_without_clauses = self.CLAUSE_PATTERN.sub("", text)

        # Điều y (chỉ bắt các Điều y đứng độc lập)
        for article in self.ARTICLE_PATTERN.findall(text_without_clauses):
            references.append({
                "type": "article",
                "article": int(article)
            })

        return references