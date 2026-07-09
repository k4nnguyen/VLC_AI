import networkx as nx

class GraphRetriever:
    """
    Kết hợp Vector/BM25 Retriever với Knowledge Graph để mở rộng ngữ cảnh (Graph Expansion).
    """
    def __init__(self, base_retriever, graph: nx.DiGraph):
        self.base_retriever = base_retriever
        self.graph = graph

    def _get_node_by_citation(self, citation: str):
        # Duyệt đồ thị để tìm node tương ứng với citation (Ví dụ: "Điều 14 Khoản 2")
        for node, data in self.graph.nodes(data=True):
            if data.get("citation") == citation:
                return node
        return None

    def retrieve(self, question: str, k: int = 5):
        # 1. Tìm kiếm ban đầu bằng Vector + BM25 (HybridRRF)
        results = self.base_retriever.retrieve(question, k=k)
        
        expanded_docs = []
        expanded_metas = []
        seen_citations = set()
        
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        
        for doc, meta in zip(docs, metas):
            citation = meta.get("citation")
            if not citation or citation in seen_citations:
                continue
                
            # Thêm Node gốc (Entry Point) vào kết quả
            expanded_docs.append(doc)
            expanded_metas.append(meta)
            seen_citations.add(citation)
            
            node_id = self._get_node_by_citation(citation)
            if not node_id:
                continue
                
            # 2. Graph Expansion: Nhảy theo các cạnh
            
            # A. Lấy các tham chiếu chéo (REFERS_TO)
            for target_id in self.graph.successors(node_id):
                edge_data = self.graph.get_edge_data(node_id, target_id)
                if edge_data and edge_data.get("relation") == "REFERS_TO":
                    target_node = self.graph.nodes[target_id]
                    target_citation = target_node.get("citation")
                    if target_citation and target_citation not in seen_citations:
                        # Thêm văn bản được tham chiếu chéo vào ngữ cảnh
                        expanded_docs.append(f"[THAM CHIẾU TỪ {citation}]:\n{target_node.get('text', '')}")
                        expanded_metas.append({"citation": target_citation, "type": "reference"})
                        seen_citations.add(target_citation)
            
            # B. Đi lùi lên Node cha (HAS_CLAUSE, HAS_POINT) để cung cấp bức tranh toàn cảnh
            for parent_id in self.graph.predecessors(node_id):
                edge_data = self.graph.get_edge_data(parent_id, node_id)
                if edge_data and edge_data.get("relation") in ["HAS_CLAUSE", "HAS_POINT"]:
                    parent_node = self.graph.nodes[parent_id]
                    parent_citation = parent_node.get("citation")
                    if parent_citation and parent_citation not in seen_citations:
                        # Thêm bối cảnh của Điều luật chứa Khoản này
                        expanded_docs.append(f"[BỐI CẢNH CỦA {citation}]:\n{parent_node.get('text', '')}")
                        expanded_metas.append({"citation": parent_citation, "type": "context"})
                        seen_citations.add(parent_citation)
                        
            # C. Đi ngược về Concept (HAS_ARTICLE) - Tuỳ chọn nếu cần thiết
            # (Bạn có thể thêm logic leo lên Concept ở đây)

        return {
            "documents": [expanded_docs],
            "metadatas": [expanded_metas]
        }
