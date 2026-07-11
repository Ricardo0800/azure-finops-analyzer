import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

# Importando módulos locais
from azure_client import AzureCostClient
from sample_data import carregar_dados_exemplo
from analyzer import FinOpsAnalyzer
from report import ReportGenerator

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

def formatar_moeda(valor: float) -> str:
    """Formata um float para o padrão de moeda do Brasil (R$ XX,XX)."""
    # Adicionamos espaços de alinhamento para o terminal
    str_val = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    # Retorna com alinhamento de 8 caracteres
    return f"{str_val:>8}"

def main():
    # 1. Carregamento / Coleta de Dados
    dias_analise = int(os.getenv("ANALYSIS_DAYS", "30"))
    dados_brutos = None

    try:
        # Tenta conectar na API real do Azure
        cliente = AzureCostClient()
        cliente.autenticar()
        # console.print("[yellow]Buscando dados na Azure API...[/yellow]")
        dados_brutos = cliente.buscar_custos(dias=dias_analise)
        if dados_brutos.empty:
            raise Exception("Retorno vazio da API.")
    except Exception as e:
        console.print(f"[yellow][AVISO] API indisponível ({e}). Usando dados de exemplo.[/yellow]")
        dados_brutos = carregar_dados_exemplo()

    # 2. Análise (FinOps)
    analyzer = FinOpsAnalyzer(dados_brutos)
    resumo = analyzer.compilar_resumo()
    
    # Prepara datas do período (convertendo YYYY-MM-DD para DD/MM/YYYY)
    start_str = resumo['period_start']
    end_str = resumo['period_end']
    try:
        p_start = f"{start_str[8:10]}/{start_str[5:7]}/{start_str[0:4]}"
        p_end = f"{end_str[8:10]}/{end_str[5:7]}/{end_str[0:4]}"
    except:
        p_start, p_end = start_str, end_str

    # Formatar o texto do painel
    titulo = Text("    AZURE FINOPS ANALYZER v1.0    ", style="bold cyan")
    painel = Panel(titulo, box=box.DOUBLE, expand=False)
    
    # 3. Impressão do Dashboard no Terminal
    console.print()
    console.print(painel)
    console.print()
    console.print(f"📅 Período: {p_start} - {p_end}")
    console.print(f"💰 Custo Total: R$ {formatar_moeda(resumo['total_cost']).strip()}")
    console.print()
    console.print("🔝 Top 5 Serviços:")
    
    for i, srv in enumerate(resumo['top_services'], 1):
        srv_name = srv['Service'].ljust(22)
        srv_cost = formatar_moeda(srv['Cost'])
        # Garantir alinhamento das porcentagens
        srv_pct = f"({srv['Percentage']:.1f}%)".rjust(8)
        console.print(f"  {i}. {srv_name} R$ {srv_cost}  {srv_pct}")
        
    console.print()
    console.print("⚠️  Otimizações sugeridas:")
    for sug in resumo['suggestions']:
        console.print(f"  • {sug}")
        
    console.print()

    # 4. Geração de Relatórios e Exportação
    report_gen = ReportGenerator(data_analise=start_str.replace("-", ""))
    
    # Gera CSV
    caminho_csv = report_gen.exportar_csv(dados_brutos)
    # Gera Excel com gráficos
    caminho_excel = report_gen.gerar_excel(
        resumo=resumo,
        df_servico_rg=analyzer.obter_custo_por_servico_rg(),
        df_diario=analyzer.obter_evolucao_diaria()
    )

    console.print(f"✅ Relatório gerado: {os.path.basename(caminho_excel)}")
    console.print(f"✅ CSV exportado:   {os.path.basename(caminho_csv)}")
    console.print()

if __name__ == "__main__":
    main()
