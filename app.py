import streamlit as st
from utils import fetch_resource, handle_session, login, logout

st.set_page_config(page_title="Análise de Dados - CPPREV",
                   page_icon="static/images/favicon.png",
                   layout="wide")

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
    # Verificar nível de acesso (adicionar esta parte)
    user_info = fetch_resource("api/v1/user-info/", st.session_state['token'])
    if user_info and 'role' in user_info:
        st.session_state['user_role'] = user_info['role']

    # Verificar se tem acesso (adicionar esta verificação)
    if st.session_state.get('user_role') not in ['admin', 'Advogados']:
        st.error("Acesso restrito. Você não tem permissão para visualizar este conteúdo.")
        if st.button("Voltar"):
            del st.session_state['token']
            st.rerun()
        st.stop()  # Impede a execução do restante do código

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
