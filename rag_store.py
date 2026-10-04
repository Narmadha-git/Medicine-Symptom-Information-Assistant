"""
RAG Knowledge Base retriever using TF-IDF & Cosine Similarity / Keyword Matching.
Loads WHO fact sheets and patient leaflets for verified factual health guidance.
"""

from typing import List, Dict, Any
import re
import math
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data.health_data import WHO_FACT_SHEETS

class HealthRAGStore:
    def __init__(self):
        self.documents = WHO_FACT_SHEETS

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant health documents based on term overlap and relevance score.
        """
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return []

        scored_docs = []
        for doc in self.documents:
            doc_text = f"{doc['title']} {doc['topic']} {doc['content']}"
            doc_tokens = self._tokenize(doc_text)
            
            # Simple keyword overlap scoring
            matches = sum(1 for token in query_tokens if token in doc_tokens)
            if matches > 0:
                score = matches / (math.log(len(doc_tokens) + 1) + 1)
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

rag_store = HealthRAGStore()

if __name__ == "__main__":
    print("Testing RAG Store...")
    results = rag_store.search("blood pressure antihypertensive ibuprofen")
    for r in results:
        print(f"Title: {r['title']}")
