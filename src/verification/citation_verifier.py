import re


class CitationVerifier:
    CITE_PATTERN = re.compile(r"Điều\s+\d+(?:\s+Khoản\s+\d+)?(?:\s+Điểm\s+[a-z]+(?:,\s*[a-z]+)*)?", re.IGNORECASE)

    def _normalize(self, citation: str) -> str:
        return re.sub(r"\s+", " ", citation).strip().lower()

    def extract_citations(self, text: str) -> set[str]:
        return {
            self._normalize(match.group(0))
            for match in self.CITE_PATTERN.finditer(text or "")
        }

    def verify_answer(self, answer: str, allowed_citations: set[str]) -> set[str]:
        extracted = self.extract_citations(answer)
        if not extracted:
            return set()

        # Map normalized allowed citations to their original casing
        allowed_map = {self._normalize(cite): cite for cite in allowed_citations}
        allowed_normalized = set(allowed_map.keys())

        valid_extracted = set()

        # Helper to get base citation (e.g., "điều 98 khoản 1" from "điều 98 khoản 1 điểm a, b")
        def get_base(cite: str) -> str:
            return re.sub(r"\s+điểm\s+.*", "", cite)

        for ext in extracted:
            ext_base = get_base(ext)
            for alw in allowed_normalized:
                alw_base = get_base(alw)
                # If the base matches (e.g. both are Điều 98 Khoản 1), we consider it a valid hit for that allowed citation
                if ext_base == alw_base:
                    valid_extracted.add(allowed_map[alw])

        return valid_extracted

    def verify_generated_item(self, item: dict, chunk_metadata: dict) -> None:
        expected_citation = self._normalize(str(chunk_metadata.get("citation", "")))
        item_citation = self._normalize(str(item.get("citation", "")))

        if not expected_citation:
            raise ValueError("Chunk metadata is missing citation.")

        if item_citation != expected_citation:
            raise ValueError(
                f"Generated citation mismatch: expected '{expected_citation}', got '{item_citation}'."
            )

        expected_article = chunk_metadata.get("article")
        expected_articles = item.get("expected_articles") or []
        if expected_article is not None and expected_article not in expected_articles:
            raise ValueError(
                f"Generated expected_articles does not include article {expected_article}."
            )