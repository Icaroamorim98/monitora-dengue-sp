import pandas as pd
from sqlalchemy import create_engine
# Esta é nova para os gráficos:
import matplotlib.pyplot as plt
engine = create_engine('sqlite:///data/dengue_sp.db')

df_teste = pd.read_sql('SELECT * FROM casos_2023', con=engine)

df_teste['DT_NOTIFIC'] = pd.to_datetime(df_teste['DT_NOTIFIC'])

#Criando a coluna do Mês
df_teste['MES'] = df_teste['DT_NOTIFIC'].dt.month

#Agrupando os casos
casos_por_mes = df_teste['MES'].value_counts().sort_index()


print(casos_por_mes)

# 1. Criar a figura (tamanho do gráfico)
plt.figure(figsize=(10, 6))

# 2. Desenhar a linha (o eixo X são os meses, o Y são os valores)
casos_por_mes.plot(kind='bar', color='red', rot=0)

# 3. Perfumaria profissional (Títulos e Legendas)
plt.title('Casos de Dengue por Mês em SP - 2023')
plt.xlabel('Mês')
plt.ylabel('Quantidade de Casos')
plt.grid(True)

# Opcional: Criar uma lista com os nomes curtos dos meses
nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Ajustar os rótulos do eixo X (Ticks)
plt.xticks(range(12), nomes_meses)

# 4. Mostrar o gráfico
plt.show()