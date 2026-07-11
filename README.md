<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0b21,100:0a0818&height=200&section=header&text=Azure%20FinOps%20Analyzer&fontSize=48&fontColor=fdf6e3&fontAlignY=38&desc=Cloud%20Cost%20Intelligence%20%E2%80%A2%20Python%20%E2%80%A2%20Azure&descSize=18&descAlignY=62&descColor=b09fd8"/>

![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Azure](https://img.shields.io/badge/azure-cost--management-0089D6?logo=microsoft-azure)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## About

Azure FinOps Analyzer is a Python CLI tool that connects directly to the **Azure Cost Management API** to fetch, analyze, and report cloud infrastructure costs in real time. It automatically identifies spending anomalies, generates executive summaries, and provides actionable optimization recommendations — following **FinOps** best practices for cloud cost governance.

Developed as a portfolio project demonstrating practical skills in cloud computing, Python automation, and infrastructure cost analysis.

> ✅ **Tested with a real Azure subscription** — fetches live cost data via Azure Cost Management API.  
> 🔁 Falls back to realistic mock data when credentials are unavailable.

---

## Features

- [x] **Secure Azure Integration** — uses `DefaultAzureCredential` for seamless authentication
- [x] **Live Cost Aggregation** — groups costs by Service and Resource Group over customizable periods
- [x] **FinOps Analysis Engine** — highlights top spending services and calculates daily growth trends
- [x] **Smart Recommendations** — suggests actionable optimizations (idle VMs, storage lifecycle, capacity reservations)
- [x] **Executive Excel Reports** — auto-generates styled `.xlsx` files with native Bar Charts across 3 worksheets
- [x] **Raw CSV Exports** — dumps aggregated data for BI tool ingestion (Power BI, Grafana, etc.)
- [x] **Graceful Fallback** — detects missing credentials and switches to realistic mock data automatically
- [x] **Rich CLI Dashboard** — visually formatted terminal output using the `rich` library

---

## Architecture

```
main.py           →  Orchestrator: execution flow, env config, CLI rendering
azure_client.py   →  Azure SDK integration, Cost Management API queries → DataFrames
analyzer.py       →  FinOps engine: KPIs, growth metrics, recommendations
report.py         →  File I/O: Excel (multi-sheet + charts) and CSV generation
sample_data.py    →  Realistic mock data for demo/fallback mode
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Cloud | Microsoft Azure |
| Auth | `azure-identity` (DefaultAzureCredential) |
| API | `azure-mgmt-costmanagement` |
| Data | `pandas` |
| Reports | `openpyxl` |
| CLI UI | `rich` |
| Config | `python-dotenv` |
| Infra | Docker |

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Ricardo0800/azure-finops-analyzer.git
cd azure-finops-analyzer
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in your Azure credentials — or leave empty for sample data mode
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run
```bash
python main.py
```

---

## Real Data vs Sample Data

| Mode | How to activate | What happens |
|------|----------------|-------------|
| **Real** | Fill `.env` with Azure credentials | Queries your live Azure subscription |
| **Sample** | Leave `.env` empty or omit it | Runs with realistic mock data automatically |

---

## Sample Output

```
╔════════════════════════════════════╗
║     AZURE FINOPS ANALYZER v1.0     ║
╚════════════════════════════════════╝

📅 Period: 10/06/2026 - 10/07/2026
💰 Total Cost: R$ 55,15

🔝 Top Services:
  1. Storage           R$  34,98   (63.4%)
  2. Virtual Network   R$  18,89   (34.3%)
  3. Virtual Machines  R$   1,29    (2.3%)
  4. Bandwidth         R$   0,00    (0.0%)

⚠️  Optimization suggestions:
  • Storage is currently your largest cost driver. Review retention policies and unused blobs.

✅ Report generated: relatorio_20260610.xlsx
✅ CSV exported:     custos_20260610.csv
```

> The output above shows **real data** fetched from an Azure for Students subscription.

---

## Azure Setup (for real data mode)

```bash
# 1. Login
az login

# 2. Create service principal with Cost Management Reader role
az ad sp create-for-rbac \
  --name "finops-analyzer" \
  --role "Cost Management Reader" \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>

# 3. Copy the output values to your .env file
```

---

## Author

**Ricardo Felix** — [github.com/Ricardo0800](https://github.com/Ricardo0800) · [linkedin.com/in/ricardo-fgs-nonato](https://linkedin.com/in/ricardo-fgs-nonato)

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0818,100:0f0b21&height=120&section=footer"/>
