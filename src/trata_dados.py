"""
Tratamento dos dados de dengue da cidade de São Paulo (capital) - 2023.

Lê a tabela bruta já filtrada (`casos_2023`) do SQLite, decodifica os códigos
do SINAN para texto legível, corrige a idade e gera uma base limpa por caso,
pronta para o Power BI (uso em panfleto informativo).

Saídas:
  - data/processed/dengue_sp_2023_tratado.csv  (UTF-8 com BOM, acentos corretos)
  - Tabela `casos_dengue_tratado` no banco data/dengue_sp.db
"""

import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# 1. Carregar dados brutos (já filtrados para a cidade de SP - município 355030)
# ---------------------------------------------------------------------------
engine = create_engine('sqlite:///data/dengue_sp.db')
df = pd.read_sql('SELECT * FROM casos_2023', con=engine)
print(f"Linhas carregadas (SP capital): {len(df)}")

# ---------------------------------------------------------------------------
# 2. Manter somente dengue confirmada
#    CLASSI_FIN: 10 = Dengue, 11 = com sinais de alarme, 12 = grave
# ---------------------------------------------------------------------------
df = df[df['CLASSI_FIN'].astype(str).isin(['10', '11', '12'])].copy()
print(f"Linhas após filtrar dengue confirmada: {len(df)}")

# ---------------------------------------------------------------------------
# 3. Selecionar apenas as colunas úteis para o dashboard
# ---------------------------------------------------------------------------
colunas = [
    'DT_NOTIFIC', 'DT_SIN_PRI', 'SEM_NOT', 'NU_ANO', 'NU_IDADE_N',
    'CS_SEXO', 'CS_GESTANT', 'CS_RACA', 'CS_ESCOL_N',
    'CLASSI_FIN', 'CRITERIO', 'EVOLUCAO', 'HOSPITALIZ', 'MUNICIPIO', 'UF',
    # sintomas principais
    'FEBRE', 'MIALGIA', 'CEFALEIA', 'EXANTEMA', 'VOMITO',
    'NAUSEA', 'DOR_COSTAS', 'ARTRALGIA', 'DOR_RETRO',
]
df = df[colunas].copy()

# ---------------------------------------------------------------------------
# 4. Converter datas e criar campos de tempo
# ---------------------------------------------------------------------------
df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
df['DT_SIN_PRI'] = pd.to_datetime(df['DT_SIN_PRI'], errors='coerce')

df['ANO'] = df['DT_NOTIFIC'].dt.year
df['MES'] = df['DT_NOTIFIC'].dt.month

nomes_meses = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez',
}
df['MES_NOME'] = df['MES'].map(nomes_meses)

# Semana epidemiológica: SEM_NOT vem como AAAASS -> pega os 2 últimos dígitos
df['SEMANA_EPID'] = pd.to_numeric(
    df['SEM_NOT'].astype(str).str[-2:], errors='coerce'
).astype('Int64')

# ---------------------------------------------------------------------------
# 5. Calcular idade real a partir do código NU_IDADE_N
#    Formato SINAN: 1º dígito = unidade (1=hora, 2=dia, 3=mês, 4=ano),
#    3 últimos dígitos = valor. Ex.: 4028 -> 28 anos.
# ---------------------------------------------------------------------------
codigo = pd.to_numeric(df['NU_IDADE_N'], errors='coerce')
unidade = codigo // 1000
valor = codigo % 1000
# Idade em anos completos: se unidade == 4 (anos) usa o valor; senão é < 1 ano
df['IDADE'] = np.where(unidade == 4, valor, 0)
df['IDADE'] = pd.to_numeric(df['IDADE'], errors='coerce').astype('Int64')

faixas = [-1, 9, 19, 29, 39, 49, 59, 69, 200]
rotulos = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70+']
df['FAIXA_ETARIA'] = pd.cut(df['IDADE'], bins=faixas, labels=rotulos)

# ---------------------------------------------------------------------------
# 6. Decodificar códigos -> texto legível
# ---------------------------------------------------------------------------
map_sexo = {'M': 'Masculino', 'F': 'Feminino', 'I': 'Ignorado'}
map_raca = {
    '1': 'Branca', '2': 'Preta', '3': 'Amarela',
    '4': 'Parda', '5': 'Indígena', '9': 'Ignorado',
}
map_gestante = {
    '1': '1º Trimestre', '2': '2º Trimestre', '3': '3º Trimestre',
    '4': 'Idade gestacional ignorada', '5': 'Não', '6': 'Não se aplica',
    '9': 'Ignorado',
}
map_escol = {
    '0': 'Analfabeto',
    '1': 'Fundamental 1ª a 4ª série incompleta',
    '2': 'Fundamental 4ª série completa',
    '3': 'Fundamental 5ª a 8ª série incompleta',
    '4': 'Fundamental completo',
    '5': 'Médio incompleto',
    '6': 'Médio completo',
    '7': 'Superior incompleto',
    '8': 'Superior completo',
    '9': 'Ignorado',
    '10': 'Não se aplica',
}
map_classi = {
    '10': 'Dengue',
    '11': 'Dengue com sinais de alarme',
    '12': 'Dengue grave',
}
map_criterio = {
    '1': 'Laboratorial', '2': 'Clínico-epidemiológico', '3': 'Em investigação',
}
map_evolucao = {
    '1': 'Cura', '2': 'Óbito por dengue', '3': 'Óbito por outras causas',
    '4': 'Óbito em investigação', '9': 'Ignorado',
}
map_sim_nao = {'1': 'Sim', '2': 'Não', '9': 'Ignorado'}

