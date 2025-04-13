# Bibliotecas
from pathlib import Path

# Caminho base do projeto
base_dir = Path(__file__).resolve().parent.parent.parent

# Diretórios
arquivos_dir = base_dir/'Arquivos'
codes_dir = base_dir/'Codes'
python_scripts_dir = codes_dir/'Python_Scripts'
sql_scripts_dir = codes_dir/'Sql_Scripts'
dataset_dir = base_dir/'Dataset'
imagens_dir = base_dir/'Imagens'

# Arquivos Especificos
modelo_joblib = arquivos_dir/'modelo.joblib'
dados_csv = arquivos_dir/'dados.csv'
env_file = base_dir/'conexao.env'

# SQL especifico
sql_select = sql_scripts_dir/'Select.sql'
