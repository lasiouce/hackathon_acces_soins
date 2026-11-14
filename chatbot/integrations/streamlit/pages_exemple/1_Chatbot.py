"""Page « Chatbot » prête à copier dans le dossier pages/ d'une application Streamlit multipage."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # chatbot_streamlit.py est dans le dossier parent
from chatbot_streamlit import afficher_chatbot  # noqa: E402

st.set_page_config(page_title="Chatbot du jumeau", page_icon="💬", layout="wide")
afficher_chatbot()
