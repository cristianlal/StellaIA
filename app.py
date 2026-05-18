"""
app.py
Interfaz gráfica con Streamlit para Stella - Tutor Virtual Adaptativo.
"""

import streamlit as st
import sys
import os
import re
from pathlib import Path

st.set_page_config(
    page_title="Stella — Tutor Matemático",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Sistema de Login ──────────────────────────────────────────────
def check_login():
    if "usuarios_db" not in st.session_state:
        st.session_state["usuarios_db"] = {}

    if not st.session_state.get("logged_in"):
        st.markdown("""
        <div style='text-align:center; padding: 40px;'>
            <h1 style='color:#00CFFF; font-size:2.5rem;'>🧮 Stella</h1>
            <p style='color:#aaaaaa; font-size:1.1rem;'>Tutor Virtual Adaptativo de Matemáticas</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab_login, tab_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])

            with tab_login:
                usuario = st.text_input("👤 Usuario:", placeholder="Tu usuario", key="login_user")
                contrasena = st.text_input("🔑 Contraseña:", type="password", placeholder="Tu contraseña", key="login_pass")
                if st.button("Entrar →", use_container_width=True, key="btn_login"):
                    if usuario and contrasena:
                        db = st.session_state["usuarios_db"]
                        if usuario in db and db[usuario] == contrasena:
                            st.session_state["logged_in"] = True
                            st.session_state["usuario_actual"] = usuario
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                    else:
                        st.warning("⚠️ Escribe tu usuario y contraseña.")

            with tab_registro:
                nuevo_usuario = st.text_input("👤 Nuevo usuario:", placeholder="Solo letras y números, mín. 3 caracteres", key="reg_user")
                nueva_contrasena = st.text_input("🔑 Contraseña:", type="password", placeholder="Mín. 6 caracteres con letras y números", key="reg_pass")
                confirmar = st.text_input("🔑 Confirmar contraseña:", type="password", placeholder="Repite la contraseña", key="reg_confirm")
                st.caption("ℹ️ Usuario: solo letras y números, sin espacios. Contraseña: mínimo 6 caracteres con letras y números.")

                if st.button("Crear cuenta →", use_container_width=True, key="btn_registro"):
                    u = nuevo_usuario.strip()
                    c = nueva_contrasena.strip()
                    cf = confirmar.strip()

                    if not u or not c or not cf:
                        st.warning("⚠️ Por favor completa todos los campos.")
                    elif len(u) < 3:
                        st.error("❌ El usuario debe tener al menos 3 caracteres.")
                    elif not re.match(r"^[a-zA-Z0-9_]+$", u):
                        st.error("❌ El usuario solo puede tener letras, números y guión bajo. Sin espacios.")
                    elif len(c) < 6:
                        st.error("❌ La contraseña debe tener al menos 6 caracteres.")
                    elif not any(ch.isalpha() for ch in c):
                        st.error("❌ La contraseña debe tener al menos una letra.")
                    elif not any(ch.isdigit() for ch in c):
                        st.error("❌ La contraseña debe tener al menos un número.")
                    elif c != cf:
                        st.error("❌ Las contraseñas no coinciden.")
                    elif u in st.session_state["usuarios_db"]:
                        st.error("❌ Ese usuario ya existe, elige otro.")
                    else:
                        st.session_state["usuarios_db"][u] = c
                        st.session_state["logged_in"] = True
                        st.session_state["usuario_actual"] = u
                        st.success(f"✅ ¡Bienvenido {u}!")
                        st.rerun()
        st.stop()

check_login()

# ── Estilos ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #00CFFF; text-align: center; text-shadow: 0px 0px 10px rgba(0,207,255,0.5); }
    .perfil-tdah { background: linear-gradient(135deg, #f093fb, #f5576c); padding: 1rem; border-radius: 10px; color: white; }
    .perfil-autismo { background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 1rem; border-radius: 10px; color: white; }
    .stButton > button { width: 100%; background-color: #6c63ff; color: white; border: none; padding: 0.6rem; border-radius: 8px; font-size: 1rem; }
    .stButton > button:hover { background-color: #5a52e0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    usuario_actual = st.session_state.get("usuario_actual", "Usuario")
    st.markdown(f"👤 **{usuario_actual}**")
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["usuario_actual"] = None
        st.rerun()
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")

    api_key_secret = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
    if api_key_secret:
        api_key = api_key_secret
        st.success("🔑 API Key cargada")
    else:
        api_key = st.text_input(
            "🔑 Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Obtén tu API key en console.groq.com",
        )

    st.markdown("---")
    st.markdown("### 📚 ¿Qué es este tutor?")
    st.info("Sistema RAG + IA que adapta sus explicaciones matemáticas según el perfil cognitivo del estudiante.")
    st.markdown("---")
    st.markdown("**📖 Temas disponibles:**")
    st.markdown("- ➕ Suma\n- ➖ Resta\n- ✖️ Multiplicación\n- ➗ División")
    st.markdown("---")
    st.caption("Proyecto Integrador — UDES 2026")

# ── Título ────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🧮 Stella</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#aaaaaa;">Matemáticas básicas para estudiantes con TDAH y Autismo</p>', unsafe_allow_html=True)
st.markdown("---")

# ── Selección de perfil ───────────────────────────────────────────
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

# ── Input ─────────────────────────────────────────────────────────
pregunta = st.text_area(
    "💬 ¿Qué quieres aprender hoy?",
    placeholder="Ejemplo: Explícame cómo se hace una multiplicación",
    height=100,
)

generar = st.button("✨ Generar explicación", use_container_width=True, type="primary")

if "historial" not in st.session_state:
    st.session_state["historial"] = []

# ── Generación ────────────────────────────────────────────────────
if generar:
    if not api_key:
        st.error("⚠️ Por favor ingresa tu Groq API Key en la barra lateral.")
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

                    es_error = any(x in respuesta for x in ["⚠️", "🔑", "⏳", "Lo siento", "no estoy diseñado", "API Key"])

                    # Extraer ejercicio del reto
                    ejercicio_encontrado = ""
                    lineas_resp = respuesta.splitlines()
                    for linea in reversed(lineas_resp):
                        if any(x in linea for x in ["Reto", "reto", "⭐", "intenta", "Intenta"]):
                            m = re.search(r"(\d+\s*[\+\-\*x\/]\s*\d+)", linea)
                            if m:
                                ejercicio_encontrado = m.group(0).strip()
                                break

                    st.session_state["ultima_respuesta"] = respuesta
                    st.session_state["perfil_reto"] = perfil_actual
                    st.session_state["pregunta_reto"] = pregunta
                    st.session_state["ejercicio_reto"] = ejercicio_encontrado
                    st.session_state["tema_reto"] = pregunta.lower()
                    st.session_state["mostrar_reto"] = not es_error
                    st.session_state["historial_reto"] = []
                    st.session_state["reto_contador"] = 0

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ── Reto Interactivo ──────────────────────────────────────────────
if st.session_state.get("mostrar_reto") and st.session_state.get("ultima_respuesta"):
    st.markdown("---")
    st.markdown("### 🎯 ¡Responde el Reto!")

    if st.session_state.get("historial_reto"):
        for item in st.session_state["historial_reto"]:
            st.markdown(f"**Tu respuesta:** `{item['respuesta']}`")
            st.markdown(item["evaluacion"])
            st.markdown("---")

    st.markdown("✏️ Escribe tu respuesta:")
    with st.form(key=f"form_reto_{st.session_state.get('reto_contador', 0)}", clear_on_submit=True):
        respuesta_reto = st.text_input(
            "Tu respuesta:",
            placeholder="Escribe aquí tu respuesta...",
            label_visibility="collapsed"
        )
        verificar = st.form_submit_button("✅ Verificar respuesta", use_container_width=True)

    if verificar:
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
                        respuesta_estudiante=respuesta_reto,
                        ejercicio=st.session_state.get("ejercicio_reto", ""),
                        tema=st.session_state.get("tema_reto", "suma")
                    )
                    if "historial_reto" not in st.session_state:
                        st.session_state["historial_reto"] = []
                    st.session_state["historial_reto"].append({
                        "respuesta": respuesta_reto,
                        "evaluacion": evaluacion
                    })
                    # Extraer nuevo ejercicio
                    nuevo_ejercicio = ""
                    for linea in evaluacion.splitlines():
                        if any(x in linea for x in ["Ahora intenta", "intenta", "Intenta"]):
                            m = re.search(r"(\d+\s*[\+\-\*x\/]\s*\d+)", linea)
                            if m:
                                nuevo_ejercicio = m.group(0).strip()
                                break
                    if nuevo_ejercicio:
                        st.session_state["ejercicio_reto"] = nuevo_ejercicio
                    st.session_state["reto_contador"] = st.session_state.get("reto_contador", 0) + 1
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al evaluar: {str(e)}")
        else:
            st.warning("⚠️ Escribe tu respuesta antes de verificar.")

# ── Feedback ──────────────────────────────────────────────────────
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

# ── Historial ─────────────────────────────────────────────────────
if st.session_state.get("historial"):
    st.markdown("---")
    with st.expander(f"📜 Historial de sesión ({len(st.session_state['historial'])} preguntas)"):
        for i, item in enumerate(reversed(st.session_state["historial"]), 1):
            st.markdown(f"**{i}. [{item['perfil']}]** {item['pregunta']}")
            st.caption(item["respuesta"][:200] + "...")
            st.markdown("---")
