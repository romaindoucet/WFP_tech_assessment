"""
Export charts from analysis for executive summary notebook
Run this script to generate static HTML chart files
"""
import os
import numpy as np
import pandas as pd
import plotly.express as px

# Setup paths
EXCEL_DATA_FILE_PATH = "../data/Technical Assignment_Data_full.xlsx"
OUTPUT_DIR = "charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Parameters from original notebook
CONSERVATIVE_EXPIRY_DATE = pd.Timestamp("2026-02-26")
OPTIMISTIC_EXPIRY_DATE = pd.Timestamp("2035-12-31")
DEFAULT_EXPIRY_DATE = OPTIMISTIC_EXPIRY_DATE

# ============================================================================
# DATA LOADING
# ============================================================================

if not os.path.exists(EXCEL_DATA_FILE_PATH):
    raise ValueError(f"File {EXCEL_DATA_FILE_PATH} does not exist")

d_raw_sheets = pd.read_excel(EXCEL_DATA_FILE_PATH, sheet_name=["Storage Report", "Product Details"])

# ============================================================================
# df_product_details
# ============================================================================

df_product_details = (
    d_raw_sheets["Product Details"]
    .rename(columns={
        "Description": "product_description",
        "Category": "product_category",
        "Sub-Category": "product_sub_category",
        "Acronym": "product_acronym",
        "Monthly Consumption (# units)": "monthly_consumption_in_units_per_month",
    })
    .pipe(lambda d: d[d.product_code.notna()])
    .drop_duplicates(subset="product_code", keep="first")
    .assign(
        product_description=lambda d: d.product_description.fillna("Not available"),
        product_category=lambda d: d.product_category.fillna("Not available"),
        product_sub_category=lambda d: d.product_sub_category.fillna("Not available"),
        product_acronym=lambda d: d.product_acronym.fillna("Not available"),
        monthly_consumption_in_units_per_month=lambda d: d.monthly_consumption_in_units_per_month.fillna(0),
    )
    [["product_code", "product_category", "product_sub_category", "product_acronym", "product_description", "monthly_consumption_in_units_per_month"]]
)

# ============================================================================
# df_storage_raw
# ============================================================================

df_storage_raw = (
    d_raw_sheets["Storage Report"]
    .rename(columns={
        "event label": "event_label",
        "date value": "event_date",
        "event line IU quantity": "qty_inventory_unit",
        "inventory unit (IU)": "inventory_unit",
        "event line HU quantity": "qty_handling_unit",
        "handling unit (HU)": "handling_unit",
        "event line weight (mT)": "weight_mt",
        "event line volume (m3)": "volume_m3",
        "event line value (USD)": "value_usd",
        "product category": "product_category_storage",
        "product owner reference": "product_owner_ref_raw",
        "product description": "product_description_storage_raw",
    })
)

# Parse product_code and expiry_date from product_owner_ref_raw
splitted = df_storage_raw["product_owner_ref_raw"].str.split(";", expand=True)
df_storage_raw["product_code"] = splitted[0].str.strip()
df_storage_raw["expiry_date"] = pd.to_datetime(splitted[1].str.strip(), format="%d/%m/%Y", errors="coerce")

# Parse product description
splitted = df_storage_raw["product_description_storage_raw"].str.split(":", expand=True)
df_storage_raw["batch_number"] = splitted[1].str.strip()
supplier_tmp = splitted[0].str.extract(r'\(([^)]+)\)\s*$')[0]
product_description_tmp = splitted[0].str.replace(r'\s*\([^)]+\)\s*$', '', regex=True).str.strip()
supplier_splitted = supplier_tmp.str.split(",", expand=True)
df_storage_raw["supplier"] = supplier_splitted[0].str.strip()
df_storage_raw["supplier_country"] = supplier_splitted[1].str.strip()
product_description_splitted = product_description_tmp.str.split(",", expand=True)
df_storage_raw["product_short_desc_storage"] = product_description_splitted[0].str.strip()
df_storage_raw["product_packaging"] = product_description_splitted[1].str.strip()
df_storage_raw["product_prescription_reco"] = product_description_splitted[2].str.strip()

# ============================================================================
# df_storage
# ============================================================================

