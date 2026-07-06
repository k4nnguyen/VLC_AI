import re 
from src.parsing.base_parser import BaseParser
from src.core.models.chapter import Chapter
from src.core.models.article import Article
from src.core.models.section import Section
from src.core.models.legal_document import LegalDocument
from src.core.models.cleaned_document import CleanedDocument
class StructureParser(BaseParser):
    chapter_pattern = re.compile(
        r"^CHƯƠNG\s+([IVXLCDM]+)\s*$",
        re.IGNORECASE
    )

    article_pattern = re.compile(
        r"^Điều\s+(\d+)\.\s*(.*)$",
        re.IGNORECASE
    )
    
    section_pattern = re.compile(
    r"^Mục\s+(\d+)\.?\s*$",
    re.IGNORECASE
)
    def parse(self, document: CleanedDocument) -> LegalDocument:
        legal_document = LegalDocument()
        current_chapter = None
        current_article = None
        current_section = None
        lines = document.cleaned_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Chapter
            chapter, consumed = self._parse_chapter(
                lines, i
            )
            if chapter:
                legal_document.chapters.append(chapter)
                current_chapter = chapter
                current_section = None
                current_article = None
                i += consumed
                continue
            
            # Section
            section, consumed = self._parse_section(
                lines, i
            )
            if section:
                current_section = section
                current_article = None
                if current_chapter:
                    current_chapter.sections.append(section)
                i += consumed
                continue
            
            # Article
            article, consumed = self._parse_article(
                line
            )
            if article:
                current_article = article
                if current_section:
                    current_section.articles.append(article)
                elif current_chapter:
                    current_chapter.articles.append(article)
                i += consumed
                continue
            
            # Content
            self._append_content(
                current_article,
                line
            )
            i+=1
        return legal_document
    
    def _parse_chapter(self, lines, index):
        match = self.chapter_pattern.match(
            lines[index].strip()
        )
        if not match:
            return None, 0
        number = match.group(1)
        title = ""
        if index + 1 < len(lines):
            title = lines[index + 1].strip()
        chapter = Chapter(
            number=number,
            title=title
        )
        return chapter, 2
    
    def _parse_section(self, lines, index):
        match = self.section_pattern.match(
            lines[index].strip()
        )
        if not match:
            return None, 0
        number = int(match.group(1))
        title = ""
        if index + 1 < len(lines):
            title = lines[index + 1].strip()
        section = Section(
            number=number,
            title=title
        )
        return section, 2
    
    def _parse_article(self, line):
        match = self.article_pattern.match(line)
        if not match:
            return None, 0
        article = Article(
            number=int(match.group(1)),
            title=match.group(2).strip(),
            raw_content=""
        )
        return article, 1
    def _append_content(self,article,line):
        if article is None:
            return
        if article.raw_content:
            article.raw_content += "\n"
        article.raw_content += line