import os
import datetime
from typing import Optional
import pandas as pd

# Azure Identity and SDK imports
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.costmanagement import CostManagementClient
    from azure.mgmt.costmanagement.models import (
        QueryDefinition,
        QueryTimePeriod,
        QueryDataset,
        QueryGrouping,
        QueryAggregation
    )
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False

class AzureCostClient:
    """
    Cliente para integração com a API do Azure Cost Management.
    """
    
    def __init__(self, subscription_id: Optional[str] = None) -> None:
        """
        Inicializa o cliente do Azure Cost Management.
        
        Args:
            subscription_id (str, opcional): ID da Assinatura do Azure. Se omitido,
                                             busca da variável de ambiente AZURE_SUBSCRIPTION_ID.
        """
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
        self.client: Optional[CostManagementClient] = None
        self.credential = None

        if not AZURE_SDK_AVAILABLE:
            raise ImportError(
                "Bibliotecas da Azure não instaladas. "
                "Certifique-se de instalar 'azure-identity' e 'azure-mgmt-costmanagement'."
            )

    def autenticar(self) -> None:
        """
        Realiza a autenticação na API do Azure utilizando o DefaultAzureCredential.
        
        Raises:
            ValueError: Se o ID da assinatura não estiver configurado.
            Exception: Se falhar na autenticação ou inicialização do cliente.
        """
        if not self.subscription_id:
            raise ValueError(
                "AZURE_SUBSCRIPTION_ID não foi definido no ambiente ou construtor."
            )
            
        try:
            # DefaultAzureCredential tenta autenticar por CLI, Service Principal, Managed Identity, etc.
            self.credential = DefaultAzureCredential()
            self.client = CostManagementClient(credential=self.credential)
        except Exception as e:
            raise Exception(f"Falha na autenticação da Azure: {e}")

    def buscar_custos(self, dias: int = 30) -> pd.DataFrame:
        """
        Consulta os custos reais dos últimos N dias na API do Cost Management.
        
        Os dados são agrupados diariamente por Serviço (ServiceName) e Grupo de Recursos (ResourceGroupName).
        
        Args:
            dias (int): Número de dias anteriores para consulta. Default é 30.
            
        Returns:
            pd.DataFrame: DataFrame com colunas ['Date', 'Service', 'ResourceGroup', 'Cost', 'Currency']
            
        Raises:
            Exception: Se o cliente não estiver autenticado ou ocorrer erro na consulta à API.
        """
        if not self.client:
            raise Exception("Cliente Azure não autenticado. Chame o método 'autenticar()' primeiro.")

        # Definir período de tempo da consulta
        hoje = datetime.date.today()
        data_inicio = hoje - datetime.timedelta(days=dias)
        
        # Converter para datetime com UTC
        start_date = datetime.datetime(data_inicio.year, data_inicio.month, data_inicio.day, 0, 0, 0)
        end_date = datetime.datetime(hoje.year, hoje.month, hoje.day, 23, 59, 59)

        scope = f"/subscriptions/{self.subscription_id}"

        # Montar definição da query do Cost Management API
        query_def = QueryDefinition(
            type="ActualCost",
            timeframe="Custom",
            time_period=QueryTimePeriod(from_property=start_date, to=end_date),
            dataset=QueryDataset(
                granularity="Daily",
                aggregation={
                    "PreTaxCost": QueryAggregation(name="PreTaxCost", function="Sum")
                },
                grouping=[
                    QueryGrouping(type="Dimension", name="ServiceName"),
                    QueryGrouping(type="Dimension", name="ResourceGroupName"),
                    QueryGrouping(type="Dimension", name="ChargeType")
                ]
            )
        )

        try:
            # Chamar a API da Azure
            result = self.client.query.usage(scope=scope, parameters=query_def)
            
            # Converter a matriz de resultados em DataFrame
            if not result or not result.rows:
                return pd.DataFrame(columns=["Date", "Service", "ResourceGroup", "Cost", "Currency"])

            # Mapear os índices das colunas retornadas
            colunas_retornadas = [col.name for col in result.columns]
            
            # Índices de interesse
            idx_cost = colunas_retornadas.index("PreTaxCost") if "PreTaxCost" in colunas_retornadas else 0
            idx_date = colunas_retornadas.index("UsageDate") if "UsageDate" in colunas_retornadas else 1
            idx_service = colunas_retornadas.index("ServiceName") if "ServiceName" in colunas_retornadas else 2
            idx_rg = colunas_retornadas.index("ResourceGroupName") if "ResourceGroupName" in colunas_retornadas else 3
            idx_currency = colunas_retornadas.index("Currency") if "Currency" in colunas_retornadas else 4

            dados_formatados = []
            for row in result.rows:
                # Tratar data no formato retornado pela API (geralmente YYYYMMDD em int)
                data_bruta = row[idx_date]
                if isinstance(data_bruta, int):
                    data_str = str(data_bruta)
                    # Converter YYYYMMDD para YYYY-MM-DD
                    if len(data_str) == 8:
                        data_formatada = f"{data_str[0:4]}-{data_str[4:6]}-{data_str[6:8]}"
                    else:
                        data_formatada = data_str
                else:
                    data_formatada = str(data_bruta)

                custo = float(row[idx_cost])
                servico = str(row[idx_service])
                rg = str(row[idx_rg])
                moeda = str(row[idx_currency]) if idx_currency < len(row) else "USD"

                dados_formatados.append({
                    "Date": data_formatada,
                    "Service": servico,
                    "ResourceGroup": rg,
                    "Cost": custo,
                    "Currency": moeda
                })

            df = pd.DataFrame(dados_formatados)
            return df

        except Exception as e:
            raise Exception(f"Erro ao consultar a API de custos da Azure: {e}")
