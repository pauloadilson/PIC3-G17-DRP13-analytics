import os
import streamlit as st
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
API_ENDPOINT = "api/v1/clientes/"


# Função para autenticar na API Django
def authenticate(username, password):
    try:
        response = requests.post(
            f"{DJANGO_API_URL}{TOKEN_ENDPOINT}",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json().get('access')
        return None
    except RequestException as e:
        st.error(f"Error getting token: {e}")
        return None


def login():
    st.set_page_config(page_title="Login", page_icon="🔐")
    st.title("🔐 Login")
    remember_me = st.checkbox("Lembrar-me", value=True)
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            token = authenticate(username, password)
            if token:
                st.session_state['token'] = token
                st.session_state['username'] = username
                st.session_state['remember_me'] = remember_me  # Armazena preferência
                st.success("Login realizado com sucesso!")
            else:
                st.error("Credenciais inválidas")
        st.rerun()


def logout():
    del st.session_state['token']
    st.rerun()


login_page = st.Page(login, title="Login", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "relatorios/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
)

clientes = st.Page(
    "relatorios/clientes.py", title="Clientes", icon=":material/dashboard:"
)

atendimentos = st.Page(
    "relatorios/atendimentos.py", title="Atendimentos", icon=":material/dashboard:"
)

requerimentos = st.Page(
    "relatorios/requerimentos_iniciais.py", title="Requerimentos Iniciais", icon=":material/dashboard:"
)

eventos = st.Page(
    "relatorios/eventos.py", title="Eventos", icon=":material/dashboard:"
)


if 'token' in st.session_state:
    pg = st.navigation(
        {
            "Conta": [logout_page],
            "Relatórios": [dashboard, clientes, atendimentos, requerimentos, eventos],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
