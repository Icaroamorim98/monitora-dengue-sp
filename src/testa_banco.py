import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///data/dengue_sp.db')

df_teste = pd.read_sql('SELECT * FROM casos_2023', con=engine)

print(df_teste.head())