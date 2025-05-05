import streamlit as st
from utils import fetch_resource, create_atendimento_link
import pandas as pd

st.set_page_config(page_title="Atendimentos", page_icon="📈", layout="wide")

st.title("Atendimentos")
st.write("Esta página é para mostrar os atendimentos.")

initial_atendimentos = fetch_resource("api/v1/atendimentos/", st.session_state['token'])

# filtros de requerimento inicial
if initial_atendimentos:
    # Process initial requests data
    df_atendimentos = pd.DataFrame(initial_atendimentos)

    # Seção de filtro por estado
    st.header("Filtrar Atendimentos")

    # Criar duas colunas para os filtros
    st.metric("Total de Atendimentos", len(df_atendimentos))

    # Criar tabela com links
    if not df_atendimentos.empty:
        st.subheader("Lista de Atendimentos")

        # Criar DataFrame para exibição com links
        df_display = df_atendimentos[['id', 'data', 'cliente', 'requerimento', 'descricao', 'observacao']].copy()
        df_display['data'] = pd.to_datetime(df_display['data']).dt.strftime('%d/%m/%Y')
        df_display['Link'] = df_display.apply(
            lambda row: create_atendimento_link(
                cpf=row['cliente'],  # Supondo que este é o campo com o CPF
                id=row['id']  # Supondo que este é o campo com o ID do atendimento
            ),
            axis=1
        )
        # Ordenar por data (mais recente primeiro)
        df_display = df_display.sort_values('data', ascending=False)

        # Exibir tabela (usando markdown para renderizar os links)
        with st.expander("Mostrar Atendimentos"):
            st.dataframe(df_display)
            # for "", unsafe_allow_html=True)
    else:
        st.warning("Nenhum atendimento registrado")
