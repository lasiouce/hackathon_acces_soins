# Intégrer le chatbot dans une application Streamlit

Le composant appelle l'API HTTP du chatbot (`POST /api/chat`) : l'application Streamlit n'importe ni le modèle ni
l'IA, n'a besoin d'aucune clé, et les garde-fous (lecture seule, vérification des nombres, périmètre) restent
côté chatbot.

1. Lancer le chatbot (dépôt jumeau-chat) : `scripts/lancer.sh`, qui écoute sur http://localhost:8768.
2. Dans votre application, copier `chatbot_streamlit.py`, puis au choix :
   - dans une page existante :
     ```python
     from chatbot_streamlit import afficher_chatbot
     afficher_chatbot()
     ```
   - comme page dédiée d'une application multipage : copier `pages_exemple/1_Chatbot.py` dans `pages/`.
3. Si le chatbot tourne ailleurs : `CHATBOT_URL=http://hote:8768 streamlit run app.py`.

Dépendances de votre application : `streamlit` (altair, pandas et requests sont fournis avec).
`afficher_chatbot(cle="autre")` isole l'historique si le composant apparaît sur plusieurs pages.

Démonstration autonome : `uv run --group streamlit streamlit run integrations/streamlit/app_demo.py`.
