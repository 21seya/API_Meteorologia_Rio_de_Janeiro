from sqlalchemy import create_engine
#from sqlalchemy import String, Float, Date, TIMESTAMP
import sqlalchemy
import pandas as pd
import os
import time
import requests
import argparse
import json
import csv

# URL da API
URL_METEOROLOGIA = "https://websempre.rio.rj.gov.br/json/dados_meteorologicos"

# --- Função para ler a API com Retry Exponencial ---
def ler_api(url, tentativas=3):
    '''
    Função que ler os dados da API caso der ok status 200 senão falha na execução.
    '''
    for i in range(tentativas):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print("Dados recebidos com sucesso.")
                return response.json()
            else:
                print(f"Tentativa {i+1}: Erro {response.status_code}")
        except requests.RequestException as e:
            print(f"Tentativa {i+1}: Falha na requisição: {e}")
        time.sleep(2 ** i)

    print("Todas as tentativas falharam.")
    return None

def limpar_e_transformar(dados):
    '''
    Função que faz limpeza de dados e transformações e criando novas colunas para tanto armazenar 
    em parquet e no banco de dados
    '''
    if not dados or 'features' not in dados:
        print("Dados vazios ou estrutura inesperada.")
        return None

    propriedades = []
    for feature in dados['features']:
        props = feature.get('properties', {})
        coords = feature.get('geometry', {}).get('coordinates', [None, None])
        station = props.get('station', {})
        data = props.get('data', {})

        props_flat = {
            **data,
            'estacao_id': station.get('id'),
            'estacao': station.get('name'),
            'latitude': coords[1],
            'longitude': coords[0],
            'read_at': props.get('read_at'),
        }
        propriedades.append(props_flat)

    df = pd.DataFrame(propriedades)

    df.replace(to_replace=["N/D", "-", ""], value=pd.NA, inplace=True)
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\W+', '_', regex=True)

    if 'read_at' in df.columns:
        df['data'] = pd.to_datetime(df['read_at'], utc=True, errors='coerce')
    else:
        print("Coluna de data não encontrada.")
        return None

    df.dropna(subset=['data'], inplace=True)

    renomear = {
        'estacao_id': 'id',
        'temperature': 'temperatura_atual',
        'min': 'temperatura_min',
        'max': 'temperatura_max',
        'humidity': 'umidade',
        'pressure': 'pressao',
        'wind': 'vento'
    }
    df.rename(columns=renomear, inplace=True)

    # --- FORÇA QUE TODAS AS COLUNAS ESPERADAS EXISTAM ---
    colunas_float = ['temperatura_atual', 'temperatura_min', 'temperatura_max', 'umidade', 'pressao', 'vento']
    for col in colunas_float:
        if col not in df.columns:
            df[col] = pd.NA  # cria a coluna com NaN se não existir
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# --- Persistência em Parquet ---
def salvar_parquet(df, tabela_nome, data_col):
    '''
    Função que armazena os dados vindo da API em parquet
    '''
    df[data_col] = pd.to_datetime(df[data_col])
    df['data_evento'] = df[data_col].dt.strftime('%Y-%m-%d')

    caminho_base = f"parquet/{tabela_nome}"
    os.makedirs(caminho_base, exist_ok=True)

    for data_unica in df['data_evento'].unique():
        df_dia = df[df['data_evento'] == data_unica]
        caminho_arquivo = os.path.join(caminho_base, f"data_evento={data_unica}", f"{data_unica}.parquet")
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        df_dia.to_parquet(caminho_arquivo, index=False)

    print(f"Dados salvos em Parquet: {caminho_base}")

# --- Persistência no PostgreSQL ---
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

def salvar_postgres(df, tabela_nome, conn_string):
    '''
    Função que armazena no postgresql usando pyscopg2
    '''
    # Usa SQLAlchemy para criar engine e pegar conexão do psycopg2
    engine = create_engine(conn_string)
    conn = engine.raw_connection()
    cursor = conn.cursor()

    # Preparar dados para inserção
    cols = df.columns.tolist()
    values = df.values.tolist()

    insert_query = f"INSERT INTO {tabela_nome} ({', '.join(cols)}) VALUES %s"
    try:
        from psycopg2.extras import execute_values
        execute_values(cursor, insert_query, values)
        conn.commit()
        print(f"Dados salvos no PostgreSQL (psycopg2): {tabela_nome}")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar no PostgreSQL: {e}")
    finally:
        cursor.close()
        conn.close()

# --- 5. Evitar duplicatas (incremental com Parquet) ---
def remover_registros_existentes(df_novo, caminho_base, chave):
    '''
    Função que remove registros caso exista
    '''
    df_novo['data_evento'] = pd.to_datetime(df_novo['data']).dt.strftime('%Y-%m-%d')
    datas_novas = df_novo['data_evento'].unique()
    registros_existentes = []

    for data_str in datas_novas:
        pasta_particionada = os.path.join(caminho_base, f"data_evento={data_str}")
        if os.path.exists(pasta_particionada):
            arquivos = [os.path.join(pasta_particionada, f) for f in os.listdir(pasta_particionada) if f.endswith('.parquet')]
            for arquivo in arquivos:
                df_existente = pd.read_parquet(arquivo)
                registros_existentes.append(df_existente)

    if not registros_existentes:
        return df_novo

    df_existente_total = pd.concat(registros_existentes, ignore_index=True)
    if not all(col in df_existente_total.columns for col in chave):
        return df_novo

    df_merged = df_novo.merge(df_existente_total[chave], on=chave, how='left', indicator=True)
    df_filtrado = df_merged[df_merged['_merge'] == 'left_only'].drop(columns=['_merge'])

    return df_filtrado

# --- Pipeline principal ---
def executar_pipeline(destino='parquet', conn_string=None):
    '''
    Função de pipeline principal onde ler e limpa os dados armazena no 
    arquivo parquet e banco de dados
    '''
    dados = ler_api(URL_METEOROLOGIA)
    df = limpar_e_transformar(dados)

    if df is not None and not df.empty:
        if destino == 'parquet':
            salvar_parquet(df, "meteorologia_estacoes", 'data')
        elif destino == 'postgres' and conn_string:
            salvar_postgres(df, "meteorologia_estacoes", conn_string)
        elif destino == 'ambos' and conn_string:
            salvar_parquet(df, "meteorologia_estacoes", 'data')
            salvar_postgres(df, "meteorologia_estacoes", conn_string)
        else:
            print("Destino inválido ou falta conexão com banco.")
    else:
        print("Nenhum dado coletado ou processado.")

def main():
    '''
    Função principal
    '''
    parser = argparse.ArgumentParser(description="Pipeline de coleta de dados meteorológicos")
    parser.add_argument('--destino', choices=['parquet', 'postgres', 'ambos'], default='parquet', help="Destino dos dados")
    parser.add_argument('--conn', help="Connection string para PostgreSQL")
    args = parser.parse_args()

    executar_pipeline(destino=args.destino, conn_string=args.conn)

if __name__ == "__main__":
    main()
