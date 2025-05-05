import streamlit as st
from utils import fetch_resource, create_cliente_link
import pandas as pd

st.set_page_config(page_title="Clientes", page_icon="📈", layout="wide")

st.title("Clientes")
st.write("Esta página é para mostrar os clientes.")

initial_clientes = fetch_resource("api/v1/clientes/", st.session_state['token'])

# filtros de requerimento inicial
if initial_clientes:
    # Process initial requests data
    df_atendimentos = pd.DataFrame(initial_clientes)

    # Criar duas colunas para os filtros
    st.metric("Total de Clientes", len(initial_clientes))

    # Criar tabela com links
    if not df_atendimentos.empty:
        st.subheader("Lista de Clientes")

        # Criar DataFrame para exibição com links
        df_display = df_atendimentos[['cpf', 'nome', 'data_nascimento', 'telefone', 'observacao_telefone', 'telefone_whatsapp', 'email']].copy()
        df_display['Link'] = df_display.apply(
            lambda row: create_cliente_link(
                cpf=row['cpf'],  # Supondo que este é o campo com o CPF
            ),
            axis=1
        )
        # Ordenar por nome (ordem alfabética)
        df_display = df_display.sort_values('nome', ascending=True)

        # Exibir tabela (usando markdown para renderizar os links)
        with st.expander("Mostrar Clientes"):
            st.dataframe(df_display)
            # for "", unsafe_allow_html=True)
    else:
        st.warning("Nenhum atendimento registrado")
