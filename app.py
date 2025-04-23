import os
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

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


def create_requerimento_link(cpf, protocolo, base_url="https://cpprev-dev-09ed70033bf7.herokuapp.com"):
    return f"[{protocolo}]({base_url}/requerimento-inicial/{cpf}/{protocolo})"


def main():
    # Configuração da página
    st.set_page_config(
        page_title="Análise de Dados - CPPREV",
        page_icon="static/images/favicon.png",
        layout="wide"
    )

    # Barra lateral com formulário de login
    with st.sidebar:
        st.markdown("[Voltar para o CPPREV](https://cpprev-dev-09ed70033bf7.herokuapp.com/)")
        st.title("🔐 Login")

        if 'token' not in st.session_state:
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
        else:
            st.success(f"Logado como {st.session_state.get('username', 'usuário')}")
            if st.button("Logout"):
                del st.session_state['token']
                st.rerun()

    # Se autenticado, mostrar dados
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

        # Título
        st.title("Análise de Clientes, Atendimentos e Requerimentos Iniciais")

        # Buscar dados da API Django
        df_clientes = fetch_resource("api/v1/clientes/", st.session_state['token'])
        df_clientes = pd.DataFrame(df_clientes)
        df_atendimentos = fetch_resource("api/v1/atendimento/", st.session_state['token'])
        df_atendimentos = pd.DataFrame(df_atendimentos)
        initial_requerimento_inicial = fetch_resource("api/v1/requerimento-inicial/", st.session_state['token'])
        # initial_estado_requerimento_inicial = fetch_resource("api/v1/estado-requerimento-inicial/", st.session_state['token'])

        df_requerimento_inicial = pd.DataFrame(initial_requerimento_inicial)
        # df_requerimento_recurso = fetch_resource("api/v1/requerimento-recurso/", st.session_state['token'])

        # Estatísticas resumidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Clientes", len(df_clientes))
        with col2:
            st.metric("Total de Atendimentos", len(df_atendimentos))
        with col3:
            st.metric("Total de Requerimentos Iniciais", len(df_requerimento_inicial))

        # requerimento inicial
        if initial_requerimento_inicial:
            # Process initial requests data
            df_requerimento_inicial = pd.DataFrame(initial_requerimento_inicial)

            # Seção de filtro por estado
            st.header("Filtrar Requerimentos por Estado")

            # Criar duas colunas para os filtros
            col1, col2 = st.columns(2)

            with col1:
                # Filtro por estado
                estados_disponiveis = df_requerimento_inicial['estado_nome'].unique()
                estado_selecionado = st.selectbox(
                    "Selecione um estado para filtrar:",
                    options=estados_disponiveis,
                    index=0
                )

            with col2:
                # Filtro por ano (opcional)
                df_requerimento_inicial['ano'] = pd.to_datetime(df_requerimento_inicial['data']).dt.year
                anos_disponiveis = sorted(df_requerimento_inicial['ano'].unique(), reverse=True)
                ano_selecionado = st.selectbox(
                    "Selecione um ano (opcional):",
                    options=["Todos"] + anos_disponiveis,
                    index=0
                )
            # Aplicar filtros
            df_filtrado = df_requerimento_inicial[
                df_requerimento_inicial['estado_nome'] == estado_selecionado
            ]
            if ano_selecionado != "Todos":
                df_filtrado = df_filtrado[df_filtrado['ano'] == ano_selecionado]

            # Mostrar estatísticas do filtro
            st.metric(f"Total de Requerimentos Iniciais {estado_selecionado}", len(df_filtrado))

            # Criar tabela com links
            if not df_filtrado.empty:
                st.subheader(f"Lista de Requerimentos - Estado: {estado_selecionado}")

                # Criar DataFrame para exibição com links
                df_display = df_filtrado[['protocolo', 'data', 'requerente_titular', 'NB']].copy()
                df_display['data'] = pd.to_datetime(df_display['data']).dt.strftime('%d/%m/%Y')
                df_display['Link'] = df_display.apply(
                    lambda row: create_requerimento_link(
                        cpf=row['requerente_titular'],  # Supondo que este é o campo com o CPF
                        protocolo=row['protocolo']
                    ),
                    axis=1
                )
                # Ordenar por data (mais recente primeiro)
                df_display = df_display.sort_values('data', ascending=False)

                # Exibir tabela (usando markdown para renderizar os links)
                with st.expander("Mostrar Requerimentos Iniciais Filtrados"):
                    st.dataframe(df_display)
                    # for _, row in df_display.iterrows():
                    #     st.markdown(f"""
                    #     **Protocolo:** {row['Link']}
                    #     **Data:** {row['data']}
                    #     **Requerente:** {row['requerente_titular']}
                    #     **NB:** {row['NB'] if pd.notna(row['NB']) else 'N/A'}
                    #     ---
                    #     """, unsafe_allow_html=True)
            else:
                st.warning(f"Nenhum requerimento encontrado para o estado {estado_selecionado}")

            # Count status for initial requests
            # print(df_requerimento_inicial['estado'].iloc[0])
            if 'estado_nome' in df_requerimento_inicial.columns:
                # df_requerimento_inicial['estado_nome'] = df_requerimento_inicial['estado_nome'].apply(lambda x: x['nome'])
                inicial_counts = df_requerimento_inicial['estado_nome'].value_counts().reset_index()
                inicial_counts.columns = ['Estado', 'Count']

                # Create pie chart for initial requests
                fig_inicial = px.pie(inicial_counts,
                                     values='Count',
                                     names='Estado',
                                     title='Estado dos Requerimentos Iniciais',
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_inicial, use_container_width=True)

        # with st.expander("Show Raw Data"):
        #     st.subheader("Initial Requests Data")
        #     st.dataframe(df_requerimento_inicial)

        # Análise de dados
        if not df_clientes.empty and not df_atendimentos.empty and not df_requerimento_inicial.empty:
            # Converter datas
            df_atendimentos['data'] = pd.to_datetime(df_atendimentos['data'])
            df_requerimento_inicial['data'] = pd.to_datetime(df_requerimento_inicial['data'])

            # Análise por ano
            st.header("Estatísticas por Ano")
            col1, col2 = st.columns(2)
            with col1:
                # Atendimentos por ano
                df_atendimentos['ano_atendimento'] = df_atendimentos['data'].dt.year
                atendimentos_por_ano = df_atendimentos['ano_atendimento'].value_counts().sort_index()
                st.subheader("Atendimentos por ano")
                st.bar_chart(atendimentos_por_ano)
            with col2:
                # Requerimentos iniciais por ano
                df_requerimento_inicial['ano_atendimento'] = df_requerimento_inicial['data'].dt.year
                requerimento_inicial_por_ano = df_requerimento_inicial['ano_atendimento'].value_counts().sort_index()
                st.subheader("Requerimentos iniciais por ano")
                st.bar_chart(requerimento_inicial_por_ano)

        else:
            st.warning("Por favor, faça login para acessar o dashboard")


if __name__ == "__main__":
    main()
