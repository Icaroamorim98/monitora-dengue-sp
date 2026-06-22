# Monitora Dengue SP 🦟

![Monitora Dengue SP](Banner%20final%20monitora-dengue-sp.png)

## 📌 Visão Geral
Projeto de Data Science para análise e visualização dos casos de **dengue no município de São Paulo (capital)** em **2023**. O fluxo cobre desde a extração dos dados brutos do SINAN/DATASUS, passando pelo tratamento e padronização, até a entrega de uma base limpa pronta para um **dashboard no Power BI** — utilizado como base para um panfleto informativo.

## 🗂️ Fonte dos Dados
- **Sistema:** SINAN — *Sistema de Informação de Agravos de Notificação* (Ministério da Saúde / DATASUS).
- **Arquivo original:** `DENGBR23.dbc/.dbf` (notificações nacionais de dengue).
- **Doença:** Dengue — CID-10 `A90` (`ID_AGRAVO = A90`).
- **Recorte:** município de São Paulo capital (código IBGE `355030`).
- **Período:** ano de 2023 (notificações de 03/01/2023 a 30/12/2023).

> *Fonte: Ministério da Saúde / SINAN – DATASUS. Notificações de dengue (CID-10 A90), município de São Paulo, 2023.*

## 🛠️ Tecnologias
- **Linguagem:** Python 3.10+
- **Bibliotecas:** Pandas, NumPy, SQLAlchemy, dbfread, Matplotlib
- **Armazenamento:** SQLite
- **Visualização:** Power BI Desktop
- **Ferramentas:** VS Code, Git

## 📂 Estrutura do Projeto
```
monitora-dengue-sp/
├── data/
│   ├── raw/                       # Dados brutos do DATASUS (.dbc/.dbf) — não versionados
│   ├── processed/                 # Saídas tratadas em CSV — não versionadas
│   └── dengue_sp.db               # Banco SQLite (tabelas bruta e tratada)
├── src/
│   ├── processa_sp.py             # Extrai do .dbf, filtra SP capital → tabela casos_2023
│   ├── trata_dados.py             # Trata e decodifica os dados → casos_dengue_tratado
│   ├── analise.py                 # Gráfico exploratório (casos por mês) com Matplotlib
│   └── testa_banco.py             # Lê o banco para conferência rápida
├── Graficos Power BI.pbix         # Dashboard do Power BI
├── requirements.txt
└── README.md
```

## 🔄 Pipeline de Dados
1. **Extração** (`processa_sp.py`): lê `DENGBR23.dbf`, filtra o município `355030` (SP capital) e grava a tabela bruta `casos_2023` no SQLite + CSV.
2. **Tratamento** (`trata_dados.py`):
   - Mantém apenas **dengue confirmada** (`CLASSI_FIN` 10, 11, 12).
   - Reduz de 121 para ~27 colunas relevantes.
   - **Corrige a idade** a partir do código `NU_IDADE_N` do SINAN (ex.: `4028` → 28 anos) e cria faixas etárias.
   - **Decodifica códigos em texto legível** (Sexo, Raça/Cor, Classificação, Evolução, Critério, Hospitalização, sintomas).
   - Cria campos de tempo (Ano, Mês, Mês-nome, Semana epidemiológica).
   - Trata valores vazios como "Não informado".
   - Salva `data/processed/dengue_sp_2023_tratado.csv` (UTF-8 com BOM) e a tabela `casos_dengue_tratado`.
3. **Visualização** (Power BI): importa o CSV / conecta ao SQLite e monta o dashboard.

## 🚀 Como Executar
```bash
# 1. Instalar as dependências
pip install -r requirements.txt

# 2. (Opcional) Reextrair a base bruta a partir do .dbf
python src/processa_sp.py

# 3. Gerar a base tratada (CSV + tabela no SQLite)
python src/trata_dados.py

# 4. (Opcional) Visualizar um gráfico exploratório
python src/analise.py
```
No Power BI: **Obter dados → Texto/CSV** e selecione `data/processed/dengue_sp_2023_tratado.csv` (ou conecte à tabela `casos_dengue_tratado` no banco `data/dengue_sp.db`).

## 📊 Base Tratada — Resultado
- **14.775** casos de dengue confirmada (SP capital, 2023).
- Pico epidemiológico em **abril/maio**.
- Colunas prontas para análise: faixa etária, sexo, raça/cor, classificação, evolução, hospitalização e sintomas — todas em texto legível.
