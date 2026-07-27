# ConfluxDuck

ConfluxDuck combines CSV→DuckDB tooling, relationship inference, notebooks, charts, and Google Sheets export into a single, shareable DuckDB analytics workspace.

Quickstart
1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Load CSVs from `data/` into a unified database:
   ```bash
   python scripts/load_csvs.py --data-dir data --out-db unified.duckdb
   ```

3. (Optional) Merge other DuckDB files:
   ```bash
   python scripts/merge_duckdbs.py --out-db unified.duckdb --attach other_project/lab.duckdb
   ```

4. Infer relationships:
   ```bash
   python scripts/infer_relationships.py --db unified.duckdb --out relationships.json
   ```

5. Open the notebook to explore and chart results:
   ```bash
   jupyter notebook notebooks/demo.ipynb
   ```

6. Export a DataFrame to Google Sheets (see scripts/export_sheets.py for setup).
