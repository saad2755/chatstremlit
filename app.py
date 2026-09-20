# app.py
# Chatbot "Lions de l'Atlas" — Version Streamlit (compatible share.streamlit.io)
# Authentification (inscription / connexion) + chatbot, avec un thème visuel
# aux couleurs du Maroc. Tout le CSS est intégré dans ce fichier (aucun
# dossier "static" ni "templates" n'est nécessaire — Streamlit n'en a pas besoin).

import os
import re
import time
import sqlite3
import hashlib
import secrets
from datetime import datetime

import streamlit as st

from chatbot_engine import get_response

# ============================================================================
# Configuration générale
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

st.set_page_config(
    page_title="Lions de l'Atlas — Chatbot",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# Base de données (SQLite) + hachage sécurisé des mots de passe
# ============================================================================
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hache le mot de passe avec PBKDF2-HMAC-SHA256 et un sel aléatoire.
    Format stocké : "sel_hex$hash_hex". On n'enregistre jamais le mot de
    passe en clair."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 200_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest_hex = stored_hash.split("$")
    except ValueError:
        return False
    check_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 200_000)
    return secrets.compare_digest(check_digest.hex(), digest_hex)


init_db()

# ============================================================================
# Icônes SVG (pas d'icône "cerveau / robot IA" : ballon, stade, joueur)
# ============================================================================
ICON_BALL = """
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="52" height="52">
  <circle cx="24" cy="24" r="21" fill="#ffffff" stroke="#0b3d24" stroke-width="2"/>
  <polygon points="24,14 30,18.5 28,25.5 20,25.5 18,18.5" fill="#0b3d24"/>
  <path d="M24 14 L24 6" stroke="#0b3d24" stroke-width="1.6"/>
  <path d="M30 18.5 L37 15.5" stroke="#0b3d24" stroke-width="1.6"/>
  <path d="M28 25.5 L32 33" stroke="#0b3d24" stroke-width="1.6"/>
  <path d="M20 25.5 L16 33" stroke="#0b3d24" stroke-width="1.6"/>
  <path d="M18 18.5 L11 15.5" stroke="#0b3d24" stroke-width="1.6"/>
</svg>
"""

ICON_PLAYER = """
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="30" height="30">
  <circle cx="24" cy="24" r="24" fill="#C1272D"/>
  <circle cx="24" cy="17" r="6.5" fill="#ffffff"/>
  <path d="M10 39c1-8 6-13 14-13s13 5 14 13" fill="#ffffff"/>
  <path d="M24 26c-3.5 0-6.5 1.2-8.7 3.4l2.2 6.6h13l2.2-6.6C30.5 27.2 27.5 26 24 26z" fill="#006233"/>
</svg>
"""

ICON_STADIUM = """
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="34" height="34">
  <ellipse cx="24" cy="24" rx="22" ry="14" fill="none" stroke="#D4AF37" stroke-width="2.5"/>
  <ellipse cx="24" cy="24" rx="14" ry="7" fill="none" stroke="#D4AF37" stroke-width="2"/>
  <path d="M2 24c0-3 2-6 6-8M46 24c0-3-2-6-6-8M2 24c0 3 2 6 6 8M46 24c0 3-2 6-6 8" stroke="#D4AF37" stroke-width="2" fill="none"/>
</svg>
"""

# ============================================================================
# CSS intégré (thème Maroc : rouge, vert, blanc, touches dorées)
# ============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

:root {
  --red: #C1272D; --red-dark: #8f1c21; --green: #006233; --green-dark: #003d20;
  --gold: #D4AF37; --border: #e4e0d6; --text-muted: #6b7168;
}

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.block-container { max-width: 620px; padding-top: 2rem; }

/* ---- Boutons ---- */
.stButton > button, .stFormSubmitButton > button {
  width: 100%;
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--red), var(--red-dark));
  color: #ffffff;
  transition: transform 0.12s, box-shadow 0.12s;
  box-shadow: 0 4px 14px rgba(193,39,45,0.25);
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(193,39,45,0.32);
  color: #ffffff;
  border: none;
}

/* Boutons secondaires (liens de navigation entre pages) */
button[kind="secondary"] {
  background: transparent !important;
  color: var(--green-dark) !important;
  box-shadow: none !important;
  font-weight: 500 !important;
  text-decoration: underline;
}
button[kind="secondary"]:hover { color: var(--red) !important; transform: none; }

/* ---- Champs texte ---- */
.stTextInput > div > div > input {
  border-radius: 10px !important;
  border: 1.5px solid var(--border) !important;
  padding: 0.55rem 0.8rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(0,98,51,0.12) !important;
}

