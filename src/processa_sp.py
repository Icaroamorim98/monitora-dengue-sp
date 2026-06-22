from dbfread import DBF
import pandas as pd
import os
from sqlalchemy import create_engine

# 1. Carrega o arquivo (O gigante)
tabela = DBF('data/raw/DENGBR23.dbf')
df = pd.DataFrame(iter(tabela))

# 2. CRIA O FILTRO (Esta é a linha que faltava!)
# Aqui dizemos: df_sp é apenas onde o município for a Capital de SP (355030)
df_sp = df[df['ID_MUNICIP'].astype(str) == '355030'].copy()

# 3. Agora sim, podemos imprimir os resultados
print(f"Total de linhas no Brasil: {len(df)}")
print(f"Total de linhas em SP Capital: {len(df_sp)}")

# 4. Mostra as primeiras linhas só de SP para conferir
print(df_sp.head())


# 5. Criar a pasta processed (se não existir) e salvar o arquivo
os.makedirs('data/processed', exist_ok=True)

df_sp.to_csv('data/processed/dengue_sp_2023.csv', index=False)
print("📂 Arquivo salvo com sucesso em data/processed/dengue_sp_2023.csv")

engine = create_engine('sqlite:///data/dengue_sp.db')
df_sp.to_sql('casos_2023', con=engine, if_exists='replace', index=False)