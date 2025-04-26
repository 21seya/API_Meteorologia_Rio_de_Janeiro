import time
from datetime import datetime
from pipeline_parquet import ler_api, limpar_e_transformar, remover_registros_existentes, salvar_parquet

INTERVALO_MINUTOS = 2  # você pode ajustar para 1, 2, 10, etc.

def loop_tempo_real():
    while True:
        print(f"\n⏱ Iniciando nova coleta: {datetime.now().isoformat()}")
        dados = ler_api("https://websempre.rio.rj.gov.br/json/dados_meteorologicos")
        df = limpar_e_transformar(dados)

        if df is not None and not df.empty:
            df = remover_registros_existentes(df, "parquet/meteorologia_estacoes", ['estacao', 'data'])
            if not df.empty:
                salvar_parquet(df, "meteorologia_estacoes", 'data')
            else:
                print("Nenhum dado novo encontrado. Aguardando próximo ciclo.")
        else:
            print("Nenhum dado válido coletado.")

        print(f" Aguardando {INTERVALO_MINUTOS} minutos para nova execução...\n")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    loop_tempo_real()
