import pytest
import pandas as pd
from pipeline_parquet import limpar_e_transformar

# --- Teste 1: Payload com campos ausentes ---
def test_limpar_e_transformar_campos_ausentes():
    payload_incompleto = {
        "features": [
            {
                "properties": {
                    "station": {"name": "Estação Teste"},
                    "data": {
                        "humidity": "85"
                    },
                    "read_at": "2024-04-25T12:00:00Z"
                },
                "geometry": {
                    "coordinates": [-43.2096, -22.9035]
                }
            }
        ]
    }

    df = limpar_e_transformar(payload_incompleto)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    expected_cols = {'id', 'estacao', 'latitude', 'longitude', 'umidade', 'data'}
    assert expected_cols.issubset(set(df.columns))

    assert pd.isna(df.loc[0, 'id'])
    assert df.loc[0, 'estacao'] == "Estação Teste"
    assert df.loc[0, 'latitude'] == -22.9035
    assert df.loc[0, 'longitude'] == -43.2096
    assert df.loc[0, 'umidade'] == 85.0

# --- Teste 2: Payload vazio ---
def test_limpar_e_transformar_payload_vazio():
    payload_vazio = {}

    df = limpar_e_transformar(payload_vazio)

    assert df is None, "Deveria retornar None para payload vazio"

# --- Teste 3: Payload sem 'features' ---
def test_limpar_e_transformar_sem_features():
    payload_sem_features = {"type": "FeatureCollection"}

    df = limpar_e_transformar(payload_sem_features)

    assert df is None, "Deveria retornar None se 'features' está ausente"

# --- Teste 4: Payload completo ---
def test_limpar_e_transformar_payload_completo():
    payload_completo = {
        "features": [
            {
                "properties": {
                    "station": {"id": 123, "name": "Estação Completa"},
                    "data": {
                        "temperature": "25.5",
                        "min": "20.0",
                        "max": "30.0",
                        "humidity": "70",
                        "pressure": "1013",
                        "wind": "5.0"
                    },
                    "read_at": "2024-04-25T15:00:00Z"
                },
                "geometry": {
                    "coordinates": [-43.1729, -22.9068]
                }
            }
        ]
    }

    df = limpar_e_transformar(payload_completo)

    assert df is not None
    assert isinstance(df, pd.DataFrame)

    # Checa se os valores estão corretos
    assert df.loc[0, 'id'] == 123
    assert df.loc[0, 'temperatura_atual'] == 25.5
    assert df.loc[0, 'temperatura_min'] == 20.0
    assert df.loc[0, 'temperatura_max'] == 30.0
    assert df.loc[0, 'umidade'] == 70.0
    assert df.loc[0, 'pressao'] == 1013.0
    assert df.loc[0, 'vento'] == 5.0
    assert df.loc[0, 'latitude'] == -22.9068
    assert df.loc[0, 'longitude'] == -43.1729
