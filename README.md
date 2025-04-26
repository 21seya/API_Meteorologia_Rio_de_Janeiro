🌦️ Pipeline de Coleta de Dados Meteorológicos


📂 Estrutura de Arquivos
pipeline_parquet.py — Pipeline principal: coleta dados, limpa e armazena.

tempo_real.py — Executa o pipeline em loop contínuo a cada X minutos.

test_pipeline_parquet.py — Conjunto de testes unitários com pytest.

🚀 Como Executar a Pipeline Principal
Clone o projeto:

bash
Copiar
Editar
git clone https://github.com/seuusuario/seurepo.git
cd seurepo
Instale as dependências:

bash
Copiar
Editar
pip install pandas sqlalchemy psycopg2 requests pytest
Execute a pipeline:

Salvar apenas em Parquet:

bash
Copiar
Editar
python pipeline_parquet.py --destino parquet
Salvar apenas no PostgreSQL:

bash
Copiar
Editar
python pipeline_parquet.py --destino postgres --conn "postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco"
Salvar em ambos:

bash
Copiar
Editar
python pipeline_parquet.py --destino ambos --conn "postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco"
🔁 Como Rodar Coleta Contínua (Tempo Real)
Execute o loop de coleta automática:

bash
Copiar
Editar
python tempo_real.py
Por padrão, coleta a cada 2 minutos (configurável no tempo_real.py).

🧪 Como Rodar os Testes
Rode todos os testes unitários:

bash
Copiar
Editar
pytest test_pipeline_parquet.py -v
🛠️ Exemplo de Criação de Tabela no PostgreSQL
Antes de rodar a opção --destino postgres ou ambos, você precisa ter a tabela no banco criada.

Aqui está um exemplo de DDL:

sql
Copiar
Editar
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
📌 Observações:

A tabela não tem chave primária porque os dados vêm incrementalmente.

Para melhorar, futuramente pode-se adicionar uma constraint de unicidade (UNIQUE (estacao, data)).

📈 Organização dos Dados no Parquet
yaml
Copiar
Editar
parquet/
└── meteorologia_estacoes/
    ├── data_evento=2025-04-26/
    │   └── 2025-04-26.parquet
    ├── data_evento=2025-04-27/
    │   └── 2025-04-27.parquet
    └── ...

📋 Requisitos Técnicos
Python 3.8+

Bibliotecas:

pandas

sqlalchemy

psycopg2

requests

pytest

📋 Funcionalidades
Retry Exponencial em chamadas de API.

Limpeza Automática de campos nulos ou inválidos.

Tipagem Correta (float, timestamp).

Armazenamento Particionado por data (data_evento) no Parquet.

Inserção em Banco de Dados usando psycopg2 otimizado (execute_values).

Execução Incremental: evita duplicação.