import os
import datetime
import pandas as pd
from typing import Dict, Any

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

class ReportGenerator:
    """
    Classe responsável por gerar relatórios financeiros e planilhas formatadas
    com os resultados da análise FinOps.
    """

    def __init__(self, data_analise: str = None) -> None:
        """
        Inicializa o gerador de relatórios.
        
        Args:
            data_analise (str): String que representa a data de geração do relatório (ex: '20260630').
                                Se não fornecida, usará a data atual.
        """
        if data_analise:
            self.data_sufixo = data_analise
        else:
            hoje = datetime.date.today()
            self.data_sufixo = hoje.strftime("%Y%M%d")

    def exportar_csv(self, df_bruto: pd.DataFrame, diretorio: str = ".") -> str:
        """
        Exporta os dados brutos de custos para um arquivo CSV.
        
        Args:
            df_bruto (pd.DataFrame): Dados completos e não agrupados.
            diretorio (str): Diretório onde o arquivo será salvo.
            
        Returns:
            str: Caminho completo do arquivo gerado.
        """
        nome_arquivo = f"custos_{self.data_sufixo}.csv"
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        
        df_bruto.to_csv(caminho_completo, index=False, encoding="utf-8")
        return caminho_completo

    def estilizar_cabecalho(self, ws) -> None:
        """
        Aplica estilo premium (fundo escuro, texto branco, negrito) à primeira linha (cabeçalho)
        da worksheet informada.
        """
        fill_cabecalho = PatternFill(start_color="203764", end_color="203764", fill_type="solid")
        font_cabecalho = Font(color="FFFFFF", bold=True)
        
        for cell in ws[1]:
            cell.fill = fill_cabecalho
            cell.font = font_cabecalho
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        # Ajustar tamanho das colunas baseado no cabeçalho
        for col in ws.columns:
            max_length = 0
            column_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 5)
            ws.column_dimensions[column_letter].width = adjusted_width

    def gerar_excel(self, 
                    resumo: Dict[str, Any], 
                    df_servico_rg: pd.DataFrame, 
                    df_diario: pd.DataFrame, 
                    diretorio: str = ".") -> str:
        """
        Gera um relatório executivo Excel (.xlsx) contendo 3 abas:
        - Resumo Executivo
        - Custo por Serviço
        - Evolução Diária (com gráfico de barras)
        
        Args:
            resumo (Dict): Retorno do método compilar_resumo() do Analyzer.
            df_servico_rg (pd.DataFrame): Dados agrupados por Serviço e RG.
            df_diario (pd.DataFrame): Dados agrupados por data.
            diretorio (str): Caminho onde o Excel será salvo.
            
        Returns:
            str: Caminho completo do arquivo gerado.
        """
        nome_arquivo = f"relatorio_{self.data_sufixo}.xlsx"
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        
        wb = Workbook()
        
        # -------------------------------------------------------------
        # ABA 1: Resumo Executivo
        # -------------------------------------------------------------
        ws_resumo = wb.active
        ws_resumo.title = "Resumo Executivo"
        
        # Título principal
        ws_resumo["A1"] = "AZURE FINOPS ANALYZER - RESUMO EXECUTIVO"
        ws_resumo["A1"].font = Font(size=16, bold=True, color="203764")
        
        # Informações Gerais
        ws_resumo["A3"] = "Período Analisado:"
        ws_resumo["B3"] = f"{resumo['period_start']} a {resumo['period_end']}"
        ws_resumo["A4"] = "Custo Total:"
        ws_resumo["B4"] = f"R$ {resumo['total_cost']:,.2f}"
        
        for row in range(3, 5):
            ws_resumo[f"A{row}"].font = Font(bold=True)
            
        # Top Serviços
        ws_resumo["A6"] = "Top Serviços (Maior Custo)"
        ws_resumo["A6"].font = Font(size=12, bold=True)
        
        linha_atual = 7
        ws_resumo[f"A{linha_atual}"] = "Serviço"
        ws_resumo[f"B{linha_atual}"] = "Custo (R$)"
        ws_resumo[f"C{linha_atual}"] = "Representação (%)"
        
        fill_subcab = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        for col in ["A", "B", "C"]:
            ws_resumo[f"{col}{linha_atual}"].fill = fill_subcab
            ws_resumo[f"{col}{linha_atual}"].font = Font(bold=True)
        
        linha_atual += 1
        for srv in resumo["top_services"]:
            ws_resumo[f"A{linha_atual}"] = srv["Service"]
            ws_resumo[f"B{linha_atual}"] = srv["Cost"]
            ws_resumo[f"C{linha_atual}"] = srv["Percentage"]
            ws_resumo[f"B{linha_atual}"].number_format = '#,##0.00'
            ws_resumo[f"C{linha_atual}"].number_format = '0.0"%"'
            linha_atual += 1
            
        # Sugestões de Otimização
        linha_atual += 2
        ws_resumo[f"A{linha_atual}"] = "⚠️ Sugestões de Otimização"
        ws_resumo[f"A{linha_atual}"].font = Font(size=12, bold=True, color="C00000")
        
        linha_atual += 1
        for sug in resumo["suggestions"]:
            ws_resumo[f"A{linha_atual}"] = f"• {sug}"
            linha_atual += 1
            
        ws_resumo.column_dimensions["A"].width = 50
        ws_resumo.column_dimensions["B"].width = 20
        ws_resumo.column_dimensions["C"].width = 20

        # -------------------------------------------------------------
        # ABA 2: Custo por Serviço
        # -------------------------------------------------------------
        ws_servicos = wb.create_sheet(title="Custo por Serviço")
        for row in dataframe_to_rows(df_servico_rg, index=False, header=True):
            ws_servicos.append(row)
            
        self.estilizar_cabecalho(ws_servicos)
        # Formatação de moeda na coluna de custo (Assumindo que é a coluna C ou 3)
        for row in range(2, ws_servicos.max_row + 1):
            ws_servicos.cell(row=row, column=3).number_format = '#,##0.00'

        # -------------------------------------------------------------
        # ABA 3: Evolução Diária (com gráfico)
        # -------------------------------------------------------------
        ws_evolucao = wb.create_sheet(title="Evolução Diária")
        for row in dataframe_to_rows(df_diario, index=False, header=True):
            ws_evolucao.append(row)
            
        self.estilizar_cabecalho(ws_evolucao)
        for row in range(2, ws_evolucao.max_row + 1):
            ws_evolucao.cell(row=row, column=2).number_format = '#,##0.00'
            
        # Adicionar o Gráfico de Barras
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Evolução Diária de Custos"
        chart.y_axis.title = "Custo (R$)"
        chart.x_axis.title = "Data"
        chart.width = 18
        chart.height = 9
        
        # As categorias (Datas) estão na Coluna 1. Os valores (Custo) estão na Coluna 2.
        dados = Reference(ws_evolucao, min_col=2, min_row=1, max_row=ws_evolucao.max_row)
        categorias = Reference(ws_evolucao, min_col=1, min_row=2, max_row=ws_evolucao.max_row)
        
        chart.add_data(dados, titles_from_data=True)
        chart.set_categories(categorias)
        
        # Posicionar o gráfico a partir da célula D2
        ws_evolucao.add_chart(chart, "D2")
        
        wb.save(caminho_completo)
        return caminho_completo
