# Passo a passo do projeto
# Passo 1: Criar a tela do sistema
# Passo 2: Criar o formulário de cadastro
# Passo 3: Salvar a venda na base de dados
# Passo 4: Mostrar a base de dados na tela
# Passo 5: Criar o dashboard com os gráficos

# pip install streamlit pandas plotly

# Passo 1: Criar a tela do sistema
# Configuração da página


import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sistema de Vendas", layout="wide", page_icon="📊"
)

# ==========================================
# GESTÃO DE DADOS (CSV + CACHE / SESSION)
# ==========================================
ARQUIVO_CSV = "vendas.csv"


def inicializar_csv():
    """Garante que o CSV exista com a coluna placa."""
    if not os.path.exists(ARQUIVO_CSV):
        df_inicial = pd.DataFrame(
            columns=[
                "data",
                "vendedor",
                "produto",
                "placa",
                "quantidade",
                "valor",
            ]
        )
        df_inicial.to_csv(ARQUIVO_CSV, index=False)



@st.cache_data
def carregar_dados():
    """Carrega os dados e garante que a coluna placa exista corretamente."""
    inicializar_csv()
    df = pd.read_csv(ARQUIVO_CSV)

    # Se existir 'placa.1', remove para não duplicar
    if "placa.1" in df.columns:
        df = df.drop(columns=["placa.1"])

    # Se a coluna placa não existir no CSV antigo, cria ela em branco
    if "placa" not in df.columns:
        df["placa"] = ""

    # Reordena e garante as colunas certas
    colunas_desejadas = ["data", "vendedor", "produto", "placa", "quantidade", "valor"]
    for col in colunas_desejadas:
        if col not in df.columns:
            df[col] = ""

    df = df[colunas_desejadas]

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)
    df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
    return df


def salvar_nova_venda(nova_venda):
    """Adiciona a nova venda ao CSV e limpa o cache."""
    df_atual = carregar_dados()
    df_atualizado = pd.concat(
        [df_atual, pd.DataFrame([nova_venda])], ignore_index=True
    )
    df_atualizado.to_csv(ARQUIVO_CSV, index=False)
    st.cache_data.clear()


# ==========================================
# SISTEMA DE AUTENTICAÇÃO / LOGIN
# ==========================================
USUARIOS_PERMITIDOS = {
    "admin": "12345",
    "rogerio.ribeiro": "manc150626",
    "marcio.navega": "manc150626",
}

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔒 Acesso ao Sistema")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário").strip()
        senha_input = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar")

        if btn_login:
            if (
                usuario_input in USUARIOS_PERMITIDOS
                and USUARIOS_PERMITIDOS[usuario_input] == senha_input
            ):
                st.session_state["logado"] = True
                st.session_state["usuario_atual"] = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    st.stop()

# ==========================================
# ÁREA RESTRITA (SISTEMA DE VENDAS)
# ==========================================
st.sidebar.write(f"👤 Logado como: {st.session_state['usuario_atual']}")
if st.sidebar.button("Sair / Logout"):
    st.session_state["logado"] = False
    st.rerun()

st.sidebar.divider()
st.title("Sistema de Vendas")

# Carrega os dados otimizados
tabela = carregar_dados()

# Passo 2: Formulário de Cadastro na Barra Lateral
st.sidebar.header("Cadastrar Venda")


with st.sidebar.form("form_venda", clear_on_submit=True):
    data = st.date_input("Data da Venda")
    vendedor = st.selectbox("Vendedor", ["Rogerio", "Marcio"])
    produto = st.selectbox(
        "Produto", ["Par de Placas", "Placa Moto", "Unidade_Placa"]
    )

    # Novo campo: Placa do veículo
    placa = st.text_input("Placa do Veículo", placeholder="Ex: ABC1D23 ou ABC1234")

    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    valor = st.number_input(
        "Valor Unitário (R$)", min_value=0.0, value=None, format="%.2f"
    )

    botao = st.form_submit_button("Cadastrar venda")


# Passo 3: Salvar a venda na base de dados
if botao:
    if valor is None:
        st.sidebar.error("Por favor, informe o valor unitário!")
    elif not placa.strip():
        st.sidebar.error("Por favor, informe a placa do veículo!")
    else:
        valor_total = quantidade * valor
        nova_venda = {
            "data": str(data),
            "vendedor": vendedor,
            "produto": produto,
            "placa": placa.strip().upper(),  # Transforma a placa em maiúsculas
            "quantidade": quantidade,
            "valor": valor_total,
        }
        salvar_nova_venda(nova_venda)
        st.sidebar.success("Venda cadastrada!")
        st.rerun()

st.sidebar.divider()

# ==========================================
# FILTROS NA BARRA LATERAL
# ==========================================
st.sidebar.header("Filtros")

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

faturamento_formatado = (
    f"R$ {soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
st.metric("Faturamento Total", faturamento_formatado)

if not tabela_exibicao.empty:
    col1, col2 = st.columns(2)

    with col1:
        grafico = px.bar(
            tabela_exibicao,
            x="vendedor",
            y="valor",
            color="produto",
            title="Faturamento por Vendedor",
            labels={"valor": "Valor (R$)", "vendedor": "Vendedor"},
        )
        st.plotly_chart(grafico, use_container_width=True)

    with col2:
        grafico2 = px.pie(
            tabela_exibicao,
            names="produto",
            values="valor",
            title="Distribuição por Produto",
        )
        st.plotly_chart(grafico2, use_container_width=True)

