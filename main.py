# Passo a passo do projeto
# Passo 1: Criar a tela do sistema
# Passo 2: Criar o formulário de cadastro
# Passo 3: Salvar a venda na base de dados
# Passo 4: Mostrar a base de dados na tela
# Passo 5: Criar o dashboard com os gráficos

# pip install streamlit pandas plotly
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Passo 1: Criar a tela do sistema
# Configuração da página


import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Sistema de Vendas", layout="wide")

# ==========================================
# SISTEMA DE AUTENTICAÇÃO / LOGIN
# ==========================================
USUARIOS_PERMITIDOS = {
    
    "rogerio.ribeiro": "manc150626",
    "marcio.navega": "manc150626"
}

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔒 Acesso ao Sistema")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar")

        if btn_login:
            if usuario_input in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[usuario_input] == senha_input:
                st.session_state["logado"] = True
                st.session_state["usuario_atual"] = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    st.stop()

# ==========================================
# ÁREA RESTRITA (SISTEMA DE VENDAS)
# ==========================================
st.sidebar.write(f"👤 Logado como: *{st.session_state['usuario_atual']}*")
if st.sidebar.button("Sair / Logout"):
    st.session_state["logado"] = False
    st.rerun()

st.sidebar.divider()
st.title("Sistema de Vendas")

# Garante que o arquivo CSV exista
if not os.path.exists("vendas.csv"):
    df_inicial = pd.DataFrame(columns=["data", "vendedor", "produto", "quantidade", "valor"])
    df_inicial.to_csv("vendas.csv", index=False)

# Carrega a base de dados
tabela = pd.read_csv("vendas.csv")
tabela["valor"] = pd.to_numeric(tabela["valor"], errors="coerce").fillna(0)

# Passo 2: Formulário de Cadastro na Barra Lateral
st.sidebar.header("Cadastrar Venda")

with st.sidebar.form("form_venda", clear_on_submit=True):
    data = st.date_input("Data da Venda")
    vendedor = st.selectbox("Vendedor", ["Rogerio", "Marcio"])
    produto = st.selectbox("Produto", ["Par de Placas", "Placa Moto", "Unidade_Placa"])
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    
    # Campo de valor iniciando em branco (value=None) sem min_none que dava erro
    valor = st.number_input("Valor Unitário (R$)", min_value=0.0, value=None, format="%.2f")
    
    botao = st.form_submit_button("Cadastrar venda")

# Passo 3: Salvar a venda na base de dados
if botao:
    if valor is None:
        st.sidebar.error("Por favor, informe o valor unitário!")
    else:
        valor_total = quantidade * valor
        nova_venda = {
            "data": str(data),
            "vendedor": vendedor,
            "produto": produto,
            "quantidade": quantidade,
            "valor": valor_total
        }
        tabela = pd.concat([tabela, pd.DataFrame([nova_venda])], ignore_index=True)
        tabela.to_csv("vendas.csv", index=False)
        st.sidebar.success("Venda cadastrada!")
        st.rerun()

st.sidebar.divider()

# ==========================================
# FILTRO POR DATA NA BARRA LATERAL
# ==========================================
st.sidebar.header("Filtros")

# Opção para ativar/desativar o filtro de data específica
filtrar_data = st.sidebar.checkbox("Filtrar por data específica")

if filtrar_data and not tabela.empty:
    data_filtro = st.sidebar.date_input("Selecione a data para consultar")
    tabela_exibicao = tabela[tabela["data"] == str(data_filtro)]
else:
    tabela_exibicao = tabela

# Passo 4: Mostrar a base de dados filtrada na tela
st.subheader("Vendas Cadastradas")
if tabela_exibicao.empty:
    st.info("Nenhuma venda encontrada para esta consulta.")
else:
    st.dataframe(tabela_exibicao, use_container_width=True)

# Passo 5: Criar o dashboard com os dados filtrados
st.subheader("Dashboard")
soma = tabela_exibicao["valor"].sum() if not tabela_exibicao.empty else 0.0
st.metric("Faturamento Total", f"R$ {soma:,.2f}")

if not tabela_exibicao.empty:
    col1, col2 = st.columns(2)

    with col1:
        grafico = px.bar(
            tabela_exibicao, 
            x="vendedor", 
            y="valor", 
            color="produto", 
            title="Faturamento por Vendedor"
        )
        st.plotly_chart(grafico,  use_container_width=True)

    with col2:
        grafico2 = px.pie(
            tabela_exibicao, 
            names="produto", 
            values="valor", 
            title="Distribuição por Produto"
        )
        st.plotly_chart(grafico2, use_container_width=True)