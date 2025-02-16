# Purpose

Automate search and selection of parts for a PC build in Switzerland.

This repo provides scripts to scrape PC parts from Toppreise and automate the selection of parts based on user-provided filtering criteria and objectives.

# Usage

Scrape products from Toppreise:
```
make scrape
```
Data will be collected in a dedicated CSV file for every product under `data/complete`.

Filter items with incomplete descriptions, not meeting specified criteria and which are not Pareto-optimal:
```
make filter
```
This invokes a dedicated Python script for each product, defining the specific filtering (and sorting) logic (e.g. `cpu.py` for CPUs).
The idea is that most of the decision-making criteria is recorded here for future reference or reproducibility.
The filtered data is collected in a dedicated CSV file for every product under `data/filtered`.

Collect the separate, filtered CSV files in a unified spreadsheet (`bom.xlsx`) for the final part selection, and composition of a bill of materials (BOM):
```
make bom
```
This target depends on the filtered data, so running `make filter` explicitly to build or update these files is not required.

Open `bom.xlsx` with a spreadsheet editor, e.g. on Ubuntu 22.04:
```
libreoffice bom.xlsx &
```
You can create a new sheet for the BOM, linking to the selected products in the auto-generated product sheets.

The product sheets can be safely updated at any time using the previous Make targets, without deleting or overwriting the manually created sheets. However, note that links to cells in the product sheets may break as a consequence of updating the product sheets.
