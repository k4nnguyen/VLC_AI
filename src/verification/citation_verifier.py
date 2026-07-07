import re


class CitationVerifier:
    CITE_PATTERN = re.compile(r"Điều\s+\d+(?:\s+Khoản\s+\d+)?", re.IGNORECASE)

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
            raise ValueError("Answer does not contain any citations.")

        allowed = {self._normalize(citation) for citation in allowed_citations}
        invalid = extracted - allowed
        if invalid:
            raise ValueError(
                "Answer contains citations not present in retrieved context: "
                + ", ".join(sorted(invalid))
            )

        return extracted

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