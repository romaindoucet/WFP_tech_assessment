# WFP Supply Chain Assessment - Just recipes

# Install dependencies
install:
    uv sync --all-extras --all-groups

# Start JupyterLab
lab:
    uv run jupyter lab

# Export charts and data from analysis notebook
export_charts:
    @echo "→ Exporting charts and data..."
    cd notebooks && uv run export_charts_for_summary.py

# Generate executive summary notebook
exec_summary: export_charts
    @echo "→ Generating executive summary with Claude..."
    cat prompts/exec_summary.md | claude
