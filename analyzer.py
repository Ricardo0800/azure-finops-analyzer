import pandas as pd
from typing import Dict, Any, List, Tuple

class FinOpsAnalyzer:
    """
    Classe responsável por processar e analisar os dados brutos de custo da Azure,
    gerando insights, relatórios resumidos e sugestões de otimização (FinOps).
    """

    def __init__(self, df_custos: pd.DataFrame) -> None:
        """
        Inicializa o analisador com os dados de custo.
        
        Args:
            df_custos (pd.DataFrame): DataFrame contendo as colunas ['Date', 'Service', 'ResourceGroup', 'Cost', 'Currency']
        """
        self.df = df_custos
        
        # Garante que as colunas essenciais existem, mesmo se o DF estiver vazio
        colunas_necessarias = {"Date", "Service", "ResourceGroup", "Cost"}
        if not colunas_necessarias.issubset(self.df.columns):
            raise ValueError(f"O DataFrame deve conter as colunas: {colunas_necessarias}")

        # Opcional: Garante que 'Cost' é numérico e remove NaNs
        self.df["Cost"] = pd.to_numeric(self.df["Cost"], errors='coerce').fillna(0)

    def obter_periodo(self) -> Tuple[str, str]:
        """
        Retorna a data de início e fim do período analisado.
        
        Returns:
            Tuple[str, str]: (data_inicio, data_fim) no formato YYYY-MM-DD. Se vazio, retorna strings vazias.
        """
        if self.df.empty:
            return ("", "")
        
        datas = sorted(self.df["Date"].unique())
        return (str(datas[0]), str(datas[-1]))

    def calcular_total(self) -> float:
        """
        Calcula o gasto total do período.
        
        Returns:
            float: Gasto total arredondado para 2 casas decimais.
        """
        return round(self.df["Cost"].sum(), 2)

    def obter_top_servicos(self, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna os 'N' serviços mais caros e seu percentual em relação ao total.
        
        Args:
            limite (int): Quantidade de serviços a retornar.
            
        Returns:
            List[Dict]: Lista de dicionários com 'Service', 'Cost' e 'Percentage'.
        """
        if self.df.empty:
            return []

        total_geral = self.calcular_total()
        if total_geral == 0:
            return []

        df_servicos = self.df.groupby("Service")["Cost"].sum().reset_index()
        df_servicos = df_servicos.sort_values(by="Cost", ascending=False).head(limite)

        top_servicos = []
        for _, row in df_servicos.iterrows():
            custo = row["Cost"]
            percentual = (custo / total_geral) * 100
            top_servicos.append({
                "Service": row["Service"],
                "Cost": round(custo, 2),
                "Percentage": round(percentual, 1)
            })

        return top_servicos

    def obter_custo_por_servico_rg(self) -> pd.DataFrame:
        """
        Agrupa os custos por Serviço e Resource Group.
        
        Returns:
            pd.DataFrame: DataFrame sumarizado.
        """
        if self.df.empty:
            return pd.DataFrame()
            
        df_agrupado = self.df.groupby(["Service", "ResourceGroup"])["Cost"].sum().reset_index()
        df_agrupado = df_agrupado.sort_values(by=["Service", "Cost"], ascending=[True, False])
        return df_agrupado

    def obter_evolucao_diaria(self) -> pd.DataFrame:
        """
        Agrupa os custos totais por data para mostrar a evolução dia a dia.
        
        Returns:
            pd.DataFrame: DataFrame com as colunas 'Date' e 'Cost', ordenado por data.
        """
        if self.df.empty:
            return pd.DataFrame()
            
        df_diario = self.df.groupby("Date")["Cost"].sum().reset_index()
        df_diario = df_diario.sort_values(by="Date")
        return df_diario

    def gerar_sugestoes_otimizacao(self) -> List[str]:
        """
        Gera sugestões de otimização automáticas baseadas nos padrões de custo encontrados.
        
        Returns:
            List[str]: Lista de strings contendo as sugestões formatadas.
        """
        sugestoes = []
        if self.df.empty:
            return sugestoes

        top_servicos = self.obter_top_servicos()
        df_diario_servicos = self.df.groupby(["Date", "Service"])["Cost"].sum().reset_index()

        # 1. Regra para Virtual Machines com alto percentual
        for servico in top_servicos:
            if servico["Service"] == "Virtual Machines" and servico["Percentage"] > 40.0:
                sugestoes.append(
                    f"Virtual Machines representam {servico['Percentage']}% do custo. "
                    "Verifique VMs paradas ou ociosas (Right-sizing/Desligamento)."
                )

        # 2. Regra para Banco de Dados
        for servico in top_servicos:
            if servico["Service"] in ["Azure SQL Database", "SQL Database"] and servico["Percentage"] > 20.0:
                sugestoes.append(
                    f"{servico['Service']} representa {servico['Percentage']}% do custo. "
                    "Considere analisar Reservas de Capacidade para economizar."
                )

        # 3. Regra de crescimento de Storage nos últimos 7 dias
        df_storage = df_diario_servicos[df_diario_servicos["Service"] == "Storage"].sort_values(by="Date")
        if len(df_storage) >= 14:
            # Pega últimos 7 dias e os 7 dias anteriores
            ultimos_7 = df_storage.tail(7)["Cost"].sum()
            anteriores_7 = df_storage.iloc[-14:-7]["Cost"].sum()
            
            if anteriores_7 > 0:
                crescimento_percentual = ((ultimos_7 - anteriores_7) / anteriores_7) * 100
                if crescimento_percentual > 5.0:
                    sugestoes.append(
                        f"Storage com crescimento de {crescimento_percentual:.0f}% nos últimos 7 dias. "
                        "Considere revisar políticas de retenção e blobs não utilizados."
                    )

        # Se nenhuma sugestão foi gerada, dá uma genérica
        if not sugestoes and top_servicos:
            sugestoes.append(
                f"Acompanhe o consumo de {top_servicos[0]['Service']}, "
                "que é atualmente a sua maior fonte de custos."
            )

        return sugestoes

    def compilar_resumo(self) -> Dict[str, Any]:
        """
        Compila todas as métricas principais num único dicionário.
        
        Returns:
            Dict: Dicionário contendo os KPIs e insights gerais.
        """
        inicio, fim = self.obter_periodo()
        return {
            "period_start": inicio,
            "period_end": fim,
            "total_cost": self.calcular_total(),
            "top_services": self.obter_top_servicos(),
            "suggestions": self.gerar_sugestoes_otimizacao()
        }
