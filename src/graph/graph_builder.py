import networkx as nx 
from src.graph.reference_parser import ReferenceParser
from src.graph.concept_extractor import ConceptExtractor

class KnowledgeGraphBuilder:
    def __init__(self, concept_extractor=None):
        self.graph = nx.DiGraph()
        self.reference_parser = ReferenceParser()
        self.concept_extractor = concept_extractor
    
    def build(self, legal_document):
        # Pass 1: Add all nodes (articles, clauses, points)
        for chapter in legal_document.chapters:
            for article in chapter.articles:
                self._add_article(article)
            for section in chapter.sections:
                for article in section.articles:
                    self._add_article(article)
                    
        # Pass 2: Add all reference edges (REFERS_TO)
        for chapter in legal_document.chapters:
            for article in chapter.articles:
                self._link_article(article)
            for section in chapter.sections:
                for article in section.articles:
                    self._link_article(article)
                    
        return self.graph
    
    def _add_article(self, article):
        article_id = f"article_{article.number}"
        
        # Build full text for article (Title + all clauses content)
        article_text = article.title + "\n"
        if article.clauses:
            for c in article.clauses:
                article_text += c.content + "\n"
                
        self.graph.add_node(
            article_id,
            type="article",
            article=article.number,
            title=article.title,
            citation=f"Điều {article.number}",
            text=article_text.strip(),
            level=1
        )

        # Trích xuất và liên kết Concept (Level 0)
        if self.concept_extractor:
            concepts = self.concept_extractor.extract(article_id, article_text)
            for concept in concepts:
                concept_id = f"concept_{concept.replace(' ', '_')}"
                if not self.graph.has_node(concept_id):
                    self.graph.add_node(
                        concept_id,
                        type="concept",
                        concept=concept,
                        level=0
                    )
                self.graph.add_edge(
                    concept_id,
                    article_id,
                    relation="HAS_ARTICLE",
                    weight=1.0
                )

        for clause in article.clauses:
            clause_id = self._add_clause(clause, article.number)
            self.graph.add_edge(
                article_id,
                clause_id,
                relation="HAS_CLAUSE",
                weight=1.0
            )
    
    def _add_clause(self, clause, article_number):
        clause_id = f"clause_{article_number}_{clause.number}"
        self.graph.add_node(
            clause_id,
            type="clause",
            article=article_number,
            clause=clause.number,
            citation=f"Điều {article_number} Khoản {clause.number}",
            text=clause.content,
            level=2
        )

        for point in clause.points:
            point_id = self._add_point(point, article_number, clause.number)
            self.graph.add_edge(
                clause_id,
                point_id,
                relation="HAS_POINT",
                weight=1.0
            )
        return clause_id

    def _add_point(self, point, article_number, clause_number):
        point_id = f"point_{article_number}_{clause_number}_{point.label}"
        self.graph.add_node(
            point_id,
            type="point",
            article=article_number,
            clause=clause_number,
            point=point.label,
            citation=f"Điều {article_number} Khoản {clause_number} Điểm {point.label}",
            text=point.content,
            level=3
        )

        return point_id

    def _link_article(self, article):
        for clause in article.clauses:
            clause_id = f"clause_{article.number}_{clause.number}"
            refs = self.reference_parser.parse(clause.content)
            for ref in refs:
                if ref["type"] == "article":
                    target = f"article_{ref['article']}"
                    if self.graph.has_node(target):
                        self.graph.add_edge(clause_id, target, relation="REFERS_TO", reference_type="article")
                elif ref["type"] == "clause":
                    target = f"clause_{ref['article']}_{ref['clause']}"
                    if self.graph.has_node(target):
                        self.graph.add_edge(clause_id, target, relation="REFERS_TO", reference_type="clause")
    
    def _add_concepts(self, article):
        article_id = f"article_{article.number}"
        concepts = self.concept_extractor.extract(
            article.title
        )
        for concept in concepts:
            concept_id = (
                "concept_" +
                concept.replace(" ", "_")
            )
            if not self.graph.has_node(concept_id):

                self.graph.add_node(
                    concept_id,
                    type="concept",
                    name=concept,
                    level=0
                )
            self.graph.add_edge(
                article_id,
                concept_id,
                relation="HAS_CONCEPT",
                weight=1.0
            )