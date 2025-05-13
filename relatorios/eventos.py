import streamlit as st
from utils import fetch_resource, handle_session
import pandas as pd

handle_session()
st.set_page_config(page_title="Agenda", page_icon="📈", layout="wide")

st.title("Agenda")
st.write("Esta página é para mostrar os eventos agendados.")

initial_eventos = fetch_resource("api/v1/eventos/", st.session_state['token'])


# filtros de requerimento inicial
if initial_eventos:
    # Filtrando datas futuras
    # Process initial requests data
    df_eventos = pd.DataFrame(initial_eventos)

    # Sidebar com filtros
    with st.sidebar:
        st.header("🔎 Filtros")
        busca_data = st.text_input("Pesquisar por data:")

    # Aplicar filtros
    if busca_data:
        df_eventos = df_eventos[df_eventos['data_inicio'].str.contains(busca_data, case=False)]

    df_eventos['data_inicio'] = pd.to_datetime(df_eventos['data_inicio'])
    data_atual = pd.Timestamp.now(tz='UTC-03:00')
    df_eventos_futuros = df_eventos[df_eventos['data_inicio'] > data_atual]
    df_eventos_passados = df_eventos[df_eventos['data_inicio'] < data_atual]
    # Seção de filtro por estado
    st.header("Filtrar Eventos  por Estado")

    # Criar duas colunas para os filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Eventos", len(df_eventos))
    with col2:
        st.metric("Total de Eventos Futuros", len(df_eventos_futuros))
    with col3:
        st.metric("Total de Eventos Passados", len(df_eventos_passados))

    # Criar tabela com links
    if not df_eventos.empty:
        st.subheader("Lista de Eventos Futuros")

        # Criar DataFrame para exibição com links
        df_display = df_eventos[['id', 'tipo', 'titulo', 'descricao', 'data_inicio', 'local']].copy()
        df_display['data_inicio'] = pd.to_datetime(df_display['data_inicio']).dt.strftime('%d/%m/%Y')
        # Ordenar por data (mais recente primeiro)
        df_display = df_display.sort_values('data_inicio', ascending=False)

        # Exibir tabela (usando markdown para renderizar os links)
        st.dataframe(df_display)
    else:
        st.warning("Nenhum eventos agendado")
