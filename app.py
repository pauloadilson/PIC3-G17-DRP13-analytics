import streamlit as st
import pandas as pd
import requests
from datetime import datetime


# Configuração da página
st.set_page_config(page_title="Análise de Dados", page_icon="📊")

# Link de volta para o Django
st.sidebar.markdown("[Voltar para o CPPREV](https://cpprev-dev-09ed70033bf7.herokuapp.com/)")

# Título
st.title("Análise de Clientes e Atendimentos")


# Buscar dados da API Django
@st.cache_data(ttl=600)  # Cache por 10 minutos
def fetch_data():
    try:
        clientes = requests.get("https://cpprev-dev-09ed70033bf7.herokuapp.com/api/v1/clientes/").json()
        atendimentos = requests.get("https://cpprev-dev-09ed70033bf7.herokuapp.com/api/v1/atendimento/").json()
        return pd.DataFrame(clientes), pd.DataFrame(atendimentos)
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()


df_clientes, df_atendimentos = fetch_data()

# Análise de dados
if not df_clientes.empty and not df_atendimentos.empty:
    # Converter datas
    df_atendimentos['data'] = pd.to_datetime(df_atendimentos['data'])

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

    # Estatísticas resumidas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Clientes", len(df_clientes))
    with col2:
        st.metric("Total de Atendimentos", len(df_atendimentos))
else:
    st.warning("Não foi possível carregar os dados. Verifique a conexão com a API.")
