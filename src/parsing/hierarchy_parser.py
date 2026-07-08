import re
from src.core.models.legal_document import LegalDocument
from src.core.models.article import Article
from src.core.models.clause import Clause
from src.core.models.point import Point
SKIP_ARTICLES = {219}
class HierarchyParser:
    CLAUSE_PATTERN = re.compile(r"^(\d+)\.\s*(.*)$")
    POINT_PATTERN = re.compile(r"^([a-z])\)\s*(.*)$")
    def parse(self, document: LegalDocument) -> LegalDocument:
        for chapter in document.chapters:
            # Article nằm trực tiếp trong Chapter
            for article in chapter.articles:
                self._parse_article(article)
                
            # Article nằm trong Section
            for section in chapter.sections:
                for article in section.articles:
                    self._parse_article(article)
        return document

    def _parse_article(self, article: Article):
        if article.number in SKIP_ARTICLES:
            return
        article.clauses.clear()
        current_clause = None
        for line in article.raw_content.splitlines():
            line = line.strip()
            if not line:
                continue

            # Clause
            clause_match = self.CLAUSE_PATTERN.match(line)
            if clause_match:
                current_clause = Clause(
                    number=int(clause_match.group(1)),
                    content=clause_match.group(2).strip()
                )
                article.clauses.append(current_clause)
                continue

            # If there's no current_clause yet, we just encountered text (e.g. an unnumbered article).
            if not current_clause:
                current_clause = Clause(number=0, content="")
                article.clauses.append(current_clause)

            # Point
            point_match = self.POINT_PATTERN.match(line)
            if point_match:
                current_clause.points.append(
                    Point(
                        label=point_match.group(1),
                        content=point_match.group(2).strip()
                    )
                )
                continue

            # Multi-line
            if current_clause.points:
                current_clause.points[-1].content += "\n" + line
            else:
                current_clause.content += "\n" + line