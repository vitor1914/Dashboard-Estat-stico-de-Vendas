
import csv
import random
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as PDFImage,
    PageBreak,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA_PROJETO / "vendas.csv"

ARQUIVO_RELATORIO_CSV = PASTA_PROJETO / "relatorio_estatistico.csv"
ARQUIVO_RELATORIO_PDF = PASTA_PROJETO / "relatorio_estatistico.pdf"

SEMENTE_ALEATORIA = 42
NUMERO_SIMULACOES = 1000


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def formatar_reais(valor):
    """Formata um número como moeda brasileira."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def converter_numero(valor):
    """Converte números com ponto ou vírgula decimal."""
    valor = str(valor).strip()
    valor = valor.replace("R$", "").replace(" ", "")

    if not valor:
        raise ValueError("Valor numérico vazio.")

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    return float(valor)


def ler_limite(mensagem, valor_padrao):
    """Solicita um número ao usuário."""
    entrada = input(
        f"{mensagem} [padrão: {valor_padrao}]: "
    ).strip()

    if not entrada:
        return float(valor_padrao)

    try:
        return converter_numero(entrada)
    except ValueError:
        print("Valor inválido. Será utilizado o valor padrão.")
        return float(valor_padrao)


def salvar_grafico(nome_arquivo):
    """Salva o gráfico na pasta do projeto."""
    caminho = PASTA_PROJETO / nome_arquivo

    plt.tight_layout()
    plt.savefig(caminho, dpi=150, bbox_inches="tight")

    print(f"Gráfico salvo: {nome_arquivo}")

    plt.show()
    plt.close()


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

def carregar_vendas(caminho):
    """Carrega e valida os registros do arquivo CSV."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}\n"
            "Coloque vendas.csv na mesma pasta do main.py."
        )

    with open(
        caminho,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        amostra = arquivo.read(4096)
        arquivo.seek(0)

        try:
            dialeto = csv.Sniffer().sniff(
                amostra,
                delimiters=",;"
            )
        except csv.Error:
            dialeto = csv.excel

        leitor = csv.DictReader(arquivo, dialect=dialeto)

        if not leitor.fieldnames:
            raise ValueError("O CSV não possui cabeçalho.")

        leitor.fieldnames = [
            nome.strip().lower()
            for nome in leitor.fieldnames
        ]

        obrigatorias = {"quantidade", "valor"}

        if not obrigatorias.issubset(set(leitor.fieldnames)):
            raise ValueError(
                "O CSV precisa ter as colunas "
                "'quantidade' e 'valor'."
            )

        registros = []
        linhas_invalidas = 0

        for linha in leitor:
            try:
                quantidade = converter_numero(
                    linha["quantidade"]
                )
                valor = converter_numero(
                    linha["valor"]
                )

                if (
                    not quantidade.is_integer()
                    or quantidade <= 0
                    or valor < 0
                ):
                    linhas_invalidas += 1
                    continue

                registros.append({
                    "quantidade": int(quantidade),
                    "valor": valor
                })

            except (ValueError, TypeError, KeyError, AttributeError):
                linhas_invalidas += 1

    if not registros:
        raise ValueError(
            "Nenhuma venda válida foi encontrada no CSV."
        )

    print("\n" + "=" * 65)
    print("CARREGAMENTO DOS DADOS")
    print("=" * 65)
    print(f"Arquivo: {caminho.name}")
    print(f"Vendas válidas: {len(registros)}")
    print(f"Linhas ignoradas: {linhas_invalidas}")
    print("=" * 65)

    return registros


# ============================================================
# ESTATÍSTICA DESCRITIVA
# ============================================================

def analisar_vendas(registros):
    """Calcula e apresenta os indicadores estatísticos."""
    valores = [r["valor"] for r in registros]
    quantidades = [r["quantidade"] for r in registros]

    media = statistics.mean(valores)
    mediana = statistics.median(valores)
    moda = statistics.multimode(valores)

    print("\n" + "=" * 65)
    print("ESTATÍSTICA DESCRITIVA")
    print("=" * 65)

    print(f"Quantidade de vendas: {len(registros)}")
    print(f"Quantidade total de itens: {sum(quantidades)}")
    print(f"Faturamento total: {formatar_reais(sum(valores))}")
    print(f"Média: {formatar_reais(media)}")
    print(f"Mediana: {formatar_reais(mediana)}")

    print(
        "Moda: "
        + ", ".join(formatar_reais(v) for v in moda)
    )

    print(f"Menor venda: {formatar_reais(min(valores))}")
    print(f"Maior venda: {formatar_reais(max(valores))}")
    print(
        f"Amplitude: "
        f"{formatar_reais(max(valores) - min(valores))}"
    )
    print(
        f"Variância populacional: "
        f"{statistics.pvariance(valores):.2f}"
    )
    print(
        f"Desvio-padrão populacional: "
        f"{statistics.pstdev(valores):.2f}"
    )

    if len(valores) >= 2:
        q1, q2, q3 = statistics.quantiles(
            valores,
            n=4,
            method="inclusive"
        )

        iqr = q3 - q1
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr

        atipicos = [
            v for v in valores
            if v < limite_inferior or v > limite_superior
        ]

        print(f"Q1: {formatar_reais(q1)}")
        print(f"Q2: {formatar_reais(q2)}")
        print(f"Q3: {formatar_reais(q3)}")
        print(f"IQR: {formatar_reais(iqr)}")

        print(
            "Possíveis valores atípicos: "
            + (
                ", ".join(formatar_reais(v) for v in atipicos)
                if atipicos else "Nenhum"
            )
        )

    if len(set(quantidades)) > 1 and len(set(valores)) > 1:
        correlacao = statistics.correlation(
            quantidades,
            valores
        )
        print(f"Correlação de Pearson: {correlacao:.4f}")
    else:
        print("Correlação de Pearson: não calculável.")

    print("=" * 65)


# ============================================================
# INTERVALO DE CONFIANÇA
# ============================================================

def obter_intervalo_confianca(valores, nivel_confianca=0.95):
    """Calcula o intervalo t de confiança da média."""
    if len(valores) < 2:
        return None

    media = statistics.mean(valores)
    desvio = statistics.stdev(valores)
    erro_padrao = desvio / (len(valores) ** 0.5)

    alfa = 1 - nivel_confianca

    valor_critico = stats.t.ppf(
        1 - alfa / 2,
        df=len(valores) - 1
    )

    margem = valor_critico * erro_padrao

    return {
        "media": media,
        "desvio_amostral": desvio,
        "erro_padrao": erro_padrao,
        "margem_erro": margem,
        "limite_inferior": media - margem,
        "limite_superior": media + margem,
        "nivel_confianca": nivel_confianca
    }


def calcular_intervalo_confianca(registros):
    """Exibe e desenha o intervalo de confiança de 95%."""
    valores = [r["valor"] for r in registros]
    intervalo = obter_intervalo_confianca(valores)

    if intervalo is None:
        print("Intervalo de confiança exige pelo menos duas vendas.")
        return

    media = intervalo["media"]
    margem = intervalo["margem_erro"]

    print("\n" + "=" * 65)
    print("INTERVALO DE CONFIANÇA DE 95%")
    print("=" * 65)
    print(f"Média amostral: {formatar_reais(media)}")
    print(
        f"Desvio-padrão amostral: "
        f"{intervalo['desvio_amostral']:.2f}"
    )
    print(f"Erro padrão: {intervalo['erro_padrao']:.2f}")
    print(f"Margem de erro: {formatar_reais(margem)}")
    print(
        f"Limite inferior: "
        f"{formatar_reais(intervalo['limite_inferior'])}"
    )
    print(
        f"Limite superior: "
        f"{formatar_reais(intervalo['limite_superior'])}"
    )
    print("=" * 65)

    plt.figure(figsize=(9, 4))
    plt.errorbar(
        x=[media],
        y=[0],
        xerr=[[margem], [margem]],
        fmt="o",
        capsize=8
    )
    plt.axvline(
        media,
        linestyle="--",
        label=f"Média: {formatar_reais(media)}"
    )
    plt.title("Intervalo de confiança de 95% da média")
    plt.xlabel("Valor médio da venda (R$)")
    plt.yticks([])
    plt.grid(axis="x", alpha=0.3)
    plt.legend()

    salvar_grafico("intervalo_confianca.png")


# ============================================================
# EXPORTAÇÃO DO RELATÓRIO CSV
# ============================================================

def exportar_relatorio_csv(registros):
    """Exporta os indicadores estatísticos para CSV."""
    valores = [r["valor"] for r in registros]
    quantidades = [r["quantidade"] for r in registros]

    moda = statistics.multimode(valores)

    resultados = [
        ("Quantidade de vendas", len(registros)),
        ("Quantidade total de itens", sum(quantidades)),
        ("Faturamento total (R$)", round(sum(valores), 2)),
        ("Média por venda (R$)", round(statistics.mean(valores), 2)),
        ("Mediana (R$)", round(statistics.median(valores), 2)),
        (
            "Moda (R$)",
            "; ".join(f"{v:.2f}" for v in moda)
        ),
        ("Menor venda (R$)", round(min(valores), 2)),
        ("Maior venda (R$)", round(max(valores), 2)),
        (
            "Amplitude (R$)",
            round(max(valores) - min(valores), 2)
        ),
        (
            "Variância populacional",
            round(statistics.pvariance(valores), 2)
        ),
        (
            "Desvio-padrão populacional",
            round(statistics.pstdev(valores), 2)
        )
    ]

    if len(valores) >= 2:
        intervalo = obter_intervalo_confianca(valores)

        resultados.extend([
            ("Nível de confiança", "95%"),
            (
                "Erro padrão (R$)",
                round(intervalo["erro_padrao"], 2)
            ),
            (
                "Margem de erro (R$)",
                round(intervalo["margem_erro"], 2)
            ),
            (
                "Limite inferior IC 95% (R$)",
                round(intervalo["limite_inferior"], 2)
            ),
            (
                "Limite superior IC 95% (R$)",
                round(intervalo["limite_superior"], 2)
            )
        ])

    if len(set(quantidades)) > 1 and len(set(valores)) > 1:
        resultados.append((
            "Correlação de Pearson",
            round(
                statistics.correlation(quantidades, valores),
                4
            )
        ))

    with open(
        ARQUIVO_RELATORIO_CSV,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["Indicador", "Resultado"])
        escritor.writerows(resultados)

    print(f"\nRelatório CSV criado: {ARQUIVO_RELATORIO_CSV.name}")


# ============================================================
# GRÁFICOS
# ============================================================

def criar_grafico(registros):
    valores = [r["valor"] for r in registros]

    plt.figure(figsize=(10, 5))
    plt.plot(
        range(1, len(valores) + 1),
        valores,
        marker="o"
    )
    plt.title("Valores das vendas")
    plt.xlabel("Número da venda")
    plt.ylabel("Valor (R$)")
    plt.grid(True, alpha=0.3)

    salvar_grafico("grafico_vendas.png")


def criar_histograma(registros):
    valores = [r["valor"] for r in registros]

    plt.figure(figsize=(10, 5))
    plt.hist(valores, bins="auto", edgecolor="black")
    plt.title("Distribuição dos valores das vendas")
    plt.xlabel("Valor da venda (R$)")
    plt.ylabel("Frequência")
    plt.grid(axis="y", alpha=0.3)

    salvar_grafico("histograma_vendas.png")


def criar_boxplot(registros):
    valores = [r["valor"] for r in registros]

    plt.figure(figsize=(8, 5))
    plt.boxplot(valores)
    plt.xticks([1], ["Vendas"])
    plt.title("Boxplot dos valores das vendas")
    plt.ylabel("Valor (R$)")
    plt.grid(axis="y", alpha=0.3)

    salvar_grafico("boxplot_vendas.png")


def criar_grafico_dispersao(registros):
    quantidades = [r["quantidade"] for r in registros]
    valores = [r["valor"] for r in registros]

    plt.figure(figsize=(9, 5))
    plt.scatter(quantidades, valores)
    plt.title("Quantidade x valor da venda")
    plt.xlabel("Quantidade de itens")
    plt.ylabel("Valor da venda (R$)")
    plt.grid(True, alpha=0.3)

    salvar_grafico("dispersao_vendas.png")


# ============================================================
# REGRESSÃO LINEAR
# ============================================================

def criar_regressao_linear(registros):
    """Ajusta o modelo e salva um gráfico da regressão."""
    quantidades = [[r["quantidade"]] for r in registros]
    valores = [r["valor"] for r in registros]

    if (
        len(registros) < 2
        or len(set(r["quantidade"] for r in registros)) < 2
    ):
        print("Regressão não calculada: faltam quantidades distintas.")
        return

    modelo = LinearRegression()
    modelo.fit(quantidades, valores)

    previsoes = modelo.predict(quantidades)
    mse = mean_squared_error(valores, previsoes)
    r2 = r2_score(valores, previsoes)

    quantidade_futura = max(
        r["quantidade"] for r in registros
    ) + 1

    previsao_futura = modelo.predict([[quantidade_futura]])[0]

    print("\n" + "=" * 65)
    print("REGRESSÃO LINEAR")
    print("=" * 65)
    print(f"Coeficiente angular: {modelo.coef_[0]:.4f}")
    print(f"Intercepto: {modelo.intercept_:.2f}")
    print(f"R²: {r2:.4f}")
    print(f"Erro quadrático médio: {mse:.2f}")
    print(
        f"Previsão para {quantidade_futura} itens: "
        f"{formatar_reais(previsao_futura)}"
    )
    print("A previsão é uma estimativa, não uma garantia.")
    print("=" * 65)

    x_ordenado = sorted(
        r["quantidade"] for r in registros
    )
    y_previsto = modelo.predict(
        [[x] for x in x_ordenado]
    )

    plt.figure(figsize=(9, 5))
    plt.scatter(
        [r["quantidade"] for r in registros],
        valores,
        label="Vendas observadas"
    )
    plt.plot(
        x_ordenado,
        y_previsto,
        label="Regressão linear"
    )
    plt.title("Regressão linear: quantidade x valor")
    plt.xlabel("Quantidade de itens")
    plt.ylabel("Valor da venda (R$)")
    plt.grid(True, alpha=0.3)
    plt.legend()

    salvar_grafico("regressao_linear.png")


# ============================================================
# PROBABILIDADE E FREQUÊNCIA RELATIVA
# ============================================================

def analisar_probabilidade(registros, limite):
    valores = [r["valor"] for r in registros]
    total = len(valores)

    acima = sum(v > limite for v in valores)
    abaixo_igual = total - acima

    prob_acima = acima / total
    prob_abaixo = abaixo_igual / total

    print("\n" + "=" * 65)
    print("PROBABILIDADE EMPÍRICA")
    print("=" * 65)
    print(f"Limite: {formatar_reais(limite)}")
    print(f"Vendas acima: {acima}/{total} ({prob_acima:.2%})")
    print(
        f"Vendas abaixo ou iguais: "
        f"{abaixo_igual}/{total} ({prob_abaixo:.2%})"
    )
    print("=" * 65)

    menor = min(valores)
    maior = max(valores)

    if menor == maior:
        faixas = [(menor, maior)]
    else:
        numero_faixas = min(5, total)
        largura = (maior - menor) / numero_faixas
        faixas = []

        for i in range(numero_faixas):
            inicio = menor + i * largura
            fim = (
                maior
                if i == numero_faixas - 1
                else menor + (i + 1) * largura
            )
            faixas.append((inicio, fim))

    rotulos = []
    frequencias = []

    for i, (inicio, fim) in enumerate(faixas):
        if menor == maior:
            quantidade = total
        elif i == len(faixas) - 1:
            quantidade = sum(
                inicio <= v <= fim for v in valores
            )
        else:
            quantidade = sum(
                inicio <= v < fim for v in valores
            )

        rotulos.append(f"{inicio:.0f}–{fim:.0f}")
        frequencias.append(quantidade / total)

    plt.figure(figsize=(10, 5))
    plt.bar(rotulos, frequencias)
    plt.title("Frequência relativa por faixa de preço")
    plt.xlabel("Faixa de preço (R$)")
    plt.ylabel("Frequência relativa")
    plt.xticks(rotation=25)
    plt.grid(axis="y", alpha=0.3)

    salvar_grafico("frequencia_relativa_precos.png")

    plt.figure(figsize=(7, 4))
    plt.bar(
        ["Acima do limite", "Abaixo ou igual"],
        [prob_acima, prob_abaixo]
    )
    plt.title("Probabilidade empírica por limite")
    plt.ylabel("Probabilidade")
    plt.ylim(0, 1)
    plt.grid(axis="y", alpha=0.3)

    salvar_grafico("probabilidade_por_limite.png")


# ============================================================
# SIMULAÇÃO DE MONTE CARLO
# ============================================================

def simular_monte_carlo(registros, numero_simulacoes=1000):
    """Simula faturamentos com base nos valores observados."""
    valores = [r["valor"] for r in registros]

    random.seed(SEMENTE_ALEATORIA)

    quantidade_vendas = len(valores)
    faturamentos = []

    for _ in range(numero_simulacoes):
        amostra = random.choices(
            valores,
            k=quantidade_vendas
        )
        faturamentos.append(sum(amostra))

    print("\n" + "=" * 65)
    print("SIMULAÇÃO DE MONTE CARLO")
    print("=" * 65)
    print(f"Número de simulações: {numero_simulacoes}")
    print(f"Vendas por simulação: {quantidade_vendas}")
    print(
        f"Faturamento médio: "
        f"{formatar_reais(statistics.mean(faturamentos))}"
    )
    print(
        f"Mediana simulada: "
        f"{formatar_reais(statistics.median(faturamentos))}"
    )
    print(
        f"Desvio-padrão: "
        f"{formatar_reais(statistics.pstdev(faturamentos))}"
    )
    print(
        f"Menor faturamento: "
        f"{formatar_reais(min(faturamentos))}"
    )
    print(
        f"Maior faturamento: "
        f"{formatar_reais(max(faturamentos))}"
    )

    limite = ler_limite(
        "Qual faturamento deseja analisar na simulação?",
        2500
    )

    probabilidade = sum(
        f > limite for f in faturamentos
    ) / numero_simulacoes

    print(
        f"Probabilidade simulada de superar "
        f"{formatar_reais(limite)}: {probabilidade:.2%}"
    )
    print(
        "A simulação usa os valores históricos como referência; "
        "não garante resultados futuros."
    )
    print("=" * 65)

    plt.figure(figsize=(10, 5))
    plt.hist(faturamentos, bins="auto", edgecolor="black")
    plt.axvline(
        limite,
        linestyle="--",
        label=f"Limite: {formatar_reais(limite)}"
    )
    plt.title("Monte Carlo: distribuição do faturamento")
    plt.xlabel("Faturamento simulado (R$)")
    plt.ylabel("Frequência")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    salvar_grafico("monte_carlo_faturamento.png")


# ============================================================
# GERAÇÃO DO RELATÓRIO PDF
# ============================================================

def gerar_relatorio_pdf(registros):
    """Cria um PDF com indicadores estatísticos e gráficos."""
    valores = [r["valor"] for r in registros]
    quantidades = [r["quantidade"] for r in registros]

    documento = SimpleDocTemplate(
        str(ARQUIVO_RELATORIO_PDF),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )

    estilos = getSampleStyleSheet()
    conteudo = []

    conteudo.append(
        Paragraph(
            "Relatório Estatístico de Vendas",
            estilos["Title"]
        )
    )
    conteudo.append(Spacer(1, 0.3 * cm))

    conteudo.append(
        Paragraph(
            "Relatório gerado automaticamente pelo projeto Python.",
            estilos["Normal"]
        )
    )
    conteudo.append(Spacer(1, 0.5 * cm))

    indicadores = [
        ["Indicador", "Resultado"],
        ["Quantidade de vendas", str(len(registros))],
        ["Quantidade total de itens", str(sum(quantidades))],
        ["Faturamento total", formatar_reais(sum(valores))],
        [
            "Média por venda",
            formatar_reais(statistics.mean(valores))
        ],
        [
            "Mediana",
            formatar_reais(statistics.median(valores))
        ],
        [
            "Moda",
            ", ".join(
                formatar_reais(v)
                for v in statistics.multimode(valores)
            )
        ],
        ["Menor venda", formatar_reais(min(valores))],
        ["Maior venda", formatar_reais(max(valores))],
        [
            "Variância populacional",
            f"{statistics.pvariance(valores):.2f}"
        ],
        [
            "Desvio-padrão populacional",
            f"{statistics.pstdev(valores):.2f}"
        ],
    ]

    if len(valores) >= 2:
        intervalo = obter_intervalo_confianca(valores)

        indicadores.extend([
            ["Intervalo de confiança", "95%"],
            [
                "Limite inferior do IC",
                formatar_reais(intervalo["limite_inferior"])
            ],
            [
                "Limite superior do IC",
                formatar_reais(intervalo["limite_superior"])
            ],
        ])

    tabela = Table(
        indicadores,
        colWidths=[8.2 * cm, 8.0 * cm],
        repeatRows=1
    )

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [colors.white, colors.HexColor("#F0F4F8")]
        ),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    conteudo.append(tabela)
    conteudo.append(Spacer(1, 0.5 * cm))

    conteudo.append(
        Paragraph(
            "Gráficos da análise",
            estilos["Heading1"]
        )
    )
    conteudo.append(Spacer(1, 0.3 * cm))

    graficos = [
        ("grafico_vendas.png", "Valores das vendas"),
        ("histograma_vendas.png", "Histograma"),
        ("boxplot_vendas.png", "Boxplot"),
        ("dispersao_vendas.png", "Dispersão"),
        ("regressao_linear.png", "Regressão linear"),
        ("intervalo_confianca.png", "Intervalo de confiança"),
        ("frequencia_relativa_precos.png", "Frequência relativa"),
        ("probabilidade_por_limite.png", "Probabilidade por limite"),
        ("monte_carlo_faturamento.png", "Simulação de Monte Carlo"),
    ]

    graficos_encontrados = 0

    for nome_arquivo, titulo in graficos:
        caminho = PASTA_PROJETO / nome_arquivo

        if caminho.exists():
            conteudo.append(
                Paragraph(titulo, estilos["Heading2"])
            )

            imagem = PDFImage(
                str(caminho),
                width=15.5 * cm,
                height=8.5 * cm,
                kind="proportional"
            )

            conteudo.append(imagem)
            conteudo.append(Spacer(1, 0.3 * cm))
            graficos_encontrados += 1

    if graficos_encontrados == 0:
        conteudo.append(
            Paragraph(
                "Nenhum gráfico encontrado.",
                estilos["Normal"]
            )
        )

    conteudo.append(Spacer(1, 0.5 * cm))
    conteudo.append(
        Paragraph(
            "Observação: os resultados descrevem os dados fornecidos. "
            "As previsões e simulações não garantem resultados futuros.",
            estilos["Normal"]
        )
    )

    documento.build(conteudo)

    print(f"\nPDF gerado: {ARQUIVO_RELATORIO_PDF.name}")


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    print("\n" + "=" * 65)
    print("PROJETO DE ANÁLISE ESTATÍSTICA DE VENDAS")
    print("=" * 65)

    try:
        registros = carregar_vendas(ARQUIVO_CSV)

        # Indicadores e exportação CSV
        analisar_vendas(registros)
        exportar_relatorio_csv(registros)

        # Gráficos descritivos
        criar_grafico(registros)
        criar_histograma(registros)
        criar_boxplot(registros)
        criar_grafico_dispersao(registros)

        # Análises adicionais
        calcular_intervalo_confianca(registros)
        criar_regressao_linear(registros)

        limite = ler_limite(
            "Qual valor deseja analisar na probabilidade?",
            250
        )

        analisar_probabilidade(registros, limite)

        simular_monte_carlo(
            registros,
            numero_simulacoes=NUMERO_SIMULACOES
        )

        # Gerar o PDF somente depois que os gráficos existirem
        gerar_relatorio_pdf(registros)

        print("\n" + "=" * 65)
        print("ANÁLISE CONCLUÍDA!")
        print("=" * 65)
        print(f"Relatório CSV: {ARQUIVO_RELATORIO_CSV.name}")
        print(f"Relatório PDF: {ARQUIVO_RELATORIO_PDF.name}")
        print("Gráficos salvos na pasta do projeto.")
        print("=" * 65)

    except (FileNotFoundError, ValueError) as erro:
        print(f"\nERRO NOS DADOS OU ARQUIVO:\n{erro}")

    except Exception as erro:
        print(f"\nERRO INESPERADO: {erro}")
        raise


if __name__ == "__main__":
    main()
