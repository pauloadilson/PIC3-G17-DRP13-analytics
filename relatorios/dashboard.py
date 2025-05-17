import streamlit as st
import pandas as pd
from utils import fetch_resource, handle_session
from metricas import calcular_metricas_periodicas, calcular_frequencia

handle_session()
# st.set_page_config(page_title="Análise de Dados - CPPREV",
#                    page_icon="static/images/favicon.png",
#                    layout="wide")

# Título
st.title("Análise de Clientes, Atendimentos e Requerimentos Iniciais")

# Buscar dados da API Django
initial_clientes = fetch_resource("api/v1/clientes/", st.session_state['token'])
df_clientes = pd.DataFrame(initial_clientes)
initial_atendimentos = fetch_resource("api/v1/atendimentos/", st.session_state['token'])
df_atendimentos = pd.DataFrame(initial_atendimentos)
initial_eventos = fetch_resource("api/v1/eventos/", st.session_state['token'])
df_eventos = pd.DataFrame(initial_eventos)


initial_requerimento_inicial = fetch_resource("api/v1/requerimentos-iniciais/", st.session_state['token'])
df_requerimento_inicial = pd.DataFrame(initial_requerimento_inicial)
# Calcular deferidos usando a função
requerimentos_iniciais_deferidos = calcular_frequencia(
    df=df_requerimento_inicial,
    coluna="estado_nome",
    valor="concluído deferido"
)

initial_recurso = fetch_resource("api/v1/requerimentos-recursos/", st.session_state['token'])
df_recurso = pd.DataFrame(initial_recurso)
recursos_deferidos = calcular_frequencia(
    df=df_recurso,
    coluna="estado_nome",
    valor="concluído deferido"
)
# Estatísticas resumidas
col1, col2, col3 = st.columns(3)
col1.metric("**Total de Clientes**", len(df_clientes), border=True)
col2.metric("**Total de Atendimentos**", len(df_atendimentos), border=True)
col3.metric("**Total de Eventos**", len(df_eventos), border=True)

# Estatísticas resumidas
col4, col5 = st.columns(2)
col4.metric("**Total de Requerimentos Iniciais/Deferidos**", len(df_requerimento_inicial), delta=requerimentos_iniciais_deferidos, border=True)
col5.metric("**Total de Recursos/Deferidos**", len(df_recurso), delta=recursos_deferidos, border=True)

# KPIs SECUNDÁRIOS
st.header("Métricas Complementares")

# Calcular métricas para cada conjunto de dados
metricas_trimestrais_atendimentos = calcular_metricas_periodicas(df_atendimentos, 3)
metricas_trimestrais_requerimentos = calcular_metricas_periodicas(df_requerimento_inicial, 3)
metricas_trimestrais_recursos = calcular_metricas_periodicas(df_recurso, 3)

secondary_col1, secondary_col2, secondary_col3 = st.columns(3)
with secondary_col1:
    st.metric(label="Atendimentos - Último Trimestre",
              value=metricas_trimestrais_atendimentos["ultimo_periodo"],
              delta=f"{metricas_trimestrais_atendimentos["delta_percentual"]:.1f}% vs trimestre anterior")
with secondary_col2:
    st.metric(label="Requerimentos Iniciais - Último Trimestre",
              value=metricas_trimestrais_requerimentos["ultimo_periodo"],
              delta=f"{metricas_trimestrais_requerimentos["delta_percentual"]:.1f}% vs trimestre anterior")
with secondary_col3:
    st.metric(label="Recursos - Último Trimestre",
              value=metricas_trimestrais_recursos["ultimo_periodo"],
              delta=f"{metricas_trimestrais_recursos["delta_percentual"]:.1f}% vs trimestre anterior")

st.divider()

# Análise de dados
if not df_atendimentos.empty and not df_requerimento_inicial.empty and not df_recurso.empty:
    # Converter datas
    df_atendimentos['data'] = pd.to_datetime(df_atendimentos['data'])
    df_requerimento_inicial['data'] = pd.to_datetime(df_requerimento_inicial['data'])
    df_recurso['data'] = pd.to_datetime(df_recurso['data'])

    # Análise por ano
    st.header("Estatísticas por Ano")
    col1, col2, col3 = st.columns(3)
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
    with col3:
        # Recursos por ano
        df_recurso['ano_atendimento'] = df_recurso['data'].dt.year
        recursos_por_ano = df_recurso['ano_atendimento'].value_counts().sort_index()
        st.subheader("Recursos por ano")
        st.bar_chart(recursos_por_ano)

else:
    st.warning("Por favor, faça login para acessar o dashboard")
