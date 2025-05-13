import streamlit as st
from utils import handle_session, login, logout


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

recursos = st.Page(
    "relatorios/recursos.py", title="Recursos", icon=":material/dashboard:"
)

eventos = st.Page(
    "relatorios/eventos.py", title="Eventos", icon=":material/dashboard:"
)

if 'token' in st.session_state:
    pg = st.navigation(
        {
            "Conta": [logout_page],
            "Relatórios": [dashboard, clientes, atendimentos, requerimentos, recursos, eventos],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
handle_session()
