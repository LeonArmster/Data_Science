# Bibliotecas
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from config import dataset_dir, env_file


pd.set_option('display.max_columns', None)

# Importando as bases de dados
caminho_bases = dataset_dir
df_airbnb = pd.DataFrame()

# Adicionando os meses e anos nas colunas do dataframe
meses = {'jan':1, 'fev':2, 'mar':3, 'abr':4, 'mai':5, 'jun':6, 'jul':7, 'ago':8, 'set':9, 'out':10, 'nov':11, 'dez':12}

# Juntando os dataframes
for arquivo in caminho_bases.iterdir():
    # Separando o mês através do nome dos arquivos
    nome_mes = arquivo.name[:3]
    mes = meses[nome_mes]
    
    # Separando o ano através do nome do arquivo
    ano = arquivo.name[-8:]
    ano = int(ano.replace('.csv', ''))

    # Lendo o dataframe
    df = pd.read_csv(caminho_bases / arquivo.name, encoding='utf-8')
    # Criando as colunas ano e mes
    df['mes'] = mes
    df['ano'] = ano
    # Juntando os dataframes
    df_airbnb = pd.concat([df_airbnb, df])

df_airbnb.head()

# Analisando colunas e excluindo não usadas
## Faremos a exclusão das colunas que não são necessárias(Regras explicadas no readme)
### Colunas finais que serão utilizadas
colunas = ['host_is_superhost','host_listings_count','latitude','longitude','property_type','room_type','accommodates','bathrooms','bedrooms','beds','bed_type','amenities','price','guests_included','extra_people','minimum_nights','maximum_nights','number_of_reviews','instant_bookable','is_business_travel_ready','cancellation_policy','ano','mes']

### Filtrando as colunas necessárias
df = df_airbnb[colunas]

# Tratando valores vazios
## Validando os valores nulos por coluna
df.isnull().sum()

## Excluindo as colunas com dados vazios já que a quantidade de valores máximos será excluída apenas 2500 linhas de um total de 900.000
df = df.dropna()
df.shape

# Validando os tipos de dados
df.dtypes

# Price, extra_people estão sendo reconhecidos como string ao invés de float. Fazendo a correção
df['price'] = df['price'].str.replace('$','')
df['price'] = df['price'].str.replace(',','')
df['price'] = df['price'].astype('float32')
df['extra_people'] = df['extra_people'].str.replace('$','')
df['extra_people'] = df['extra_people'].str.replace(',','')
df['extra_people'] = df['extra_people'].astype('float32')

# Convertendo os valores floats desnecessários para int
df['host_listings_count'] = df['host_listings_count'].astype(int)
df['bathrooms'] = df['bathrooms'].astype(int)
df['bedrooms'] = df['bedrooms'].astype(int)
df['beds'] = df['beds'].astype(int)
df['guests_included'] = df['guests_included'].astype(int)
df['extra_people'] = df['extra_people'].astype(int)

###############################################################################################################################################################
# Inserindo os dados no servidor
## Conectando ao servidor
### Lendo o caminho do arquivo onde estão salvas as configurações do acesso ao servidor
load_dotenv(dotenv_path=env_file)

### Carregando as configurações
database = os.getenv("bd").lower()
user = os.getenv("usuario")
password = os.getenv("senha")
hostname = os.getenv("host")
porta = os.getenv("port")

### String para consolidar as informações de conexão
database_url = f'postgresql+psycopg2://{user}:{password}@{hostname}:{porta}/{database}'

### Engine de conexão ao banco
engine = create_engine(database_url)

### Inserindo os dados no servidor
with engine.connect() as conexao:
    # comando para inserir de maneira segura dentro de uma transação
    transacao = conexao.begin()
    try:
        # comando para criar tabela e inserir os dados no banco
        df.to_sql('tb_dados_imobiliarios', con=conexao, index=False, if_exists='replace',chunksize=20)
        # Salvar os dados na tabela caso não haja problema
        transacao.commit()
    except:
        # Dar rollback no processo caso aconteça qualquer problema na inserção
        transacao.rollback()
        raise
