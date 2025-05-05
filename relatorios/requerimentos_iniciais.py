import streamlit as st
from utils import fetch_resource, create_requerimento_link
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Requerimento Inicial", page_icon="../static/images/favicon.ico", layout="wide")

st.title("Requerimentos Iniciais")
st.write("Esta página é para mostrar os requerimentos.")

initial_requerimento_inicial = fetch_resource("api/v1/requerimento-inicial/", st.session_state['token'])
# initial_estado_requerimento_inicial = fetch_resource("api/v1/estado-requerimento-inicial/", st.session_state['token'])

df_requerimento_inicial = pd.DataFrame(initial_requerimento_inicial)
# df_requerimento_recurso = fetch_resource("api/v1/requerimento-recurso/", st.session_state['token'])

# filtros de requerimento inicial
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
        df_display = df_filtrado[['id', 'protocolo', 'data', 'requerente_titular', 'NB']].copy()
        df_display['data'] = pd.to_datetime(df_display['data']).dt.strftime('%d/%m/%Y')
        df_display['Link'] = df_display.apply(
            lambda row: create_requerimento_link(
                cpf=row['requerente_titular'],  # Supondo que este é o campo com o CPF
                id=row['id']
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
