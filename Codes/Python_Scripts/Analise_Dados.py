# Bibliotecas
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.model_selection import train_test_split
import joblib
from config import env_file, sql_select, modelo_joblib, dados_csv

# Eliminar o limite de colunas
pd.set_option('display.max_columns', None)

# Carregando a configuração de conexão com o servidor
load_dotenv(dotenv_path=env_file)

## Puxando os dados do arquivo onde estão alocados
usuario = os.getenv('usuario')
senha = os.getenv('senha')
host = os.getenv('host')
porta = os.getenv('port')
database = os.getenv('bd')

## Criando URL de conexão
database_url = f'postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{database}'

## Engine de conexão
engine = create_engine(database_url)

### Query com arquivo para carregar os dados do servidor
with open(sql_select, 'r', encoding='utf-8') as select:
    query = select.read()

### Puxando os dados do servidor
with engine.connect() as conexao:
    df = pd.read_sql_query(query, con=conexao)

df.head()

# Validando os tipos
df.dtypes

# Selecionar apenas colunas numéricas
df_numerico = df.select_dtypes(include=['number'])

# Analisando a correlação dos dados
plt.figure(figsize=(15,5))
sns.heatmap(df_numerico.corr(), annot=True, cmap='Greens')

# Analisando os outliers
## Função para calcular os limites
def limite(coluna):
    q1 = coluna.quantile(0.25)
    q3 = coluna.quantile(0.75)
    amplitude = q3 - q1
    return q1 - 1.5*amplitude, q3 + 1.5*amplitude

## Função para criar o gráfico de boxplot para análise dos outliers
def diagrama_boxplot(coluna):
    fig, (ax1, ax2) = plt.subplots(1,2)
    fig.set_size_inches(15,5)
    sns.boxplot(x=coluna, ax=ax1)
    ax2.set_xlim(limite(coluna))
    sns.boxplot(x=coluna, ax=ax2)

## Função para criar o gráfico de barras para análise dos outliers
def grafico_barras(coluna):
    plt.figure(figsize=(15,5))
    ax = sns.barplot(x=coluna.value_counts().index, y=coluna.value_counts())
    ax.set_xlim(limite(coluna))

### Gráfico de análise da coluna Price
diagrama_boxplot(df['price'])

### Excluindo outliers
def excluir_outliers(data_frame, nome_coluna):
    qtde_linhas = data_frame.shape[0]
    lim_inf, lim_sup = limite(data_frame[nome_coluna])
    dataframe_filtrado = data_frame.loc[(data_frame[nome_coluna] >= lim_inf) & (data_frame[nome_coluna] <= lim_sup)]
    linhas_removidas = qtde_linhas - dataframe_filtrado.shape[0]
    return dataframe_filtrado, linhas_removidas

### novo dataframe com os dados de price filtrados
df_filtrado, linha_excluida = excluir_outliers(df, 'price')

### Gráfico de análise da coluna Extra_People
diagrama_boxplot(df_filtrado['extra_people'])

### novo dataframe com os dados de extra people filtrados
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'extra_people')


### Analisando os dados com valores discretos
#### Analisando host_listings_count
diagrama_boxplot(df_filtrado['host_listings_count'])
grafico_barras(df_filtrado['host_listings_count'])


#### Analisando accomodates 
diagrama_boxplot(df_filtrado['accommodates'])
grafico_barras(df_filtrado['accommodates'])

#### Excluindo os outliers do accomodates
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'accommodates')
print(linha_excluida)


### Analisando bathrooms
diagrama_boxplot(df_filtrado['bathrooms'])
grafico_barras(df_filtrado['bathrooms'])

#### Excluindo os outliers do accomodates
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'bathrooms')
print(linha_excluida)


### Analisando bedrooms
diagrama_boxplot(df_filtrado['bedrooms'])
grafico_barras(df_filtrado['bedrooms'])

#### Excluindo os outliers do accomodates
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'bedrooms')
print(linha_excluida)

df_filtrado.shape

### Analisando beds
diagrama_boxplot(df_filtrado['beds'])
grafico_barras(df_filtrado['beds'])

#### Excluindo os outliers do accomodates
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'beds')
print(linha_excluida)

#### Analisando guests_included
grafico_barras(df_filtrado['guests_included'])

#### Excluindo a coluna guests_included
df_filtrado = df_filtrado.drop('guests_included', axis = 1)


#### Analisando Minimum_Nights
diagrama_boxplot(df_filtrado['minimum_nights'])

#### Excluindo os outliers do Minimum_Nights
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'minimum_nights')
print(linha_excluida)

#### Analisando maximum_nights
diagrama_boxplot(df_filtrado['maximum_nights'])
grafico_barras(df_filtrado['maximum_nights'])

#### Excluindo a coluna guests_included
df_filtrado = df_filtrado.drop('maximum_nights', axis = 1)


#### Analisando number_of_reviews
diagrama_boxplot(df_filtrado['number_of_reviews'])
grafico_barras(df_filtrado['number_of_reviews'])



## Analisando os dados de texto
### Analisando a coluna property_type
df_filtrado['property_type'].value_counts()

plt.figure(figsize=(15,5))
grafico = sns.countplot(x='property_type', data = df_filtrado)
grafico.tick_params(axis = 'x', rotation = 90)

### Mudando os valores menores que 2000 para outros
tabela_tipos_casa = df_filtrado['property_type'].value_counts()
coluna_agrupar = []
for tipo in tabela_tipos_casa.index:
    if tabela_tipos_casa[tipo] < 3000:
        coluna_agrupar.append(tipo)

for tipo in coluna_agrupar:
    df_filtrado.loc[df_filtrado['property_type'] == tipo, 'property_type'] = 'Outros'


