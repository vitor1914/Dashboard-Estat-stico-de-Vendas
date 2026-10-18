# Dashboard Estatístico de Vendas

Projeto de análise estatística e visualização de dados desenvolvido em Python, com foco na exploração de dados comerciais e na construção de um dashboard interativo.

## Objetivo

Analisar dados de vendas por meio de estatística descritiva, gráficos e indicadores, permitindo explorar os resultados de forma interativa.

## Tecnologias utilizadas

- Python
- Pandas
- Matplotlib
- Streamlit
- SciPy e Scikit-learn — utilizados em análises adicionais do projeto principal, quando aplicável

## Funcionalidades

- Cálculo de média, mediana e moda.
- Análise de valores mínimos, máximos e amplitude.
- Cálculo de desvio padrão e outras estatísticas descritivas.
- Visualização dos valores por registro.
- Histograma da distribuição dos valores.
- Gráfico de quantidade por registro.
- Dispersão entre quantidade e valor.
- Filtro interativo por faixa de preço.
- Tabela de dados filtrados.
- Exportação dos dados filtrados para CSV.
- Resumo estatístico dos dados.

## Estrutura do projeto

```text
Média, mediana e moda/
├── main.py
├── dashboard.py
├── vendas.csv
├── README.md
├── relatorio_estatistico.csv
├── relatorio_estatistico.pdf
└── gráficos gerados pelo projeto
```

## Como executar

### 1. Clonar o repositório

```bash
git clone
cd 
```

Substitua os valores acima pelo endereço e pelo nome reais do seu repositório.

### 2. Criar um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install pandas matplotlib streamlit scipy scikit-learn reportlab
```

### 4. Executar o dashboard

```bash
python -m streamlit run dashboard.py
```

O Streamlit exibirá um endereço local para abrir o dashboard no navegador.

## Dados

O projeto utiliza um arquivo CSV com as colunas `quantidade` e `valor`. Os dados devem estar na pasta do projeto.

Utilize dados fictícios ou anonimizados ao publicar o repositório.

## Aprendizados

- Manipulação e validação de dados com Pandas.
- Aplicação de estatística descritiva.
- Construção de gráficos com Matplotlib.
- Desenvolvimento de dashboards interativos.
- Organização de um projeto de análise de dados.
- Exportação de resultados para CSV.

## Autor

Portfólio de projetos em Data Analytics e Ciência de Dados.

Tecnologias e projetos adicionais: Python, SQL, Power BI e Engenharia de Dados.
