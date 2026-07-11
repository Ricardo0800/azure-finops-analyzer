# Azure FinOps Analyzer

![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Azure](https://img.shields.io/badge/azure-cost--management-0089D6?logo=microsoft-azure)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## About
Azure FinOps Analyzer is a Python-based CLI tool designed to fetch, analyze, and report cloud infrastructure costs directly from the Azure Cost Management API. Developed as a demonstration of Cloud FinOps practices and Software Engineering principles, it automatically identifies cost anomalies, generates executive summaries, and provides dynamic optimization recommendations.

## Features
- [x] **Secure Azure Integration**: Uses `DefaultAzureCredential` for seamless and secure authentication.
- [x] **Cost Aggregation**: Fetches and groups costs by Service and Resource Group over customizable periods.
- [x] **Dynamic FinOps Analysis**: Automatically highlights top spending services and calculates daily growth.
- [x] **Smart Recommendations**: Suggests actionable optimizations (e.g., stopping idle VMs, lifecycle management for storage).
- [x] **Executive Excel Reports**: Auto-generates heavily stylized `.xlsx` files complete with native Bar Charts.
- [x] **Raw CSV Exports**: Dumps aggregated data into `.csv` files for BI tool ingestion.
- [x] **Graceful Fallback Mechanism**: Detects missing credentials or API failures and seamlessly switches to realistic mock data for demonstration purposes.
- [x] **Beautiful CLI Dashboard**: Presents a visually appealing terminal summary using the `rich` library.

## Architecture
The project is built with modularity and separation of concerns in mind:
1. **`main.py`**: The central orchestrator that handles the execution flow, environment variables, and the CLI UI rendering.
2. **`azure_client.py`**: Handles API connections using the Azure Python SDK, mapping raw API responses into structured DataFrames.
3. **`sample_data.py`**: Provides highly realistic deterministic mock data for testing and demonstrations when real Azure credentials are not available.
4. **`analyzer.py`**: The core FinOps engine. Processes the raw cost DataFrames to extract KPIs, growth metrics, and generate dynamic text-based recommendations.
5. **`report.py`**: Responsible for the file I/O layer. Generates CSVs and formatted multi-sheet Excel files utilizing `openpyxl`.

## Tech Stack
- **Language**: Python 3.11+
- **Cloud Provider**: Microsoft Azure
- **Libraries**: `azure-identity`, `azure-mgmt-costmanagement`, `pandas`, `openpyxl`, `rich`, `python-dotenv`
- **Infrastructure**: Docker

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/azure-finops-analyzer.git
cd azure-finops-analyzer
```

### 2. Configure Environment
Copy the example environment file and fill in your Azure details.
```bash
cp .env.example .env
```
*(Leave it empty to automatically run the Fallback mode with Sample Data).*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Analyzer
```bash
python main.py
```

## How to Use: Real Data vs Sample Data
- **Real Data**: Ensure your `.env` contains valid `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_SUBSCRIPTION_ID`. The application will authenticate and query your actual Azure tenant.
- **Sample Data**: If no `.env` is configured or if the Azure API is unreachable, the tool automatically catches the exception and falls back to generating realistic mock data (featuring standard Azure services like Virtual Machines and App Services).

## Sample Output

```
╔══════════════════════════════════════╗
║     AZURE FINOPS ANALYZER v1.0       ║
╚══════════════════════════════════════╝

📅 Período: 01/06/2026 - 30/06/2026
💰 Custo Total: R$ 847,32

🔝 Top 5 Serviços:
  1. Virtual Machines      R$ 412,10  (48.6%)
  2. Azure SQL Database    R$ 198,44  (23.4%)
  3. Storage               R$ 121,33  (14.3%)
  4. App Service           R$  89,22  (10.5%)
  5. Azure Monitor         R$  26,23   (3.1%)

⚠️  Otimizações sugeridas:
  • Virtual Machines representam 48.6% do custo. Verifique VMs paradas (Right-sizing/Desligamento).
  • Azure SQL Database representa 23.4% do custo. Considere analisar Reservas de Capacidade para economizar.
  • Storage com crescimento de 12% nos últimos 7 dias. Considere revisar políticas de retenção e blobs não utilizados.

✅ Relatório gerado: relatorio_20260630.xlsx
✅ CSV exportado:   custos_20260630.csv
```
