import streamlit as st
from utils import fetch_resource, create_cliente_link, handle_session
import pandas as pd

handle_session()
st.set_page_config(page_title="Clientes", page_icon="📈", layout="wide")

st.title("📇 Lista de Clientes")
st.write("Explore os dados dos clientes cadastrados no sistema.")

initial_clientes = fetch_resource("api/v1/clientes/", st.session_state['token'])

if initial_clientes:
    df_clientes = pd.DataFrame(initial_clientes)

    # Sidebar com filtros
    with st.sidebar:
        st.header("🔎 Filtros")
        busca_nome = st.text_input("Pesquisar por nome:")
        busca_cpf = st.text_input("Pesquisar por CPF:")

    # Aplicar filtros
    if busca_nome:
        df_clientes = df_clientes[df_clientes['nome'].str.contains(busca_nome, case=False)]
    if busca_cpf:
        df_clientes = df_clientes[df_clientes['cpf'].str.contains(busca_cpf)]

    st.metric("Total de Clientes", len(df_clientes),
              help="Número total de clientes cadastrados no sistema")

    if not df_clientes.empty:
        # Formatar dados
        df_clientes['data_nascimento'] = pd.to_datetime(df_clientes['data_nascimento']).dt.strftime('%d/%m/%Y')
        df_clientes['telefone'] = df_clientes['telefone'].fillna('N/A')

        # Criar links
        df_clientes['Detalhes'] = df_clientes['cpf'].apply(
            lambda cpf: f'<a href="{create_cliente_link(cpf)}" target="_blank" style="color: #1f77b4; text-decoration: none;">Detalhes</a>'
        )

        # Selecionar e ordenar colunas
        cols = ['nome', 'data_nascimento', 'cpf', 'telefone', 'email', 'Detalhes']
        df_display = df_clientes[cols].sort_values('nome', ascending=True)

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

        st.subheader("Lista de Clientes")

        st.markdown(
            df_display
            .to_html(escape=False, index=False,
                     columns=cols,
                     header=True,
                     justify='left'),
            unsafe_allow_html=True
        )

    else:
        st.warning("Nenhum cliente encontrado com os filtros selecionados")

else:
    st.error("Não foi possível carregar os dados dos clientes")