/* ---- Carte d'authentification ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 16px !important;
  border-top: 4px solid var(--red) !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  padding: 0.5rem;
}

.brand-title { text-align: center; color: var(--green-dark); font-weight: 700; font-size: 1.4rem; margin: 6px 0 0; }
.brand-tagline { text-align: center; color: var(--text-muted); font-size: 0.85rem; margin: 0 0 18px; }
.auth-title { text-align: center; font-size: 1.15rem; margin: 4px 0 16px; }
.footer-note { text-align: center; font-size: 0.85rem; color: var(--text-muted); margin-top: 10px; }

/* ---- En-tête du chat ---- */
.chat-header {
  background: linear-gradient(120deg, var(--green-dark), var(--green));
  color: #ffffff;
  padding: 14px 20px;
  border-radius: 14px;
  border-bottom: 3px solid var(--gold);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.chat-header h1 { margin: 0; font-size: 1.1rem; }
.chat-header p { margin: 0; font-size: 0.78rem; opacity: 0.85; }

/* ---- Bulles de messages ---- */
.msg-row { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 12px; max-width: 88%; }
.msg-row.user { margin-left: auto; flex-direction: row-reverse; }
.msg-avatar { flex-shrink: 0; width: 30px; height: 30px; border-radius: 50%; overflow: hidden; }
.msg-avatar.user-avatar {
  background: var(--gold); color: #fff; display: flex; align-items: center;
  justify-content: center; font-size: 0.78rem; font-weight: 700;
}
.msg-bubble { padding: 10px 14px; border-radius: 16px; font-size: 0.92rem; line-height: 1.45; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
.msg-row.bot .msg-bubble { background: #ffffff; border: 1px solid var(--border); border-bottom-left-radius: 4px; }
.msg-row.user .msg-bubble { background: linear-gradient(135deg, var(--green), var(--green-dark)); color: #fff; border-bottom-right-radius: 4px; }
.msg-time { display: block; font-size: 0.68rem; margin-top: 4px; opacity: 0.65; }

[data-testid="stChatInput"] textarea { border-radius: 20px !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# État de session
# ============================================================================
if "view" not in st.session_state:
    st.session_state.view = "login"  # login | register | forgot | chat
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []  # liste de (role, texte, heure)


def go_to(view: str):
    st.session_state.view = view


def logout():
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.messages = []
    st.session_state.view = "login"


# Si connecté, on force l'affichage du chat même si "view" pointait ailleurs
if st.session_state.user_id and st.session_state.view in ("login", "register", "forgot"):
    st.session_state.view = "chat"


# ============================================================================
# En-tête de marque (utilisé sur les pages d'authentification)
# ============================================================================
def brand_header():
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom: 8px;">{ICON_BALL}</div>
        <p class="brand-title">Lions de l'Atlas</p>
        <p class="brand-tagline">Le chatbot des supporters marocains</p>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# Page : Connexion
# ============================================================================
def render_login():
    brand_header()
    with st.container(border=True):
        st.markdown('<p class="auth-title">Connexion</p>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Adresse e-mail", placeholder="vous@exemple.com")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            remember_me = st.checkbox("Se souvenir de moi")
            submitted = st.form_submit_button("Se connecter")

        if submitted:
            errors = []
            email_clean = email.strip().lower()
            if not EMAIL_REGEX.match(email_clean):
                errors.append("Adresse e-mail invalide.")
            if not password:
                errors.append("Veuillez saisir votre mot de passe.")

            user = None
            if not errors:
                conn = get_connection()
                user = conn.execute("SELECT * FROM users WHERE email = ?", (email_clean,)).fetchone()
                conn.close()
                if not user or not verify_password(password, user["password_hash"]):
                    errors.append("E-mail ou mot de passe incorrect.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["full_name"]
                st.session_state.view = "chat"
                st.session_state.messages = []
                st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            st.button("Mot de passe oublié ?", key="go_forgot", type="secondary", on_click=go_to, args=("forgot",))
        with col2:
            st.button("Créer un compte", key="go_register", type="secondary", on_click=go_to, args=("register",))

    st.markdown(
        '<p class="footer-note">Remarque : la session reste active tant que cet onglet '
        'du navigateur reste ouvert (limite technique de Streamlit).</p>',
        unsafe_allow_html=True,
    )


# ============================================================================
# Page : Inscription
# ============================================================================
def render_register():
    brand_header()
    with st.container(border=True):
        st.markdown('<p class="auth-title">Créer un compte</p>', unsafe_allow_html=True)

        with st.form("register_form"):
            full_name = st.text_input("Nom complet", placeholder="Votre nom complet")
            email = st.text_input("Adresse e-mail", placeholder="vous@exemple.com")
            password = st.text_input("Mot de passe", type="password", placeholder="8 caractères minimum")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password", placeholder="Répétez le mot de passe")
            submitted = st.form_submit_button("Créer mon compte")

        if submitted:
            errors = []
            full_name_clean = full_name.strip()
            email_clean = email.strip().lower()

            if len(full_name_clean) < 2:
                errors.append("Le nom complet doit contenir au moins 2 caractères.")
            if not EMAIL_REGEX.match(email_clean):
                errors.append("Adresse e-mail invalide.")
            if len(password) < 8:
                errors.append("Le mot de passe doit contenir au moins 8 caractères.")
            if password != confirm_password:
                errors.append("Les mots de passe ne correspondent pas.")

            if not errors:
                conn = get_connection()
                existing = conn.execute("SELECT id FROM users WHERE email = ?", (email_clean,)).fetchone()
                if existing:
                    errors.append("Un compte existe déjà avec cet e-mail.")
                conn.close()

            if errors:
                for e in errors:
                    st.error(e)
            else:
                conn = get_connection()
                conn.execute(
                    "INSERT INTO users (full_name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    (full_name_clean, email_clean, hash_password(password), datetime.utcnow().isoformat()),
                )
                conn.commit()
                conn.close()
                st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                time.sleep(1.1)
                go_to("login")
                st.rerun()

        st.button("← Déjà un compte ? Se connecter", key="go_login_from_register", type="secondary", on_click=go_to, args=("login",))


# ============================================================================
# Page : Mot de passe oublié
# ============================================================================
def render_forgot():
    brand_header()
    with st.container(border=True):
        st.markdown('<p class="auth-title">Mot de passe oublié</p>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center; color:#6b7168; font-size:0.88rem;">'
            "Saisissez votre adresse e-mail, nous vous enverrons un lien pour "
            "réinitialiser votre mot de passe.</p>",
            unsafe_allow_html=True,
        )
        with st.form("forgot_form"):
            email = st.text_input("Adresse e-mail", placeholder="vous@exemple.com")
            submitted = st.form_submit_button("Envoyer le lien")

        if submitted:
            if EMAIL_REGEX.match(email.strip().lower()):
                # En production : envoyer un vrai e-mail avec un lien de réinitialisation.
                st.success(
                    "Si un compte existe avec cette adresse, un lien de "
                    "réinitialisation vient de lui être envoyé."
                )
            else:
                st.error("Adresse e-mail invalide.")

        st.button("← Retour à la connexion", key="go_login_from_forgot", type="secondary", on_click=go_to, args=("login",))


# ============================================================================
# Page : Chatbot (protégée)
# ============================================================================
def render_chat():
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(
            f"""
            <div class="chat-header">
                {ICON_STADIUM}
                <div>
                    <h1>Lions de l'Atlas</h1>
                    <p>Bonjour, {st.session_state.user_name} 👋</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.button("↺", key="restart_btn", help="Recommencer la conversation",
                       on_click=lambda: st.session_state.update(messages=[]))
        with c2:
            st.button("⏻", key="logout_btn", help="Se déconnecter", on_click=logout)

    # Message de bienvenue au premier affichage
    if not st.session_state.messages:
        st.session_state.messages.append(("bot", "Salut ! Je suis le chatbot des Lions de l'Atlas 🦁. "
                                                    "Pose-moi une question sur les joueurs, les matchs ou "
                                                    "l'histoire de l'équipe nationale marocaine !",
                                           datetime.now().strftime("%H:%M")))

    messages_container = st.container()
    with messages_container:
        for role, text, ts in st.session_state.messages:
            if role == "user":
                st.markdown(
                    f"""
                    <div class="msg-row user">
                        <div class="msg-avatar user-avatar">Moi</div>
                        <div class="msg-bubble">{text}<span class="msg-time">{ts}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="msg-row bot">
                        <div class="msg-avatar">{ICON_PLAYER}</div>
                        <div class="msg-bubble">{text}<span class="msg-time">{ts}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    user_text = st.chat_input("Écrivez votre question sur les Lions de l'Atlas...")
    if user_text:
        now = datetime.now().strftime("%H:%M")
        st.session_state.messages.append(("user", user_text, now))
        with st.spinner("Le chatbot répond..."):
            time.sleep(0.5)  # petite pause pour un rendu plus naturel
            reply = get_response(user_text)
        st.session_state.messages.append(("bot", reply, datetime.now().strftime("%H:%M")))
        st.rerun()


# ============================================================================
# Routage principal
# ============================================================================
if st.session_state.view == "chat" and st.session_state.user_id:
    render_chat()
elif st.session_state.view == "register":
    render_register()
elif st.session_state.view == "forgot":
    render_forgot()
else:
    render_login()
