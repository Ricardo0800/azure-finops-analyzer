import datetime
import math
from typing import List, Dict, Any
import pandas as pd

def carregar_dados_exemplo() -> pd.DataFrame:
    """
    Gera um DataFrame do Pandas contendo dados de custo simulados e realistas do Azure.
    
    Os valores totais por serviço são projetados para somar exatamente os R$ 847,32 
    do exemplo, com a seguinte distribuição:
      1. Virtual Machines: R$ 412,10 (48.6%)
      2. Azure SQL Database: R$ 198,44 (23.4%)
      3. Storage: R$ 121,33 (14.3%)
      4. App Service: R$ 89,22 (10.5%)
      5. Azure Monitor: R$ 26,23 (3.1%)
      
    Além disso, simula um aumento de ~12% no custo de Storage nos últimos 7 dias.

    Retorna:
        pd.DataFrame: DataFrame com as colunas ['Date', 'Service', 'ResourceGroup', 'Cost', 'Currency']
    """
    # Configuração de metas de custo por serviço
    servicos_config = {
        "Virtual Machines": {
            "total": 412.10,
            "rgs": [("rg-prod-compute", 0.8), ("rg-stage-compute", 0.2)]
        },
        "Azure SQL Database": {
            "total": 198.44,
            "rgs": [("rg-prod-databases", 1.0)]
        },
        "Storage": {
            "total": 121.33,
            "rgs": [("rg-prod-storage", 1.0)]
        },
        "App Service": {
            "total": 89.22,
            "rgs": [("rg-shared-infra", 1.0)]
        },
        "Azure Monitor": {
            "total": 26.23,
            "rgs": [("rg-monitoring", 1.0)]
        }
    }

    datas: List[str] = []
    # Período de 01/06/2026 a 30/06/2026
    data_inicio = datetime.date(2026, 6, 1)
    dias = 30
    
    lista_dados: List[Dict[str, Any]] = []

    # Dicionário para acumular os valores já gerados para cada serviço
    custos_acumulados = {servico: 0.0 for servico in servicos_config}

    for dia_idx in range(dias):
        data_atual = data_inicio + datetime.timedelta(days=dia_idx)
        data_str = data_atual.strftime("%Y-%m-%d")
        dia_num = dia_idx + 1

        for servico, config in servicos_config.items():
            total_alvo = config["total"]
            
            # Se for o último dia, ajustamos para garantir que a soma seja EXATA
            if dia_idx == dias - 1:
                custo_dia = round(total_alvo - custos_acumulados[servico], 2)
            else:
                # Comportamento padrão para cada serviço
                if servico == "Virtual Machines":
                    # Flutuação diária baseada em seno para simular cargas variáveis de VMs
                    fator = 1.0 + 0.12 * math.sin(dia_num)
                    custo_dia = (total_alvo / dias) * fator
                elif servico == "Azure SQL Database":
                    # Flutuação estável de banco de dados
                    fator = 1.0 + 0.05 * math.cos(dia_num * 0.5)
                    custo_dia = (total_alvo / dias) * fator
                elif servico == "Storage":
                    # Simular crescimento linear de 12% nos últimos 7 dias.
                    # Dias 1-23: estável em torno de um patamar menor.
                    # Dias 24-30: crescimento diário acumulativo.
                    if dia_num >= 24:
                        # Crescimento nos últimos 7 dias
                        fator = 1.12 + 0.02 * (dia_num - 24)
                    else:
                        fator = 0.95 + 0.01 * math.sin(dia_num)
                    
                    custo_dia = (total_alvo / dias) * fator
                elif servico == "App Service":
                    # Pouca variação diária (plano App Service Plan fixo)
                    fator = 1.0 + 0.02 * math.sin(dia_num * 2)
                    custo_dia = (total_alvo / dias) * fator
                elif servico == "Azure Monitor":
                    # Volume de logs varia bastante
                    fator = 1.0 + 0.3 * math.cos(dia_num)
                    custo_dia = (total_alvo / dias) * fator
                else:
                    custo_dia = total_alvo / dias
                
                custo_dia = round(custo_dia, 2)
            
            # Atualiza acumulado
            custos_acumulados[servico] += custo_dia
            
            # Distribui o custo do dia entre os Resource Groups configurados para o serviço
            for rg, proporcao in config["rgs"]:
                custo_rg = round(custo_dia * proporcao, 2)
                lista_dados.append({
                    "Date": data_str,
                    "Service": servico,
                    "ResourceGroup": rg,
                    "Cost": custo_rg,
                    "Currency": "BRL"
                })

    # Criamos o DataFrame
    df = pd.DataFrame(lista_dados)
    
    # Pequena correção final de arredondamento geral no DataFrame
    # Para garantir que a soma dos custos no DF final seja exatamente a soma dos totais alvo
    soma_alvo = sum(c["total"] for c in servicos_config.values())
    soma_atual = df["Cost"].sum()
    diferenca = round(soma_alvo - soma_atual, 2)
    
    if diferenca != 0.0:
        # Aplica a diferença no último registro do maior serviço para compensar arredondamento de RG
        df.iloc[-1, df.columns.get_loc("Cost")] = round(df.iloc[-1]["Cost"] + diferenca, 2)
        
    return df

if __name__ == "__main__":
    df = carregar_dados_exemplo()
    print("Total:", df["Cost"].sum())
    print(df.groupby("Service")["Cost"].sum())
    print(df.head())
