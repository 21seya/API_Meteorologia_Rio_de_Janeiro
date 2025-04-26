#Criação da tabela 

CREATE TABLE meteorologia_estacoes (
    id TEXT,
    estacao TEXT,
    temperatura_atual FLOAT,
    temperatura_min FLOAT,
    temperatura_max FLOAT,
    umidade FLOAT,
    pressao FLOAT,
    vento FLOAT,
    data_evento DATE,
    latitude varchar(255),
    longitude varchar(255),
    read_at date,
    data TIMESTAMP WITH TIME ZONE
);

#Seleciona todas as colunas 
select * from meteorologia_estacoes;