df_storage = (
    df_storage_raw
    .assign(product_code=lambda d: d.product_code.fillna("Missing"))
    .assign(
        qty_inventory_unit=lambda d: d.qty_inventory_unit.fillna(0),
        value_usd=lambda d: d.value_usd.fillna(0),
        product_category_storage=lambda d: d.product_category_storage.fillna("Not available"),
        product_description_storage_raw=lambda d: d.product_description_storage_raw.fillna("Not available"),
        product_short_desc_storage=lambda d: d.product_short_desc_storage.fillna("Not available"),
        batch_number=lambda d: d.batch_number.fillna("Not available"),
        expiry_date=lambda d: d.expiry_date.fillna(DEFAULT_EXPIRY_DATE),
    )
    [["product_code", "expiry_date",
      "product_description_storage_raw", "product_short_desc_storage", "product_category_storage", "batch_number",
      "qty_inventory_unit", "inventory_unit", "qty_handling_unit", "handling_unit",
      "weight_mt", "volume_m3", "value_usd",
      "event_date", "event_label",
      ]]
    .astype({
        "qty_inventory_unit": "Int64",
        "qty_handling_unit": "Int64",
        "value_usd": "Int64",
    })
    .sort_values("expiry_date", ascending=True)
)

# ============================================================================
# Claude categorizations (pre-generated)
# ============================================================================

df_claude_cat = pd.read_csv("claude_missing_cat.csv")

# ============================================================================
# df_stock
# ============================================================================

df_stock = (
    df_storage
    .pipe(lambda d: d[d.event_label == "Closing Stock on Hand - Good Condition"])
    .groupby(["product_code", "expiry_date", "product_short_desc_storage", "event_date"], as_index=False)
    .agg(
        product_short_desc_storage=("product_short_desc_storage", lambda x: x.mode().iloc[0]),
        qty_inventory_unit=("qty_inventory_unit", sum),
        value_usd=("value_usd", sum),
    )
    .merge(
        df_product_details[["product_code", "product_category", "product_sub_category"]],
        on="product_code", how="left"
    )
    .merge(
        df_claude_cat
        .pipe(lambda d: d[d.category.isin(["HIV", "TB", "Malaria"])])
        .rename(columns={"short_desc": "product_short_desc_storage", "category": "product_category_fallback"}),
        on="product_short_desc_storage", how="left"
    )
    .assign(product_category=lambda d: d.product_category.fillna(d.product_category_fallback))
    .drop(columns=["product_category_fallback"])
    .assign(
        product_category=lambda d: d.product_category.fillna("Not available"),
        product_sub_category=lambda d: d.product_sub_category.fillna("Not available"),
        adult_category=lambda d: d.adult_category.fillna("Not available"),
    )
)

print("Data loaded successfully!")
print(f"Total stock value: ${df_stock.value_usd.sum():,}")

# ============================================================================
# CHART 1 (Q1): Stock Value by Category
# ============================================================================

df_stock_value_by_cat = (
    df_stock
    .groupby(["product_category"], as_index=False)
    .value_usd.sum()
)

fig1 = px.bar(
    df_stock_value_by_cat,
    x="product_category",
    y="value_usd",
    title="Stock Value by Product Category",
    color="product_category",
    text="value_usd",
    labels={"value_usd": "Stock Value (USD)", "product_category": "Disease Category"}
)
fig1.update_traces(texttemplate='$%{text:,}', textposition='outside')
fig1.update_layout(showlegend=False, height=500)
fig1.write_html(f"{OUTPUT_DIR}/q1_stock_value_by_category.html")
print("✓ Chart 1: Stock value by category")

# ============================================================================
# CHART 2a (Q2): Adults with HIV - Stock Levels
# ============================================================================

df_stock_adults_HIV = (
    df_stock
    [["product_code", "expiry_date", "event_date", "product_short_desc_storage", "product_category", "product_sub_category", "adult_category", "qty_inventory_unit", "value_usd"]]
    .pipe(lambda d: d[d.product_category == "HIV"])
    .pipe(lambda d: d[(d.product_sub_category.str.contains("Adults")) | (d.adult_category.isin(["Adult", "Both"]))])
)

df_stock_levels_adults_HIV = (
    df_stock_adults_HIV
    .groupby(["product_short_desc_storage", "product_code"], as_index=False)
    .qty_inventory_unit.sum()
)

fig2 = px.treemap(
    df_stock_levels_adults_HIV,
    path=["product_short_desc_storage", "product_code"],
    values="qty_inventory_unit",
    title="HIV Adult Products: Current Stock Levels",
)
fig2.update_layout(height=500)
fig2.write_html(f"{OUTPUT_DIR}/q2_hiv_adults_stock_levels.html")
print("✓ Chart 2a: HIV adult stock levels")

# ============================================================================
# CHART 2b (Q2): Adults with HIV - Expiry Distribution
# ============================================================================

bins = [-float("inf"), 0, 30, 60, 90, 180, 365, 730, 10000]
labels = ["expired", "0-30", "30-60", "60-90", "90-180", "180-365", "365-730", "730+"]

