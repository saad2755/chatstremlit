# 🦁 Chatbot Lions de l'Atlas — Version Streamlit (compatible share.streamlit.io)

Chatbot consacré à l'équipe nationale marocaine de football, avec système
d'inscription/connexion et interface moderne aux couleurs du Maroc — **cette
version est une vraie application Streamlit**, déployable directement sur
`share.streamlit.io`.

---

## 1. Arborescence du projet (3 fichiers, aucun dossier)

```
lions-atlas-chatbot/
├── app.py               # Application Streamlit complète (pages, auth, CSS intégré)
├── chatbot_engine.py     # Logique du chatbot (règles NLTK, reprises de Chat.py)
└── requirements.txt      # Dépendances (streamlit + nltk)
```

`database.db` (SQLite) est créé automatiquement au premier lancement.

---

## 2. Pourquoi cette version et pas la version Flask ?

`share.streamlit.io` ne sait déployer que des scripts qui utilisent
`import streamlit as st` : c'est le seul framework qu'il sait exécuter. La
version Flask précédente ne peut donc pas fonctionner sur cette plateforme
— cette version-ci a été réécrite spécifiquement pour Streamlit, en gardant
les mêmes fonctionnalités (connexion, inscription, chatbot stylé).

---

## 3. Déploiement sur share.streamlit.io

1. Poussez les 3 fichiers (`app.py`, `chatbot_engine.py`, `requirements.txt`)
   à la racine de votre dépôt GitHub (`saad2755/chatbot` par exemple), sur
   la branche `main`.
2. Sur la page de déploiement (`https://share.streamlit.io/deploy`) :
   - **Branch** : `main`
   - **Main file path** : choisissez **`app.py`** (c'est le point d'entrée ;
     ne choisissez jamais `chatbot_engine.py`, qui n'est qu'un module importé).
3. Cliquez sur **Deploy**.

---

## 4. Lancer en local (avant de déployer, pour tester)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Ouvrez ensuite l'adresse indiquée dans le terminal (en général
`http://localhost:8501`).

---

## 5. Explication simple (pour un étudiant débutant)

### Comment fonctionne une application Streamlit ?

Contrairement à Flask, Streamlit **réexécute tout le script `app.py` de haut
en bas** à chaque interaction (clic sur un bouton, saisie d'un champ...).
Il n'y a pas de vraies "routes" comme `/login` ou `/chat` : on simule
plusieurs pages avec une variable `st.session_state.view` (qui vaut
`"login"`, `"register"`, `"forgot"` ou `"chat"`), et on affiche le contenu
correspondant à chaque exécution :

```python
if st.session_state.view == "chat":
    render_chat()
elif st.session_state.view == "register":
    render_register()
...
```

`st.session_state` est un dictionnaire qui **survit** entre deux exécutions
du script (tant que l'onglet du navigateur reste ouvert) — c'est ce qui
remplace les "sessions" de Flask.

### Comment les mots de passe sont protégés ?

Comme dans la version précédente, on ne stocke **jamais** le mot de passe en
clair. Ici, `hash_password()` utilise `PBKDF2-HMAC-SHA256` (une fonction de
hachage lente et répétée 200 000 fois, ce qui rend les attaques par force
brute beaucoup plus difficiles) combinée à un sel aléatoire unique par
utilisateur. `verify_password()` recalcule ce hachage à la connexion et le
compare à celui stocké en base — sans jamais avoir besoin de connaître le
mot de passe original.

### Comment le chatbot répond ?

`chatbot_engine.py` reprend exactement la logique du fichier `Chat.py`
d'origine : une liste de règles (regex → réponse), interprétée par
`nltk.chat.util.Chat`. Quand vous tapez un message dans `st.chat_input()`,
`app.py` appelle `get_response()`, ajoute la réponse à
`st.session_state.messages`, puis relance le script — ce qui réaffiche la
conversation avec le nouveau message.

---

## 6. Limites techniques propres à Streamlit (à connaître)

- **"Se souvenir de moi"** : Streamlit ne propose pas de vrais cookies
  persistants sans bibliothèque tierce. La session reste active tant que
  l'onglet reste ouvert, mais elle est perdue si vous fermez l'onglet ou
  rechargez complètement la page (F5). La case à cocher est présente pour
  l'expérience utilisateur, mais ne prolonge pas la session au-delà de ça.
- **Base de données éphémère sur Streamlit Cloud** : sur l'offre gratuite,
  le fichier `database.db` peut être réinitialisé lorsque l'application
  redémarre (mise en veille après inactivité, redéploiement...). Pour une
  vraie mise en production avec des comptes qui durent dans le temps, il
  est recommandé d'utiliser une base de données externe persistante (par
  exemple Supabase, Neon ou une base Postgres managée) plutôt que SQLite.
- **Afficher/masquer le mot de passe** (icône 👁) n'est pas disponible
  nativement avec les champs `st.text_input(type="password")` de Streamlit,
  contrairement à la version HTML/JS précédente ; cette fonctionnalité a
  donc été retirée dans cette version.

---

## 7. Points de sécurité déjà en place

- ✅ Mots de passe hachés avec sel aléatoire (PBKDF2-HMAC-SHA256, 200 000 itérations).
- ✅ Page chatbot affichée uniquement si `st.session_state.user_id` est défini.
- ✅ Validation des champs (format e-mail, longueur du mot de passe, confirmation).
- ✅ Aucune clé API dans le code (et aucune clé API n'est utilisée ici).

## 8. Pistes d'amélioration possibles

- Remplacer SQLite par une base de données externe persistante pour la production.
- Ajouter un vrai envoi d'e-mail pour "mot de passe oublié".
- Sauvegarder l'historique des conversations par utilisateur en base de données.
- Ajouter une limitation du nombre de tentatives de connexion (anti brute-force).
