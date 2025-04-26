# 🌦️ Pipeline de Coleta de Dados Meteorológicos

## 📂 Estrutura de Arquivos
- `pipeline_parquet.py` — Pipeline principal: coleta dados, limpa e armazena.
- `tempo_real.py` — Executa o pipeline em loop contínuo a cada X minutos.
- `test_pipeline_parquet.py` — Conjunto de testes unitários com pytest.

---

## 🚀 Como Executar a Pipeline Principal

Clone o projeto:

```bash
git clone https://github.com/21seya/API_Meteorologia_Rio_de_Janeiro
cd seurepo


Instale as dependências:
pip install pandas sqlalchemy psycopg2 requests pytest


Salvar apenas em Parquet:
python pipeline_parquet.py --destino parquet

Salvar apenas no PostgreSQL:
python pipeline_parquet.py --destino postgres --conn "postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco"

Salvar em ambos:
python pipeline_parquet.py --destino ambos --conn "postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco"
---

## 🔁 Como Rodar Coleta Contínua (Tempo Real)

Execute o loop de coleta automática:

```bash
python tempo_real.py