df_stock_levels_adults_HIV_expiring_soon = (
    df_stock_adults_HIV
    .assign(days_to_expiry=lambda d: (d.expiry_date - d.event_date).dt.days)
    .assign(expiry_bucket_days=lambda d: pd.cut(d.days_to_expiry, bins=bins, labels=labels, right=True))
    .groupby(["product_short_desc_storage", "product_code", "expiry_bucket_days", "expiry_date"], as_index=False)
    .qty_inventory_unit.sum()
)

fig3 = px.bar(
    df_stock_levels_adults_HIV_expiring_soon,
    y='expiry_bucket_days',
    x='qty_inventory_unit',
    color='product_short_desc_storage',
    orientation='h',
    title="HIV Adult Products: Stock Distribution by Days to Expiry",
    labels={
        'qty_inventory_unit': 'Stock Quantity (units)',
        'expiry_bucket_days': 'Days to Expiry',
        'product_short_desc_storage': 'Product',
        'product_code': 'Product Code'
    },
    hover_data={'expiry_date': '|%Y-%m-%d', 'product_code': True},
    category_orders={'expiry_bucket_days': ['expired', '0-30', '30-60', '60-90', '90-180', '180-365', '365-730', '730+']},
    text='qty_inventory_unit'
)
fig3.update_traces(texttemplate='%{x:,}', textposition='inside')
fig3.update_layout(
    height=500,
    barmode='stack',
    legend=dict(title="Product", orientation="v", yanchor="top", y=1, xanchor="left", x=1.01)
)
fig3.write_html(f"{OUTPUT_DIR}/q2_hiv_adults_expiry.html")
print("✓ Chart 2b: HIV adult expiry distribution")

# ============================================================================
# Q3 & Q4: Stock evolution and out-of-stock dates
# ============================================================================

date_min, date_max = df_stock.event_date.min(), df_stock.expiry_date.max()
df_dates = pd.DataFrame({'date': pd.date_range(start=date_min, end=date_max, freq='D')})

df_stock_non_expired_by_date = (
    df_stock
    .assign(KEY=1)
    .merge(df_dates.assign(KEY=1), on="KEY", how="inner")
    .assign(is_expired=lambda d: np.where(d.date >= d.expiry_date, 1, 0))
    .assign(
        non_expired_qty=lambda d: d.qty_inventory_unit * (1 - d.is_expired),
        non_expired_value_usd=lambda d: d.value_usd * (1 - d.is_expired),
    )
    .groupby(["product_code", "product_short_desc_storage", "product_category", "product_sub_category", "adult_category", "date", "event_date"], as_index=False)
    [["non_expired_qty", "non_expired_value_usd"]].sum()
    .assign(nb_days_since_origin=lambda d: (d.date - d.event_date).dt.days)
    .merge(
        df_product_details
        .assign(daily_consumption=lambda d: d.monthly_consumption_in_units_per_month * 12 / 365)
        [["product_code", "daily_consumption"]],
        on=["product_code"], how="left"
    )
    .assign(daily_consumption=lambda d: d.daily_consumption.fillna(0))
    .assign(cumul_consumption=lambda d: d.daily_consumption * d.nb_days_since_origin)
    .assign(remaining_stock_qty=lambda d: d.non_expired_qty - d.cumul_consumption)
)

df_out_of_stock_date_by_product = (
    df_stock_non_expired_by_date
    .pipe(lambda d: d[d.remaining_stock_qty < 0])
    .groupby(["product_code", "product_short_desc_storage", "product_category"], as_index=False)
    ["date"].min()
    .rename(columns={"date": "out_of_stock_date"})
    .sort_values(["out_of_stock_date"])
)

df_out_of_stock_date_malaria = (
    df_out_of_stock_date_by_product
    .pipe(lambda d: d[d.product_category == "Malaria"])
    .assign(days_until_stockout=lambda d: (d.out_of_stock_date - df_stock.event_date.min()).dt.days)
)

# ============================================================================
# CSV exports
# ============================================================================

df_stock_value_by_cat.to_csv(f"{OUTPUT_DIR}/q1_data.csv", index=False)
df_out_of_stock_date_malaria.to_csv(f"{OUTPUT_DIR}/q3_data.csv", index=False)
df_out_of_stock_date_by_product.to_csv(f"{OUTPUT_DIR}/q4_out_of_stock_dates.csv", index=False)

print(f"\n✓ All outputs exported to '{OUTPUT_DIR}/' directory")
print(f"  Charts:")
print(f"    - q1_stock_value_by_category.html")
print(f"    - q2_hiv_adults_stock_levels.html")
print(f"    - q2_hiv_adults_expiry.html")
print(f"  Data:")
print(f"    - q1_data.csv")
print(f"    - q3_data.csv")
print(f"    - q4_out_of_stock_dates.csv")
