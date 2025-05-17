import streamlit as st
from utils import fetch_resource, create_requerimento_link, handle_session
import plotly.express as px
import pandas as pd

handle_session()
# st.set_page_config(page_title="Requerimento Inicial", page_icon="../static/images/favicon.ico", layout="wide")

st.title("Requerimentos Iniciais")
st.write("Esta página é para mostrar os requerimentos.")

initial_requerimento_inicial = fetch_resource("api/v1/requerimentos-iniciais/", st.session_state['token'])

# filtros de requerimento inicial
if initial_requerimento_inicial:
    # Process initial requests data
    df_requerimento_inicial = pd.DataFrame(initial_requerimento_inicial)

    # Sidebar com filtros
    with st.sidebar:
        st.header("🔎 Filtros")
        busca_NB = st.text_input("Pesquisar por NB:")
        busca_cpf = st.text_input("Pesquisar por CPF:")

    df_requerimento_inicial['NB'] = df_requerimento_inicial['NB'].fillna("")
    df_requerimento_inicial['requerente_titular'] = df_requerimento_inicial['requerente_titular'].fillna("")

    # Aplicar filtros
    if busca_NB:
        df_requerimento_inicial = df_requerimento_inicial[df_requerimento_inicial['NB'].str.contains(busca_NB, case=False)]
    if busca_cpf:
        df_requerimento_inicial = df_requerimento_inicial[df_requerimento_inicial['requerente_titular'].str.contains(busca_cpf)]

    st.metric("Total de Requerimentos Iniciais", len(df_requerimento_inicial),
              help="Número total de requerimentos iniciais cadastrados no sistema")

    col1, col2 = st.columns(2)
    with col1:
        if 'estado_nome' in df_requerimento_inicial.columns:
            inicial_counts = df_requerimento_inicial['estado_nome'].value_counts().reset_index()
            inicial_counts.columns = ['Estado', 'Count']

            # Create pie chart for initial requests
            fig_inicial = px.pie(inicial_counts,
                                 values='Count',
                                 names='Estado',
                                 title='Estado dos Requerimentos Iniciais',
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_inicial, use_container_width=True)
    with col2:
        # Seção de filtro por estado
        st.header("Filtrar Requerimentos por Estado")

        # Criar duas colunas para os filtros
        subcol1, subcol2 = st.columns(2)

        with subcol1:
            # Filtro por estado
            estados_disponiveis = df_requerimento_inicial['estado_nome'].unique()
            estado_selecionado = st.selectbox(
                "Selecione um estado para filtrar:",
                options=estados_disponiveis,
                index=0
            )

        with subcol2:
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
            lambda row: f'<a href="{create_requerimento_link(
                cpf=row['requerente_titular'],  # Supondo que este é o campo com o CPF
                id=row['id']
            )}" target="_blank" style="color: #1f77b4; text-decoration: none;">Detalhes</a>',
            axis=1
        )
        # Ordenar por data (mais recente primeiro)
        df_display = df_display.sort_values(
            'data',
            ascending=False,
            key=lambda s: pd.to_datetime(s, dayfirst=True)
        )

        # Estilizar a tabela
        st.markdown("""
        <style>
            table { width: 100%; border-collapse: collapse; }
            th {  padding: 12px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #eee; font-size: 14px; }
            a:hover { text-decoration: underline !important; }
            .stNumberInput { width: 120px; }
        </style>
        """, unsafe_allow_html=True)

        st.subheader("Lista de Requerimentos Iniciais Filtrados")

        # Exibir tabela (usando markdown para renderizar os links)
        st.markdown(
            df_display
            .to_html(escape=False, index=False,
                     header=True,
                     justify='left'),
            unsafe_allow_html=True
        )
    else:
        st.warning(f"Nenhum requerimento encontrado para o estado {estado_selecionado}")
