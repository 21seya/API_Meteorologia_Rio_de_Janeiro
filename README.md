
# 🌦️ API de Meteorologia — Coleta e Armazenamento de Dados

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/21seya/API_Meteorologia_Rio_de_Janeiro)

> Pipeline para coleta contínua de dados meteorológicos, com armazenamento em Parquet e PostgreSQL.

---

## 📚 Sumário

- [📂 Estrutura de Arquivos](#-estrutura-de-arquivos)
- [🚀 Como Executar a Pipeline Principal](#-como-executar-a-pipeline-principal)
- [🔁 Coleta Contínua (Tempo Real)](#-coleta-contínua-tempo-real)
- [🧪 Como Rodar os Testes](#-como-rodar-os-testes)
- [🛠️ Configuração do Banco de Dados](#-configuração-do-banco-de-dados)
- [📈 Organização dos Dados em Parquet](#-organização-dos-dados-em-parquet)
- [📋 Requisitos Técnicos](#-requisitos-técnicos)
- [⚙️ Funcionalidades](#️-funcionalidades)

---

## 📂 Estrutura de Arquivos

- `pipeline_parquet.py` — Pipeline principal: coleta dados, limpa e armazena.
- `tempo_real.py` — Executa o pipeline em loop contínuo a cada X minutos.
- `test_pipeline_parquet.py` — Testes unitários com pytest.

---

## 🚀 Como Executar a Pipeline Principal

Clone o projeto:

```bash
git clone https://github.com/21seya/API_Meteorologia_Rio_de_Janeiro
cd seurepo
```

Instale as dependências:

```bash
pip install pandas sqlalchemy psycopg2 requests pytest
```

Execute a pipeline:

- **Salvar apenas em Parquet:**
  ```bash
  python pipeline_parquet.py --destino parquet
  ```

- **Salvar apenas no PostgreSQL:**
  ```bash
  python pipeline_parquet.py --destino postgres --conn "postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco"
  ```

- **Salvar em ambos:**
  ```bash
  python pipeline_parquet.py --destino ambos --conn "postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco"
  ```

---

## 🔁 Coleta Contínua (Tempo Real)

Execute o loop de coleta automática:

```bash
python tempo_real.py
```

> ℹ️ Por padrão, coleta a cada 2 minutos (pode ser alterado no `tempo_real.py`).

---

## 🧪 Como Rodar os Testes

Execute todos os testes unitários:

```bash
pytest test_pipeline_parquet.py -v
```

---

## 🛠️ Configuração do Banco de Dados

Antes de rodar o pipeline com PostgreSQL, crie a tabela:

```sql
CREATE TABLE meteorologia_estacoes (
    id INTEGER,
    estacao TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    temperatura_atual DOUBLE PRECISION,
    temperatura_min DOUBLE PRECISION,
    temperatura_max DOUBLE PRECISION,
    umidade DOUBLE PRECISION,
    pressao DOUBLE PRECISION,
    vento DOUBLE PRECISION,
    read_at TIMESTAMP WITH TIME ZONE,
    data TIMESTAMP WITH TIME ZONE,
    data_evento DATE
);
```

📌 Observação:

- A tabela não possui chave primária porque os dados chegam incrementalmente.
- Futuramente, pode-se adicionar uma constraint de unicidade:

```sql
UNIQUE (estacao, data)
```

---

## 📈 Organização dos Dados em Parquet

Os dados ficam organizados por data (`data_evento`):

```
parquet/
└── meteorologia_estacoes/
    ├── data_evento=2025-04-26/
    │   └── 2025-04-26.parquet
    ├── data_evento=2025-04-27/
    │   └── 2025-04-27.parquet
    └── ...
```

---

## 📋 Requisitos Técnicos

- Python 3.8+
- Bibliotecas utilizadas:
  - pandas
  - sqlalchemy
  - psycopg2
  - requests
  - pytest

---

## ⚙️ Funcionalidades

- Retry Exponencial em chamadas de API.
- Limpeza automática de campos nulos ou inválidos.
- Tipagem correta de dados (float, timestamp).
- Armazenamento particionado por data no Parquet.
- Inserção eficiente no PostgreSQL (`execute_values`).
- Execução incremental para evitar duplicações.

---
