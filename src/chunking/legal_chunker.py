from src.chunking.base_chunker import BaseChunker
from src.core.models.chunk import Chunk
from src.core.models.legal_document import LegalDocument

class LegalChunker(BaseChunker):
    def chunk(self, document: LegalDocument) -> list[Chunk]:
        chunks = []
        for chapter in document.chapters:
            # Article trực tiếp trong Chapter
            for article in chapter.articles:
                chunks.extend(
                    self._chunk_article(
                        article,
                        chapter.number,
                        None
                    )
                )

            # Article trong Section
            for section in chapter.sections:
                for article in section.articles:
                    chunks.extend(
                        self._chunk_article(
                            article,
                            chapter.number,
                            section.number
                        )
                    )
        return chunks

    def _chunk_article(self,article,chapter_number,section_number) -> list[Chunk]:
        chunks = []
        for clause in article.clauses:
            text = (
                f"Điều {article.number}. {article.title}\n\n"
                f"Khoản {clause.number}\n"
                f"{clause.content}"
            )
            chunk = Chunk(
                chunk_id=f"BLLD2019_{article.number}_{clause.number}",
                text=text,
                metadata={
                    "law": "BLLD2019",
                    "chapter": chapter_number,
                    "section": section_number,
                    "article": article.number,
                    "clause": clause.number,
                    "title": article.title,
                    "citation": f"Điều {article.number} Khoản {clause.number}"
                }
            )
            chunks.append(chunk)
        return chunks