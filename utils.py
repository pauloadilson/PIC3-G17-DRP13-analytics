import os
import streamlit as st
import requests

# Verifica se está no Heroku (usando variáveis de ambiente) ou local (usando secrets.toml)
if 'DYNO' in os.environ:  # Verifica se está rodando no Heroku
    DJANGO_API_URL = os.environ.get('DJANGO_API_URL')
    DJANGO_USERNAME = os.environ.get('DJANGO_API_USERNAME')
    DJANGO_PASSWORD = os.environ.get('DJANGO_API_PASSWORD')
else:  # Modo de desenvolvimento local
    DJANGO_API_URL = st.secrets["django_api"]["api_url"]
    DJANGO_USERNAME = st.secrets["django_api"]["username"]
    DJANGO_PASSWORD = st.secrets["django_api"]["password"]

TOKEN_ENDPOINT = "api/v1/authentication/token/"


def create_cliente_link(cpf, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"[{id}]({base_url}/cliente/{cpf})"


def create_requerimento_link(cpf, id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"[{id}]({base_url}/requerimento-inicial/{cpf}/{id})"


def create_atendimento_link(cpf, id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"<a>{base_url}/atendimento/{cpf}/{id}</a>"


def create_evento_link(id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"<a>{base_url}/api/v1/eventos/{id}</a>"


@st.cache_data(ttl=600)  # Cache por 10 minutos
def fetch_resource(endpoint, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{DJANGO_API_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None