df['SEXO'] = df['CS_SEXO'].astype(str).str.strip().map(map_sexo)
df['RACA_COR'] = df['CS_RACA'].astype(str).str.strip().map(map_raca)
df['GESTANTE'] = df['CS_GESTANT'].astype(str).str.strip().map(map_gestante)
df['ESCOLARIDADE'] = df['CS_ESCOL_N'].astype(str).str.strip().map(map_escol)
df['CLASSIFICACAO'] = df['CLASSI_FIN'].astype(str).str.strip().map(map_classi)
df['CRITERIO_DIAG'] = df['CRITERIO'].astype(str).str.strip().map(map_criterio)
df['EVOLUCAO_CASO'] = df['EVOLUCAO'].astype(str).str.strip().map(map_evolucao)
df['HOSPITALIZACAO'] = df['HOSPITALIZ'].astype(str).str.strip().map(map_sim_nao)

# Sintomas -> Sim/Não
sintomas = {
    'FEBRE': 'FEBRE', 'MIALGIA': 'MIALGIA', 'CEFALEIA': 'CEFALEIA',
    'EXANTEMA': 'EXANTEMA', 'VOMITO': 'VOMITO', 'NAUSEA': 'NAUSEA',
    'DOR_COSTAS': 'DOR_COSTAS', 'ARTRALGIA': 'ARTRALGIA', 'DOR_RETRO': 'DOR_RETRO',
}
for origem, destino in sintomas.items():
    df[destino] = df[origem].astype(str).str.strip().map(map_sim_nao)

# ---------------------------------------------------------------------------
# 7. Montar tabela final, renomear e tratar nulos
# ---------------------------------------------------------------------------
# A base é só da capital; os campos MUNICIPIO/UF do SINAN vêm quase sempre vazios,
# então definimos valores fixos legíveis (úteis como rótulo no Power BI).
df['MUNICIPIO_NOME'] = 'São Paulo'
df['UF'] = 'SP'

df_final = df.rename(columns={
    'DT_NOTIFIC': 'DATA_NOTIFICACAO',
    'DT_SIN_PRI': 'DATA_PRIMEIROS_SINTOMAS',
})[[
    'DATA_NOTIFICACAO', 'DATA_PRIMEIROS_SINTOMAS', 'ANO', 'MES', 'MES_NOME',
    'SEMANA_EPID', 'IDADE', 'FAIXA_ETARIA', 'SEXO', 'RACA_COR', 'GESTANTE',
    'ESCOLARIDADE', 'CLASSIFICACAO', 'CRITERIO_DIAG', 'EVOLUCAO_CASO',
    'HOSPITALIZACAO', 'MUNICIPIO_NOME', 'UF',
    'FEBRE', 'MIALGIA', 'CEFALEIA', 'EXANTEMA', 'VOMITO',
    'NAUSEA', 'DOR_COSTAS', 'ARTRALGIA', 'DOR_RETRO',
]].copy()

# Categóricas vazias / sem correspondência -> "Não informado"
cols_categoricas = [
    'SEXO', 'RACA_COR', 'GESTANTE', 'ESCOLARIDADE', 'CRITERIO_DIAG',
    'EVOLUCAO_CASO', 'HOSPITALIZACAO',
    'FEBRE', 'MIALGIA', 'CEFALEIA', 'EXANTEMA', 'VOMITO',
    'NAUSEA', 'DOR_COSTAS', 'ARTRALGIA', 'DOR_RETRO',
]
for c in cols_categoricas:
    df_final[c] = df_final[c].fillna('Não informado')

# FAIXA_ETARIA é Categorical: adiciona a categoria antes de preencher
df_final['FAIXA_ETARIA'] = df_final['FAIXA_ETARIA'].cat.add_categories(
    ['Não informado']
).fillna('Não informado')

# ---------------------------------------------------------------------------
# 8. Salvar (CSV + SQLite)
# ---------------------------------------------------------------------------
os.makedirs('data/processed', exist_ok=True)

caminho_csv = 'data/processed/dengue_sp_2023_tratado.csv'
df_final.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
print(f"[OK] CSV salvo: {caminho_csv}")

df_final.to_sql('casos_dengue_tratado', con=engine, if_exists='replace', index=False)
print("[OK] Tabela 'casos_dengue_tratado' atualizada no banco.")

print(f"\nBase tratada pronta: {len(df_final)} casos x {df_final.shape[1]} colunas")
