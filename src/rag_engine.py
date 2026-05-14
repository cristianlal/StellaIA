"""
rag_engine.py
Motor RAG para el Tutor Matemático Adaptativo.
"""

import os
from pathlib import Path


class SimpleRAGEngine:

    def __init__(self, knowledge_dir: str = "knowledge_base"):
        self.knowledge_dir = Path(knowledge_dir)
        self.documents = {}
        self._load_documents()

    def _load_documents(self):
        if not self.knowledge_dir.exists():
            raise FileNotFoundError(f"Directorio '{self.knowledge_dir}' no encontrado.")
        for filepath in self.knowledge_dir.glob("*.txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                self.documents[filepath.stem] = f.read()
        print(f"[RAG] Documentos cargados: {list(self.documents.keys())}")

    def _truncar(self, texto: str, max_chars: int = 3000) -> str:
        if len(texto) <= max_chars:
            return texto
        truncado = texto[:max_chars]
        ultimo_salto = truncado.rfind("\n")
        if ultimo_salto > max_chars * 0.8:
            truncado = truncado[:ultimo_salto]
        return truncado + "\n\n[... contenido adicional disponible ...]"

    def retrieve(self, query: str, top_k: int = 1) -> str:
        query_lower = query.lower()
        keyword_map = {
            "suma": ["suma", "sumar", "añadir", "agregar", "más", "adición"],
            "resta": ["resta", "restar", "quitar", "sustraer", "menos", "sustracción"],
            "multiplicacion_division": [
                "multiplicación", "multiplicar", "multiplicacion",
                "división", "dividir", "division", "tabla",
            ],
        }
        scores = {}
        for doc_name, keywords in keyword_map.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[doc_name] = score

        best_doc = max(scores, key=scores.get)

        if scores[best_doc] == 0:
            primer_doc = list(self.documents.values())[0]
            return self._truncar(primer_doc, max_chars=2000)

        contenido = self.documents.get(best_doc, "Información no disponible.")
        return self._truncar(contenido, max_chars=3000)

    def list_topics(self) -> list:
        topic_names = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicacion_division": "Multiplicación y División",
        }
        return [topic_names.get(k, k) for k in self.documents.keys()]
