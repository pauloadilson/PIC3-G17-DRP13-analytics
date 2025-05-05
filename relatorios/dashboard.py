import streamlit as st
import pandas as pd
from utils import fetch_resource


st.set_page_config(page_title="Análise de Dados - CPPREV",
                   page_icon="static/images/favicon.png",
                   layout="wide")

# Verificar nível de acesso (adicionar esta parte)
user_info = fetch_resource("api/v1/user-info/", st.session_state['token'])
if user_info and 'role' in user_info:
    st.session_state['user_role'] = user_info['role']

# Verificar se tem acesso (adicionar esta verificação)
if st.session_state.get('user_role') not in ['admin', 'Advogados']:
    st.error(f"Acesso restrito. Você não tem permissão para visualizar este conteúdo. Role: {st.session_state.get('user_role')}")
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
