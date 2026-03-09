# WFP Supply Chain – Technical Assessment

## Context

Humanitarian operations are becoming increasingly complex to manage. In some countries, WFP manages the warehousing and distribution of medicine on behalf of NGOs operating in the health sector.

In this exercise, WFP manages a **central warehouse** on behalf of an NGO fighting TB, Malaria and HIV in a sub-Saharan country.

## Data

Two sheets in the Excel file:

- **Storage Report**: stock batches extracted from the NGO's inventory management system (quantities, expiration dates, values)
- **Product Details**: reference data for the most important products per program, including estimated monthly consumption

> Note: The `product owner reference` column is used for both the product code and expiration date (system limitation) — they must be parsed from a single field.

## Business Questions

1. What is the **value of stock** at central level for the different disease categories?
2. What are the **stock levels** at the central warehouse for products used to treat **adults with HIV**? Are any of these products expected to **expire soon**?
3. When are the products used for **malaria** expected to **run out of stock**?
4. Do you foresee any **operational issues**? How is the **data quality**?

## Instructions

- Automate the analysis in a sequence of steps using a **Jupyter Notebook**
- Use **inline plotting** where relevant to answer the business questions
- Be prepared to explain each step of the analysis during the interview
