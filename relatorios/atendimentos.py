import streamlit as st
from utils import fetch_resource, create_atendimento_link, handle_session
import pandas as pd

handle_session()
st.set_page_config(page_title="Atendimentos", page_icon="📈", layout="wide")

st.title("Atendimentos")
st.write("Explore os dados dos atendimentos cadastrados no sistema.")

initial_atendimentos = fetch_resource("api/v1/atendimentos/", st.session_state['token'])

# filtros de requerimento inicial
if initial_atendimentos:
    # Process initial requests data
    df_atendimentos = pd.DataFrame(initial_atendimentos)

    df_atendimentos['requerimento'] = df_atendimentos['requerimento'].fillna("")

    # Sidebar com filtros
    with st.sidebar:
        st.header("🔎 Filtros")
        busca_data = st.text_input("Pesquisar por data:")
        busca_cpf = st.text_input("Pesquisar por CPF:")

    # Aplicar filtros
    if busca_data:
        df_atendimentos = df_atendimentos[df_atendimentos['data'].str.contains(busca_data, case=False)]
    if busca_cpf:
        df_atendimentos = df_atendimentos[df_atendimentos['cliente'].str.contains(busca_cpf)]

    # Criar duas colunas para os filtros
    st.metric("Total de Atendimentos", len(df_atendimentos))

    # Criar tabela com links
    if not df_atendimentos.empty:
        # Criar DataFrame para exibição com links
        df_display = df_atendimentos[['id', 'data', 'cliente', 'requerimento', 'descricao', 'observacao']].copy()
        df_display['data'] = pd.to_datetime(df_display['data']).dt.strftime('%d/%m/%Y')
        df_display['Link'] = df_display.apply(
            lambda row: f'<a href="{create_atendimento_link(
                cpf=row['cliente'],  # Supondo que este é o campo com o CPF
                id=row['id']  # Supondo que este é o campo com o ID do atendimento
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

        st.subheader("Lista de Atendimentos")

        # Exibir tabela (usando markdown para renderizar os links)
        st.markdown(
            df_display
            .to_html(escape=False, index=False,
                     header=True,
                     justify='left'),
            unsafe_allow_html=True
        )
    else:
        st.warning("Nenhum atendimento registrado")
