"""
tutor_engine.py
Motor principal del tutor adaptativo. Integra el RAG con Groq API.
"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from groq import Groq
from rag_engine import SimpleRAGEngine
from prompt_builder import build_prompt

class TutorAdaptativo:
    PERFILES_VALIDOS = ["TDAH", "AUTISMO", "GENERAL"]

    def __init__(self, api_key: str, knowledge_dir: str = "knowledge_base"):
        self.client = Groq(api_key=api_key)
        self.model_id = "llama-3.3-70b-versatile"
        self.rag = SimpleRAGEngine(knowledge_dir=knowledge_dir)
        print("[Tutor] Sistema inicializado con Groq ✓")

    def responder(self, perfil: str, pregunta: str) -> dict:
        perfil = perfil.upper().strip()
        if perfil not in self.PERFILES_VALIDOS:
            return {
                "error": f"Perfil '{perfil}' no válido. Usa: {self.PERFILES_VALIDOS}",
                "respuesta": None,
            }

        contexto_rag = self.rag.retrieve(query=pregunta)
        prompt_final = build_prompt(
            perfil=perfil,
            pregunta=pregunta,
            contexto_rag=contexto_rag,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un tutor virtual de matemáticas especializado en estudiantes neurodivergentes con TDAH y Autismo. Respondes siempre en español."
                    },
                    {
                        "role": "user",
                        "content": prompt_final
                    }
                ],
                temperature=0.4,
                max_tokens=2048,
            )
            respuesta_texto = response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "413" in error_str or "too large" in error_str:
                respuesta_texto = "⚠️ Lo siento, no estoy diseñado para responder esa pregunta. Por favor escribe un tema de matemáticas básicas como: **suma**, **resta**, **multiplicación** o **división**."
            elif "401" in error_str or "invalid_api_key" in error_str:
                respuesta_texto = "🔑 La API Key no es válida. Por favor verifica tu clave en la barra lateral."
            elif "429" in error_str or "rate_limit" in error_str:
                respuesta_texto = "⏳ Demasiadas consultas seguidas. Espera un momento e intenta de nuevo."
            else:
                respuesta_texto = "⚠️ Lo siento, no estoy diseñado para responder esa pregunta. Por favor escribe un tema de matemáticas básicas como: **suma**, **resta**, **multiplicación** o **división**."

        return {
            "perfil": perfil,
            "pregunta": pregunta,
            "respuesta": respuesta_texto,
            "fuente_rag": "base de conocimiento interna",
        }

    def evaluar_reto(self, perfil: str, respuesta_estudiante: str) -> str:
        """Evalúa la respuesta del reto sin pasar por el RAG."""
        prompt = f"""Eres Stella, tutora de matemáticas. El estudiante respondió el Reto Rápido con: "{respuesta_estudiante}"

Responde en exactamente 3 líneas:
1. Si es correcto: "🏆 ¡Correcto! Tienes el Reto Rápido correcto." / Si es incorrecto: "❌ Casi lo logras, la respuesta correcta es [respuesta] porque [razón breve]."
2. Una oración corta de ánimo.
3. Un nuevo ejercicio: "Ahora intenta: [ejercicio sencillo]"
Sin explicaciones largas ni estrategias."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres Stella, tutora virtual de matemáticas. Respondes siempre en español de forma breve y motivadora."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            return "⏳ No pude evaluar tu respuesta en este momento. Intenta de nuevo."

    def temas_disponibles(self) -> list:
        return self.rag.list_topics()
