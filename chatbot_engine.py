# chatbot_engine.py
# Logique du chatbot "Lions de l'Atlas", extraite et conservée telle quelle
# depuis le fichier Chat.py original (basée sur nltk.chat.util).

from nltk.chat.util import Chat, reflections

PAIRS = [
    [r"mon nom est (.*)", ["Hello %1, bienvenue fan des Lions de l'Atlas !"]],
    [r"bonjour|salut|coucou", ["Salut toi, prêt à parler des Lions de l'Atlas ?", "Hello, supporter du Maroc ?"]],
    [r"(.*)surnom(.*)équipe(.*)", ["L'équipe nationale du Maroc est surnommée les Lions de l'Atlas"]],
    [r"(.*)entraineur|(.*)sélectionneur(.*)", ["Le sélectionneur du Maroc est Walid Regragui"]],
    [r"(.*)capitaine(.*)", ["Le capitaine des Lions de l'Atlas est Romain Saïss"]],
    [r"(.*)gardien(.*)", ["Yassine Bounou (Bono) est le gardien emblématique du Maroc"]],
    [r"(.*)hakimi(.*)", ["Achraf Hakimi est le latéral droit du Maroc, il joue au PSG"]],
    [r"(.*)ziyech(.*)", ["Hakim Ziyech est un milieu offensif talentueux des Lions de l'Atlas"]],
    [r"(.*)coupe du monde 2022|(.*)qatar(.*)", ["Le Maroc a atteint les demi-finales de la Coupe du Monde 2022, une première pour l'Afrique !"]],
    [r"(.*)demi.finale(.*)", ["Oui ! Le Maroc est la première équipe africaine à atteindre les demi-finales d'une Coupe du Monde en 2022"]],
    [r"(.*)espagne(.*)", ["Le Maroc a éliminé l'Espagne aux tirs au but en huitièmes de finale du Mondial 2022"]],
    [r"(.*)portugal(.*)", ["Le Maroc a battu le Portugal 1-0 en quarts de finale du Mondial 2022, but de Youssef En-Nesyri"]],
    [r"(.*)can(.*)gagné|(.*)coupe d'afrique(.*)", ["Le Maroc a remporté la CAN en 1976"]],
    [r"(.*)stade(.*)", ["Les Lions de l'Atlas jouent souvent au Complexe Mohammed V à Casablanca et au Grand Stade de Rabat"]],
    [r"(.*)maillot|(.*)couleurs(.*)", ["Les couleurs du Maroc sont le rouge et le vert"]],
    [r"(.*)en.nesyri(.*)", ["Youssef En-Nesyri est l'attaquant du Maroc, célèbre pour son but de la tête contre le Portugal"]],
    [r"(.*)coupe du monde 2030(.*)", ["Le Maroc organisera la Coupe du Monde 2030 avec l'Espagne et le Portugal"]],
    [r"(.*)meilleur joueur(.*)", ["C'est subjectif, mais Achraf Hakimi et Hakim Ziyech sont parmi les meilleurs"]],
    [r"merci(.*)", ["De rien ! Dima Maghrib !"]],
    [r"au revoir|bye|quitter", ["Au revoir ! Dima Maghrib 🇲🇦"]],
    [r"(.*)", ["Je ne comprends pas, pose-moi une question sur les Lions de l'Atlas"]],
]

_chat = Chat(PAIRS, reflections)


def get_response(message: str) -> str:
    """Retourne la réponse du chatbot pour un message utilisateur donné."""
    if not message or not message.strip():
        return "Pose-moi une question sur les Lions de l'Atlas !"
    response = _chat.respond(message.strip())
    return response or "Je ne comprends pas, pose-moi une question sur les Lions de l'Atlas"
