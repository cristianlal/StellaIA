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

        # FILTRO DE TEMA — solo responde sobre matemáticas básicas
        temas_validos = [
            "suma", "sumar", "adición", "añadir", "agregar",
            "resta", "restar", "sustracción", "quitar",
            "multiplicación", "multiplicar", "tabla", "producto",
            "división", "dividir", "cociente", "repartir",
            "matemática", "matemáticas", "número", "números",
            "operación", "operaciones", "calcular", "cálculo",
            "más", "menos", "por", "entre", "resultado",
            "ejercicio", "problema", "ecuación", "aritmética"
        ]
        pregunta_lower = pregunta.lower()
        es_tema_valido = any(t in pregunta_lower for t in temas_validos)

        if not es_tema_valido:
            return {
                "perfil": perfil,
                "pregunta": pregunta,
                "respuesta": "⚠️ Solo puedo ayudarte con **suma**, **resta**, **multiplicación** y **división**. Por favor escribe una pregunta sobre estos temas.",
                "fuente_rag": "filtro de tema",
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
                        "content": "Eres Stella, tutora virtual de matemáticas básicas especializada en estudiantes neurodivergentes con TDAH y Autismo. SOLO respondes preguntas sobre suma, resta, multiplicación y división. Si te preguntan algo diferente, responde exactamente: '⚠️ Solo puedo ayudarte con suma, resta, multiplicación y división. Por favor escribe una pregunta sobre estos temas.' Respondes siempre en español."
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

    def evaluar_reto(self, perfil: str, respuesta_estudiante: str, ejercicio: str = "", tema: str = "suma") -> str:
        """Evalúa la respuesta del reto sin pasar por el RAG."""
        
        # Si no tenemos el ejercicio, no podemos evaluar correctamente
        if not ejercicio:
            prompt = f"""Eres Stella, tutora de matemáticas.
El estudiante respondió "{respuesta_estudiante}" a un ejercicio de {tema}.
No tengo el ejercicio exacto pero felicítalo si parece una respuesta numérica válida.
Propón un ejercicio nuevo de {tema} con números pequeños.
Responde en 3 líneas máximo. NO cambies de tema."""
        else:
            prompt = f"""Eres Stella, tutora de matemáticas.

EJERCICIO: {ejercicio}
RESPUESTA DEL ESTUDIANTE: {respuesta_estudiante}
TEMA: {tema}

PASO 1: Resuelve el ejercicio {ejercicio} tú mismo ahora.
PASO 2: Compara con la respuesta del estudiante "{respuesta_estudiante}".
PASO 3: Responde en exactamente 3 líneas:
- LÍNEA 1: Si es correcto: "🏆 ¡Correcto! {ejercicio} = {respuesta_estudiante} es la respuesta correcta." / Si es incorrecto: "❌ Casi lo logras, {ejercicio} = [resultado correcto], no {respuesta_estudiante}."
- LÍNEA 2: Una oración corta de ánimo.
- LÍNEA 3: "Ahora intenta: [nuevo ejercicio de {tema} con números similares] = ?"
IMPORTANTE: Solo usa operaciones de {tema}. Si el tema es suma usa solo +. Si es resta usa solo -."""

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
