import pandas as pd
import os
import time
import requests
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# --- 1. Coleta da API com Retry Exponencial ---
URL_METEOROLOGIA = "https://websempre.rio.rj.gov.br/json/dados_meteorologicos"

def ler_api(url, tentativas=3):
    for i in range(tentativas):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print("✅ Dados recebidos com sucesso.")
                return response.json()
            else:
                print(f"⚠️ Tentativa {i+1}: Erro {response.status_code}")
        except requests.RequestException as e:
            print(f"⚠️ Tentativa {i+1}: Falha na requisição: {e}")
        time.sleep(2 ** i)  # Retry exponencial

    print("❌ Todas as tentativas falharam.")
    return None

dados = ler_api(URL_METEOROLOGIA)
print(json.dumps(dados, indent=2))

def limpar_e_transformar(dados):
    if not dados:
        print("❌ Dados estão vazios ou nulos.")
        return None

    if not isinstance(dados, dict) or 'features' not in dados:
        print("❌ Estrutura de dados inesperada.")
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
            'tipo': props.get('type')
        }
        propriedades.append(props_flat)

    df = pd.DataFrame(propriedades)

    df.replace(to_replace=["N/D", "-", ""], value=pd.NA, inplace=True)
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\W+', '_', regex=True)

    colunas_data_possiveis = ['read_at', 'data', 'data_medicao', 'datahora']
    data_col = None
    for col in colunas_data_possiveis:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')
                data_col = col
                break
            except Exception:
                continue

    if data_col is None:
        print("❌ Nenhuma coluna de data válida encontrada.")
        return None

    df.dropna(subset=[data_col], inplace=True)
    df.rename(columns={data_col: 'data'}, inplace=True)

    for col in df.columns:
        if df[col].dtype == object and df[col].astype(str).str.contains(",", na=False).any():
            df[col] = df[col].astype(str).str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.rename(columns={
        'estacao_id': 'id',
        'temperature': 'temperatura_atual',
        'min': 'temperatura_min',
        'max': 'temperatura_max',
        'humidity': 'umidade',
        'pressure': 'pressao',
        'wind': 'vento'
    }, inplace=True)

    # Força os tipos
    colunas_float = ['temperatura_atual', 'temperatura_min', 'temperatura_max', 'umidade', 'pressao', 'vento']
    for col in colunas_float:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df
limpar_e_transformar(dados)
