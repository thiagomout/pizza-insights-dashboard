import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Painel de Controle da Pizzaria")

if 'df' not in st.session_state:
    st.session_state.df = None

# Carregar dados do CSV
with st.sidebar:
    st.header("Configurações")
    uploaded_file = st.file_uploader("Carregar arquivo CSV", type=["csv"])
    
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.df['Data'] = pd.to_datetime(st.session_state.df['Data'], dayfirst=True, errors='coerce')
        st.success("Arquivo carregado com sucesso!")
    else:
        st.warning("Por favor, carregue um arquivo CSV.")

    if st.session_state.df is not None:
        st.header("Opções de Visualização")
        aggregate_option = st.selectbox(
            "Selecione o tipo de agregação",
            ["Diário", "Semanal"],
            key="aggregate_option"
        )

#Aba para ver dados e adcionar novos dados


st.header("Evolução Comparativa dos Indicadores")
if st.session_state.df is not None:
    df = st.session_state.df.copy() # Usa uma cópia para segurança
    df.dropna(subset=['Data'], inplace=True)
    df = df.sort_values('Data')

    # Agrupar os dados conforme a opção selecionada
    if aggregate_option == "Semanal":
        df_to_plot = df.set_index('Data').resample('W').sum().reset_index()
        st.write("Dados agregados semanalmente:")
    elif aggregate_option == "Diário":
        df_to_plot = df.copy()

    # Normalizar os dados
    df_norm = df_to_plot.copy()
    columns_to_normalize = ['Venda', 'Caixas', 'LataMolho', 'KgMuzzarela', 'KgFarinha']
    for col in columns_to_normalize:
        df_norm[col] = (df_norm[col] - df_norm[col].min()) / (df_norm[col].max() - df_norm[col].min())
    # Plotar os dados normalizados
    fig = px.line(df_norm, x='Data', y=columns_to_normalize,
                  title='Evolução Normalizada dos Indicadores',
                  labels={'value': 'Valor Normalizado', 'variable': 'Indicadores'})
    st.plotly_chart(fig)

    with st.expander("Adicionar dados de um novo dia"):
        with st.form("novo_dado_form", clear_on_submit=True):
            new_data = {}
            new_data['Data'] = st.date_input("Data", value=pd.to_datetime('today'))
            new_data['Venda'] = st.number_input("Venda", min_value=0, step=1)
            new_data['Caixas'] = st.number_input("Caixas", min_value=0, step=1)
            new_data['LataMolho'] = st.number_input("Lata de Molho", min_value=0, step=1)
            new_data['KgMuzzarela'] = st.number_input("Kg de Muzzarela", min_value=0.0, step=0.1)
            new_data['KgFarinha'] = st.number_input("Kg de Farinha", min_value=0.0, step=0.1)

            submitted = st.form_submit_button("Adicionar Novo Dado")

            if submitted:
                new_row = pd.DataFrame([new_data])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.df['Data'] = pd.to_datetime(st.session_state.df['Data'], dayfirst=True, errors='coerce')
                st.success("Dados adicionados com sucesso!")

# Salvar os dados atualizados de volta ao CSV
if st.session_state.df is not None:
    st.sidebar.download_button(
        label="Baixar CSV Atualizado",
        data=st.session_state.df.to_csv(index=False).encode('utf-8'),
        file_name='data_pizzateca_atualizado.csv',
        mime='text/csv'
    )
else:
    st.sidebar.info("Nenhum dado para salvar. Carregue um arquivo CSV primeiro.")