import streamlit as st
import pandas as pd
import requests
import plotly.express as px

from requests.exceptions import RequestException

DJANGO_API_URL = st.secrets["django_api"]["api_url"]
TOKEN_ENDPOINT = "api/v1/authentication/token/"
API_ENDPOINT = "api/v1/clientes/"

DJANGO_USERNAME = st.secrets["django_api"]["username"]
DJANGO_PASSWORD = st.secrets["django_api"]["password"]


# Função para obter token
def get_jwt_token():
    try:
        if not DJANGO_USERNAME or not DJANGO_PASSWORD:
            st.error("API credentials not configured :(")
            return None

        response = requests.post(
            f"{DJANGO_API_URL}{TOKEN_ENDPOINT}",
            json={"username": DJANGO_USERNAME, "password": DJANGO_PASSWORD}
        )
        response.raise_for_status()
        return response.json().get('access')
    except RequestException as e:
        st.error(f"Error getting token: {e}")
        return None


# Função para fazer requisição autenticada
def make_authenticated_request(endpoint, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{DJANGO_API_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Erro na requisição: {e}")
        return None


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


def main():
    # Configuração da página
    st.set_page_config(page_title="Análise de Dados", page_icon="static/images/favicon.png")

    # Link de volta para o Django
    st.sidebar.markdown("[Voltar para o CPPREV](https://cpprev-dev-09ed70033bf7.herokuapp.com/)")

    # Título
    st.title("Análise de Clientes, Atendimentos e Requerimentos Iniciais")

    # get JWT token
    token = get_jwt_token()
    if token:
        st.session_state['token'] = token
        st.success("Autenticado com sucesso!")

    # Se autenticado, mostrar dados
    if 'token' in st.session_state:

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
                                     title='Distribution of Initial Request Statuses',
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

            # Clientes por ano de cadastro (assumindo que há uma data de cadastro)
            if 'data_cadastro' in df_clientes.columns:
                df_clientes['ano_cadastro'] = pd.to_datetime(df_clientes['data_cadastro']).dt.year
                clientes_por_ano = df_clientes['ano_cadastro'].value_counts().sort_index()
                st.subheader("Clientes cadastrados por ano")
                st.bar_chart(clientes_por_ano)

            # Atendimentos por ano
            df_atendimentos['ano_atendimento'] = df_atendimentos['data'].dt.year
            atendimentos_por_ano = df_atendimentos['ano_atendimento'].value_counts().sort_index()
            st.subheader("Atendimentos por ano")
            st.bar_chart(atendimentos_por_ano)

            # Requerimentos iniciais por ano
            df_requerimento_inicial['ano_atendimento'] = df_requerimento_inicial['data'].dt.year
            requerimento_inicial_por_ano = df_requerimento_inicial['ano_atendimento'].value_counts().sort_index()
            st.subheader("Requerimentos iniciais por ano")
            st.bar_chart(requerimento_inicial_por_ano)

        else:
            st.warning("Não foi possível carregar os dados. Verifique a conexão com a API.")


if __name__ == "__main__":
    main()
