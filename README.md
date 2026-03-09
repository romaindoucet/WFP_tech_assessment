# WFP Supply Chain Technical Assessment

Technical assessment for the **Supply Chain Data Scientist position at WFP** (World Food Programme) — Job ID JR119606.

## Business Context

WFP manages a central warehouse for an NGO fighting TB, Malaria, and HIV in a sub-Saharan country. This assessment analyses medicine stock data to answer four business questions:

1. **Stock value by disease category** — What is the total value of stock at central level?
2. **HIV adult products** — What are the current stock levels and expiry dates for adult HIV treatment products?
3. **Malaria supply timeline** — When will malaria products run out of stock?
4. **Operational issues & data quality** — Are there forecast problems or data quality concerns?

Data source: two Excel sheets — a Storage Report (stock batches with expiry dates) and a Product Details reference table. A known system limitation is that product codes and expiry dates are encoded together in a single field and must be parsed.

## Repository Structure

```
data/                    # Excel datasets (dev, full, tricks variants)
instructions/            # Assessment brief and business questions
notebooks/
  02_final_notebook.ipynb    # Main analysis — run this
  03_executive_summary.ipynb # Generated executive summary (output artifact)
  charts/                    # Exported HTML charts and CSV data (generated)
  export_charts_for_summary.py
prompts/
  exec_summary.md        # Claude prompt used to generate the executive summary
justfile                 # Task automation
pyproject.toml           # Python dependencies
```

## Prerequisites

### uv (Python package manager)

**macOS:**
```bash
brew install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
winget install --id=astral-sh.uv -e
# or
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### just (task runner)

**macOS:**
```bash
brew install just
```

**Windows:**
```powershell
winget install --id Casey.Just -e
# or via cargo: cargo install just
```

### Claude Code (required for executive summary only)

Install and authenticate Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
claude login
```

Claude Code is only needed to run `just exec_summary`. The main analysis notebook (`02_final_notebook.ipynb`) runs without it.

## Installation

```bash
just install
```

This creates a `.venv` and installs all Python dependencies (pandas, plotly, jupyterlab, etc.) via `uv sync`.

## Running the Analysis

### 1. Launch JupyterLab

```bash
just lab
```

Open `notebooks/02_final_notebook.ipynb` and run all cells. The notebook:
- Loads data from `data/Technical Assignment_Data_full.xlsx`
- Cleans and parses the stock data (including Claude-assisted categorisation of ambiguous products)
- Produces inline Plotly charts answering each business question

> **Note:** The notebook has a `INVOKE_CLAUDE_FOR_MISSING_DATA` flag. When `True`, it calls Claude Code to categorise products that cannot be matched automatically. This requires Claude Code to be installed and authenticated.

### 2. Generate the Executive Summary (optional)

```bash
just exec_summary
```

This runs two steps:
1. `just export_charts` — exports charts and summary CSVs to `notebooks/charts/`
2. Pipes `prompts/exec_summary.md` to `claude`, which generates `notebooks/03_executive_summary.ipynb`

The output notebook is a presentation-ready summary for business stakeholders.

## Available Commands

```
just install        # Set up Python environment
just lab            # Launch JupyterLab
just export_charts  # Export charts and data from the analysis notebook
just exec_summary   # Generate executive summary (requires Claude Code)
```
