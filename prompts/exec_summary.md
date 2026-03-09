Please generate the executive summary notebook. Here's what I need:

1. Review the business questions in instructions/assessment.md
2. Review the generated data and charts in notebooks/charts/ directory
3. If needed, check notebooks/export_charts_for_summary.py and notebooks/02_final_notebook.ipynb for context
4. Generate notebooks/03_executive_summary.ipynb with:
   - only markdown cells, apart from the charts
   - Clear answers to all 4 business questions from assessment.md
   - Embedded charts example:
        from IPython.display import IFrame
        IFrame(src='charts/q1_stock_value_by_category.html', width=900, height=550)
   - Professional executive summary format
   - IMPORTANT: In markdown tables, escape dollar signs with backslash (\$) not forward slash

The notebook should be presentation-ready for business stakeholders.
