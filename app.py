"""
app.py
Interfaz gráfica con Streamlit para el Tutor Virtual Adaptativo.
Ejecutar con: streamlit run app.py
Actualizado para usar google-genai en lugar de google-generativeai.
"""

import streamlit as st
import sys
import os
from pathlib import Path

st.set_page_config(
    page_title="Stella IA — Matemáticas Adaptativas",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #00CFFF; text-align: center; text-shadow: 0px 0px 10px rgba(0,207,255,0.5); }
    .perfil-tdah { background: linear-gradient(135deg, #f093fb, #f5576c);
                   padding: 1rem; border-radius: 10px; color: white; }
    .perfil-autismo { background: linear-gradient(135deg, #4facfe, #00f2fe);
                      padding: 1rem; border-radius: 10px; color: white; }
    .respuesta-box { background: #f8f9fa; border-left: 4px solid #6c63ff;
                     padding: 1.5rem; border-radius: 8px; margin-top: 1rem; }
    .stButton > button { width: 100%; background-color: #6c63ff;
                         color: white; border: none; padding: 0.6rem;
                         border-radius: 8px; font-size: 1rem; }
    .stButton > button:hover { background-color: #5a52e0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")

    api_key = st.text_input(
        "🔑 API Key de Groq",
        type="password",
        placeholder="AIzaSy...",
        help="Obtén tu llave gratuita en https://aistudio.google.com",
    )

    st.markdown("---")
    st.markdown("### 📚 ¿Qué es este tutor?")
    st.info(
        "Sistema RAG + IA que adapta sus explicaciones matemáticas "
        "según el perfil cognitivo del estudiante (TDAH o Autismo)."
    )
    st.markdown("---")
    st.markdown("**📖 Temas disponibles:**")
    st.markdown("- ➕ Suma\n- ➖ Resta\n- ✖️ Multiplicación\n- ➗ División")
    st.markdown("---")
    st.caption("Proyecto Integrador I — UDES 2026")

# ── Título ───────────────────────────────────────────────────────
st.markdown('<p class="main-title">🧮 Stella</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#aaaaaa;">Matemáticas básicas para estudiantes con TDAH y Autismo</p>', unsafe_allow_html=True)
st.markdown("---")

# ── Selección de perfil ──────────────────────────────────────────
perfil_actual = st.session_state.get("perfil", None)

if perfil_actual is None:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎮 TDAH", use_container_width=True):
            st.session_state["perfil"] = "TDAH"
            st.rerun()
    with col2:
        if st.button("🧩 Autismo", use_container_width=True):
            st.session_state["perfil"] = "AUTISMO"
            st.rerun()
    with col3:
        if st.button("📖 General", use_container_width=True):
            st.session_state["perfil"] = "GENERAL"
            st.rerun()
else:
    col_perfil, col_boton = st.columns([4, 1])
    with col_perfil:
        if perfil_actual == "TDAH":
            st.markdown('<div class="perfil-tdah"><strong>🎮 Modo TDAH activado</strong><br>Explicaciones gamificadas, breves y con retos rápidos ⭐</div>', unsafe_allow_html=True)
        elif perfil_actual == "AUTISMO":
            st.markdown('<div class="perfil-autismo"><strong>🧩 Modo Autismo (TEA) activado</strong><br>Explicaciones literales, estructuradas y predecibles 📋</div>', unsafe_allow_html=True)
        elif perfil_actual == "GENERAL":
            st.info("📖 **Modo General activado** — Explicación estándar y didáctica.")
    with col_boton:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Cambiar", use_container_width=True):
            st.session_state["perfil"] = None
            st.session_state["historial"] = []
            st.rerun()

st.markdown("")

# ── Input ────────────────────────────────────────────────────────
pregunta = st.text_area(
    "💬 ¿Qué quieres aprender hoy?",
    placeholder="Ejemplo: Explícame cómo se hace una multiplicación",
    height=100,
)

generar = st.button("✨ Generar explicación", use_container_width=True, type="primary")

if "historial" not in st.session_state:
    st.session_state["historial"] = []

# ── Generación ───────────────────────────────────────────────────
if generar:
    if not api_key:
        st.error("⚠️ Por favor ingresa tu API Key de Gemini en la barra lateral.")
    elif not perfil_actual:
        st.warning("⚠️ Selecciona un perfil primero (TDAH, Autismo o General).")
    elif not pregunta.strip():
        st.warning("⚠️ Escribe una pregunta antes de continuar.")
    else:
        st.session_state["api_key_guardada"] = api_key
        with st.spinner("⏳ Generando respuesta adaptada..."):
            try:
                sys.path.append(str(Path(__file__).parent / "src"))
                from tutor_engine import TutorAdaptativo

                tutor = TutorAdaptativo(api_key=api_key, knowledge_dir="knowledge_base")
                resultado = tutor.responder(perfil=perfil_actual, pregunta=pregunta)

                if resultado.get("error"):
                    st.error(f"❌ {resultado['error']}")
                else:
                    respuesta = resultado["respuesta"]
                    st.markdown("### 📝 Respuesta del Tutor")
                    st.markdown(respuesta)

                    st.session_state["historial"].append({
                        "perfil": perfil_actual,
                        "pregunta": pregunta,
                        "respuesta": respuesta,
                    })
                    # Solo mostrar reto si la respuesta no es un mensaje de error
                    es_error = any(x in respuesta for x in ["⚠️", "🔑", "⏳", "Lo siento", "no estoy diseñado", "API Key"])
                    st.session_state["ultima_respuesta"] = respuesta
                    st.session_state["perfil_reto"] = perfil_actual
                    st.session_state["pregunta_reto"] = pregunta
                    st.session_state["mostrar_reto"] = not es_error



            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ── Sección de Reto Interactivo ──────────────────────────────────
if st.session_state.get("mostrar_reto") and st.session_state.get("ultima_respuesta"):
    st.markdown("---")
    st.markdown("### 🎯 ¡Responde el Reto!")
    st.markdown("Escribe tu respuesta al reto rápido que te dio Stella:")

    respuesta_reto = st.text_input(
        "✏️ Tu respuesta:",
        placeholder="Escribe aquí tu respuesta...",
        key="input_reto"
    )

    if st.button("✅ Verificar respuesta", use_container_width=True):
        if respuesta_reto.strip():
            with st.spinner("⏳ Stella está evaluando tu respuesta..."):
                try:
                    from tutor_engine import TutorAdaptativo
                    tutor_eval = TutorAdaptativo(
                        api_key=st.session_state.get("api_key_guardada", ""),
                        knowledge_dir="knowledge_base"
                    )
                    evaluacion = tutor_eval.evaluar_reto(
                        perfil=st.session_state.get("perfil_reto", "GENERAL"),
                        respuesta_estudiante=respuesta_reto
                    )
                    st.markdown("### 💬 Stella dice:")
                    st.markdown(evaluacion)
                    st.session_state["mostrar_reto"] = False
                except Exception as e:
                    st.error(f"❌ Error al evaluar: {str(e)}")
        else:
            st.warning("⚠️ Escribe tu respuesta antes de verificar.")

# ── Feedback ─────────────────────────────────────────────────────
if st.session_state.get("ultima_respuesta"):
    st.markdown("---")
    st.markdown("**¿Te fue útil esta explicación?**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("👍 Sí, muy útil", use_container_width=True):
            st.success("¡Genial! Sigue practicando 💪")
    with col_b:
        if st.button("👎 Necesito más ayuda", use_container_width=True):
            st.info("No te preocupes, intenta preguntar de otra forma o elige otro tema.")

# ── Historial ────────────────────────────────────────────────────
if st.session_state["historial"]:
    st.markdown("---")
    with st.expander(f"📜 Historial de sesión ({len(st.session_state['historial'])} preguntas)"):
        for i, item in enumerate(reversed(st.session_state["historial"]), 1):
            st.markdown(f"**{i}. [{item['perfil']}]** {item['pregunta']}")
            st.caption(item["respuesta"][:200] + "...")
            st.markdown("---")

