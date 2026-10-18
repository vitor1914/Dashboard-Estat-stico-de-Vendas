
import io
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ==================================================
# CONFIGURAÇÃO
# ==================================================

PASTA = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA / "vendas.csv"

st.set_page_config(
    page_title="Dashboard de Vendas | Data Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("Dashboard de Vendas")
st.caption("Projeto de análise estatística e visualização de dados")

# ==================================================
# CARREGAMENTO DOS DADOS
# ==================================================

@st.cache_data
def carregar_dados(caminho, ultima_modificacao):
    df = pd.read_csv(caminho, sep=None, engine="python")
    df.columns = df.columns.str.strip().str.lower()

    obrigatorias = {"quantidade", "valor"}
    faltantes = obrigatorias - set(df.columns)

    if faltantes:
        raise ValueError(
            "Colunas obrigatórias ausentes: "
            + ", ".join(sorted(faltantes))
        )

    for coluna in ["quantidade", "valor"]:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[coluna] = pd.to_numeric(
            df[coluna], errors="coerce"
        )

    df = df.dropna(subset=["quantidade", "valor"])
    return df


if not ARQUIVO_CSV.exists():
    st.error(
        "O arquivo vendas.csv não foi encontrado na pasta do projeto."
    )
    st.stop()

try:
    df = carregar_dados(
        str(ARQUIVO_CSV),
        ARQUIVO_CSV.stat().st_mtime,
    )
except Exception as erro:
    st.error(f"Não foi possível carregar os dados: {erro}")
    st.stop()

if df.empty:
    st.error("O arquivo não possui registros numéricos válidos.")
    st.stop()

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def reais(valor):
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_numero(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def criar_figura():
    fig, ax = plt.subplots(figsize=(8, 4))
    return fig, ax


# ==================================================
# FILTROS
# ==================================================

st.sidebar.header("Filtros de análise")
st.sidebar.write(f"Registros disponíveis: {len(df)}")

minimo = float(df["valor"].min())
maximo = float(df["valor"].max())

if minimo < maximo:
    intervalo = st.sidebar.slider(
        "Valor da venda",
        min_value=minimo,
        max_value=maximo,
        value=(minimo, maximo),
        format="%.2f",
    )
    dados = df[df["valor"].between(*intervalo)].copy()
else:
    dados = df.copy()
    st.sidebar.info("Todas as vendas têm o mesmo valor.")

if dados.empty:
    st.warning("Nenhum registro corresponde ao filtro.")
    st.stop()

st.sidebar.divider()
st.sidebar.caption("Dashboard desenvolvido em Python, Pandas, Matplotlib e Streamlit.")

# ==================================================
# INDICADORES
# ==================================================

valores = dados["valor"]
quantidades = dados["quantidade"]

faturamento = valores.sum()
media = valores.mean()
mediana = valores.median()
unidades = quantidades.sum()
modas = valores.mode()
moda = modas.iloc[0] if not modas.empty else float("nan")

st.subheader("Indicadores principais")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Faturamento dos registros", reais(faturamento))
c2.metric("Valor médio", reais(media))
c3.metric("Mediana", reais(mediana))
c4.metric("Unidades vendidas", formatar_numero(unidades))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Registros analisados", f"{len(dados)}")
c6.metric("Menor valor", reais(valores.min()))
c7.metric("Maior valor", reais(valores.max()))
c8.metric("Desvio padrão", reais(valores.std()) if len(dados) > 1 else "N/A")

st.divider()

# ==================================================
# VISUALIZAÇÕES
# ==================================================

st.subheader("Visualizações de vendas")

coluna1, coluna2 = st.columns(2)

with coluna1:
    st.markdown("**Valores por registro**")
    fig, ax = criar_figura()
    ax.plot(
        range(1, len(dados) + 1),
        valores.tolist(),
        marker="o",
    )
    ax.set_xlabel("Registro")
    ax.set_ylabel("Valor (R$)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with coluna2:
    st.markdown("**Distribuição dos valores**")
    fig, ax = criar_figura()
    ax.hist(valores, bins="auto", edgecolor="black")
    ax.set_xlabel("Valor (R$)")
    ax.set_ylabel("Frequência")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

coluna1, coluna2 = st.columns(2)

with coluna1:
    st.markdown("**Quantidade por registro**")
    fig, ax = criar_figura()
    ax.bar(range(1, len(dados) + 1), quantidades.tolist())
    ax.set_xlabel("Registro")
    ax.set_ylabel("Quantidade")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with coluna2:
    st.markdown("**Quantidade × valor**")
    fig, ax = criar_figura()
    ax.scatter(quantidades, valores)
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("Valor (R$)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ==================================================
# ANÁLISE AUTOMÁTICA
# ==================================================

st.divider()
st.subheader("Análise automática")

if media > mediana:
    st.write(
        "A média está acima da mediana. Valores elevados podem estar "
        "influenciando a média."
    )
elif media < mediana:
    st.write(
        "A média está abaixo da mediana. Valores menores podem estar "
        "influenciando a média."
    )
else:
    st.write("A média e a mediana são iguais neste conjunto de dados.")

if len(dados) > 1 and valores.std() > 0:
    coeficiente_variacao = valores.std() / media * 100 if media != 0 else float("nan")
    st.write(
        f"Coeficiente de variação amostral: "
        f"{formatar_numero(coeficiente_variacao)}%."
    )
    st.caption(
        "O coeficiente de variação compara o desvio padrão com a média; "
        "a interpretação depende do contexto dos dados."
    )

st.write(f"Moda: {reais(moda)}" if pd.notna(moda) else "Moda: não disponível.")
st.write(f"Amplitude dos valores: {reais(valores.max() - valores.min())}")

# ==================================================
# TABELA E EXPORTAÇÃO
# ==================================================

st.divider()
st.subheader("Dados filtrados")

st.dataframe(
    dados,
    use_container_width=True,
    hide_index=True,
)

csv_bytes = dados.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Baixar dados filtrados em CSV",
    data=csv_bytes,
    file_name="vendas_filtradas.csv",
    mime="text/csv",
)

# ==================================================
# RESUMO ESTATÍSTICO
# ==================================================

with st.expander("Consultar resumo estatístico completo"):
    resumo = dados[["quantidade", "valor"]].describe().T
    st.dataframe(resumo, use_container_width=True)

st.caption(
    "Observação: o faturamento exibido é a soma da coluna valor. "
    "Confirme se cada registro representa uma venda ou um item de venda."
)

st.success("Dashboard carregado com sucesso!")
