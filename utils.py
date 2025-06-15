import os
import streamlit as st
import extra_streamlit_components as stx

import requests

from requests.exceptions import RequestException

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
TOKEN_VALIDATION_ENDPOINT = "api/v1/authentication/token/verify/"
TOKEN_REFRESH_ENDPOINT = "api/v1/authentication/token/refresh/"

cookie_manager = stx.CookieManager()
cookie_keys = []


def login():
    # st.set_page_config(page_title="Login", page_icon="🔐")
    st.title("🔐 Login")
    remember_me = st.checkbox("Lembrar-me", value=True)
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            auth_tokens = authenticate(username, password)
            if auth_tokens:
                token = auth_tokens.get('access')
                refresh = auth_tokens.get('refresh')

                st.session_state['token'] = token
                st.session_state['refresh_token'] = refresh
                st.session_state['username'] = username
                st.session_state['remember_me'] = remember_me  # Armazena preferência
                st.success("Login realizado com sucesso!")
            else:
                st.error("Credenciais inválidas")
        st.rerun()


# Função para autenticar na API Django
def authenticate(username, password):
    try:
        response = requests.post(
            f"{DJANGO_API_URL}{TOKEN_ENDPOINT}",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            response = response.json()
            return response
        return None
    except RequestException as e:
        st.error(f"Error getting token: {e}")
        return None


def handle_session():
    """Gerencia o estado da sessão e valida o token"""
    if 'token' in st.session_state:
        if not is_token_valid(st.session_state['token']):
            # Se o token for inválido, atualiza o token ou faça logout
            # Se o usuário escolheu lembrar-se, atualize o token
            if st.session_state.get('remember_me'):
                update_token()
            else:
                logout()
            # del st.session_state['token']
            st.rerun()


def logout():
    del st.session_state['token']
    st.navigation(st.Page(login, title="Login", icon=":material/login:"))
    st.rerun()


def is_token_valid(token):
    """Verifica a validade do token consultando o servidor Django."""
    # Validação no servidor: envia o token no corpo da requisição como JSON
    try:
        response = requests.post(
            f"{DJANGO_API_URL}{TOKEN_VALIDATION_ENDPOINT}",
            json={"token": token}  # Enviando o token no formato esperado
        )
        return response.status_code == 200
    except RequestException:
        return False


# update token with refresh token
def update_token():
    """Atualiza o token de autenticação usando o refresh token."""
    if 'token' in st.session_state:
        try:
            update_response = requests.post(
                f"{DJANGO_API_URL}{TOKEN_REFRESH_ENDPOINT}",
                json={"refresh": st.session_state['refresh_token']}
            )
            if update_response.status_code == 200:
                st.session_state['token'] = update_response.json().get('access')
                st.session_state['refresh_token'] = update_response.json().get('refresh')
                st.success("Token atualizado com sucesso!")
            else:
                st.error("Falha ao atualizar o token")
        except RequestException as e:
            st.error(f"Erro ao atualizar o token: {e}")


def create_cliente_link(cpf, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"{base_url}/cliente/{cpf}"


def create_requerimento_link(cpf, id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"{base_url}/requerimento_inicial/{cpf}/{id}"


def create_recurso_link(cpf, id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"{base_url}/requerimento_recurso/{cpf}/{id}"


def create_atendimento_link(cpf, id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"{base_url}/atendimento/{cpf}/{id}"


def create_evento_link(id, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"{base_url}/api/v1/eventos/{id}"


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
