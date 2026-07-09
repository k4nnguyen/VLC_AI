import networkx as nx
from pathlib import Path
from src.graph.graph_builder import KnowledgeGraphBuilder
from src.loaders.docx_loader import DocxLoader
from src.cleaners.text_cleaner import TextCleaner
from src.parsing.structure_parser import StructureParser
from src.parsing.hierarchy_parser import HierarchyParser

# 1. Parse the document
loader = DocxLoader()
raw_doc = loader.load(Path("data/raw/lao_dong.docx"))
clean_doc = TextCleaner().clean(raw_doc)
legal_doc = StructureParser().parse(clean_doc)
legal_document = HierarchyParser().parse(legal_doc)

# 2. Build the Knowledge Graph
builder = KnowledgeGraphBuilder()
graph = builder.build(legal_document)

import matplotlib.pyplot as plt

print(f"Number of nodes: {graph.number_of_nodes()}")
print(f"Number of edges: {graph.number_of_edges()}")

# Vẽ đồ thị
# nx.draw(graph, node_size=10)
# plt.show()

print("\n--- Test Metadata của Nodes (Ví dụ: Điều 98) ---")
import json
try:
    print("\n[LEVEL 1 - ARTICLE]")
    print(json.dumps(graph.nodes["article_98"], ensure_ascii=False, indent=2))
    
    print("\n[LEVEL 2 - CLAUSE]")
    print(json.dumps(graph.nodes["clause_98_1"], ensure_ascii=False, indent=2))
    
    print("\n[LEVEL 3 - POINT]")
    print(json.dumps(graph.nodes["point_98_1_c"], ensure_ascii=False, indent=2))
    
    print("\n[EDGES FROM ARTICLE 98]")
    edges = graph.out_edges("article_98", data=True)
    for u, v, d in edges:
        print(f"{u} -> {v} (Relation: {d['relation']}, Weight: {d.get('weight')})")
        
except KeyError as e:
    print(f"Lỗi: Không tìm thấy node {e} trong đồ thị.")