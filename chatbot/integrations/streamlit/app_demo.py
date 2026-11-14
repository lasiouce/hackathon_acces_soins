"""Application Streamlit de démonstration : uv run --group streamlit streamlit run integrations/streamlit/app_demo.py"""
import streamlit as st

from chatbot_streamlit import afficher_chatbot

st.set_page_config(page_title="Jumeau de l'offre de soins", page_icon="💬", layout="wide")
afficher_chatbot()
