"""
rag_engine.py
Motor RAG (Retrieval-Augmented Generation) para el Tutor Matemático Adaptativo.
Carga la base de conocimiento y recupera fragmentos relevantes para enriquecer el prompt.
"""

import os
import re
from pathlib import Path


class SimpleRAGEngine:
    """
    Motor RAG simplificado basado en búsqueda por palabras clave.
    En producción, reemplazar con FAISS + embeddings de LangChain.
    """

    def __init__(self, knowledge_dir: str = "knowledge_base"):
        self.knowledge_dir = Path(knowledge_dir)
        self.documents = {}
        self._load_documents()

    def _load_documents(self):
        """Carga todos los archivos .txt de la base de conocimiento."""
        if not self.knowledge_dir.exists():
            raise FileNotFoundError(f"Directorio '{self.knowledge_dir}' no encontrado.")

        for filepath in self.knowledge_dir.glob("*.txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                self.documents[filepath.stem] = f.read()

        print(f"[RAG] Documentos cargados: {list(self.documents.keys())}")

    def retrieve(self, query: str, top_k: int = 1) -> str:
        """
        Recupera el fragmento más relevante de la base de conocimiento.
        Estrategia: busca por palabras clave del tema en el nombre del documento.
        """
        query_lower = query.lower()

        # Mapa de palabras clave a documentos
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

        # Ordenar por score y obtener el mejor
        best_doc = max(scores, key=scores.get)

        # Si ninguna coincide, devolver todos los documentos resumidos
        if scores[best_doc] == 0:
            return "\n\n---\n\n".join(self.documents.values())

        return self.documents.get(best_doc, "Información no disponible.")

    def list_topics(self) -> list:
        """Retorna la lista de temas disponibles."""
        topic_names = {
            "suma": "Suma",
            "resta": "Resta",
            "multiplicacion_division": "Multiplicación y División",
        }
        return [topic_names.get(k, k) for k in self.documents.keys()]