### Analisando a coluna room_type
df_filtrado['room_type'].value_counts()

plt.figure(figsize=(15,5))
grafico = sns.countplot(x='room_type', data = df_filtrado)
grafico.tick_params(axis = 'x', rotation = 90)


### Analisando a coluna room_type
df_filtrado['bed_type'].value_counts()

plt.figure(figsize=(15,5))
grafico = sns.countplot(x='bed_type', data = df_filtrado)
grafico.tick_params(axis = 'x', rotation = 90)


### Analisando a coluna cancellation_policy
df_filtrado['cancellation_policy'].value_counts()

plt.figure(figsize=(15,5))
grafico = sns.countplot(x='cancellation_policy', data = df_filtrado)
grafico.tick_params(axis = 'x', rotation = 90)


### Mudando os valores menores que 2000 para outros
tabela_policy = df_filtrado['cancellation_policy'].value_counts()
coluna_agrupar = []
for tipo in tabela_policy.index:
    if tabela_policy[tipo] < 13000:
        coluna_agrupar.append(tipo)

for tipo in coluna_agrupar:
    df_filtrado.loc[df_filtrado['cancellation_policy'] == tipo, 'cancellation_policy'] = 'strict'


### Analisando amenities
df_filtrado['amenities'].iloc[1].split(',')

#### Criando a coluna nova
df_filtrado['n_amenities'] = df_filtrado['amenities'].str.split(',').apply(len)

#### Excluindo a coluna amenities
df_filtrado = df_filtrado.drop('amenities', axis = 1)

#### Analisando os outliers dos amenities
#### Analisando n_amenities
diagrama_boxplot(df_filtrado['n_amenities'])
grafico_barras(df_filtrado['n_amenities'])

#### Excluindo os outliers do Minimum_Nights
df_filtrado, linha_excluida = excluir_outliers(df_filtrado, 'n_amenities')
print(linha_excluida)


### Alterando as variáveis True e False
df_cod = df_filtrado

# colunas que faremos a mudança de true para 1 e false para 0
colunas_cod = ['host_is_superhost', 'instant_bookable', 'is_business_travel_ready']

## Alterando
for coluna in colunas_cod:
    df_cod.loc[df_cod[coluna] == 't', coluna] = 1
    df_cod.loc[df_cod[coluna] == 'f', coluna] = 0

### Alterando as variáveis categóricas multiplas
# Colunas que serão alteradas:
colunas_dummies = ['property_type', 'room_type', 'bed_type', 'cancellation_policy']

## Alterando
df_cod = pd.get_dummies(data=df_cod, columns=colunas_dummies)


###############################################################################################

# Modelo de Previsão
## Função para avaliar o erro
def avaliar_modelo(nome_modelo, y_teste, previsao):
    r2 = r2_score(y_teste, previsao)
    RSME = np.sqrt(mean_squared_error(y_teste, previsao))
    return print(f'Modelo {nome_modelo}: \nR²:{r2}\nRSME:{RSME}')

## Modelos
modelo_rf = RandomForestRegressor()
modelo_lr = LinearRegression()
modelo_et = ExtraTreesRegressor()

modelos = {'RandomForest': RandomForestRegressor(),
           'LinearRegression': LinearRegression(),
           'ExtraTrees': ExtraTreesRegressor()}

y = df_cod['price']
x = df_cod.drop('price', axis=1)

## Separando entre treino e teste
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=10)

## Avaliando modelos
for nome_modelo, modelo in modelos.items():
    #Treinar
    modelo.fit(x_train, y_train)
    #Testar
    previsao = modelo.predict(x_test)
    print(avaliar_modelo(nome_modelo, y_test, previsao))

## Avaliação de importância de Features
modelo_et.fit(x_train, y_train)
modelo_et.feature_importances_

## Criando Dataframe para fazer melhor avaliação das features
importancia_features = pd.DataFrame(modelo_et.feature_importances_, x_train.columns)
importancia_features = importancia_features.sort_values(by=0, ascending=False)
importancia_features

## Gráfico para Análise das Features
plt.figure(figsize=(15,5))
ax = sns.barplot(x=importancia_features.index, y=importancia_features[0])
ax.tick_params(axis = 'x', rotation = 90)

## Excluindo a coluna is_is_business_travel_ready
df_cod = df_cod.drop('is_business_travel_ready', axis = 1)

## Excluindo a coluna number_of_reviews
df_cod = df_cod.drop('number_of_reviews', axis = 1)

## Testando novamente o modelo
y = df_cod['price']
x = df_cod.drop('price', axis=1)

## Separando entre treino e teste
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=10)

## Novo treinamento
modelo_et.fit(x_train, y_train)
previsao = modelo_et.predict(x_test)
avaliar_modelo(modelo_et, y_test, previsao)


## Removendo as colunas com bed_types
df_teste = df_cod.copy()

for coluna in df_teste:
    if 'bed_type' in coluna:
        df_teste = df_teste.drop(coluna, axis = 1)

## Retreinando o modelo
y = df_teste['price']
x = df_teste.drop('price', axis=1)


## Separando entre treino e teste
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=10)

## Novo treinamento
modelo_et.fit(x_train, y_train)
previsao = modelo_et.predict(x_test)
avaliar_modelo(modelo_et, y_test, previsao)


#######################################################################################
# Perpetuando o modelo em um arquivo

## Recolocando a variável y de volta à base x
x['price'] = y

### Salvando a base de dados tratada
x.to_csv(dados_csv, index=False)

x.head()

### Transformando o arquivo em um dump para ML
joblib.dump(modelo_et, modelo_joblib)
