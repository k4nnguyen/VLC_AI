import re 
from src.parsing.base_parser import BaseParser
from src.core.models.chapter import Chapter
from src.core.models.article import Article
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
    
    def parse(self, document: CleanedDocument) -> LegalDocument:
        legal_document = LegalDocument()
        current_chapter = None
        current_article = None
        lines = document.cleaned_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Parse phần chapter
            chapter_match = self.chapter_pattern.match(line)
            if chapter_match:
                roman_number = chapter_match.group(1)
                title = ""
                if i + 1 > len(lines):
                    title = lines[i+1].strip()
                current_chapter = Chapter(number=roman_number, title=title)
                legal_document.chapters.append(current_chapter)
                i += 2
                continue
            
            # Parse phần article
            article_match = self.article_pattern.match(line)
            if article_match:
                article_number = int(article_match.group(1))
                article_title = article_match.group(2).strip()
                current_article = Article(number=article_number,title=article_title,raw_content="")
                if current_chapter is None:
                    current_chapter = Chapter(number="0",title="Unknown")
                    legal_document.chapters.append(current_chapter)
                current_chapter.articles.append(current_article)
                i+=1
                continue
            
            # Content trong phần article
            if current_article is not None:
                if current_article.raw_content:
                    current_article.raw_content += "\n"
                current_article.raw_content += line 
            i+=1
        return legal_document
        