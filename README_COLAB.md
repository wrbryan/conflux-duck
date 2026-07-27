ConfluxDuck — Colab quickstart

This quick guide shows how to run ConfluxDuck from Google Colab, persist files to Google Drive, run CSV→DuckDB loading, infer relationships, review suggestions interactively (or via a safe fallback), and export results to Google Sheets using user OAuth.

High-level steps
1) Clone the repo and install dependencies
2) Mount Google Drive for persistence (store unified.duckdb and relationships.json there)
3) Load CSVs into a Drive-backed DuckDB
4) Run relationship inference and review suggestions (interactive ipywidgets or DataFrame fallback)
5) Export query results to Google Sheets using user OAuth

Copy-paste cells for a Colab notebook (run one cell at a time)

Cell 1 — Clone & install
```bash
# Clone repository and install runtime deps
!git clone https://github.com/wrbryan/conflux-duck.git
%cd conflux-duck
!pip install -r requirements.txt
```

Cell 2 — Mount Drive & set paths
```python
from google.colab import drive
drive.mount('/content/drive')
WORKDIR = '/content/drive/MyDrive/conflux-duck-work'
import os
os.makedirs(WORKDIR, exist_ok=True)
DB_PATH = f"{WORKDIR}/unified.duckdb"
REL_PATH = f"{WORKDIR}/relationships.json"
print("DB:", DB_PATH)
```

Cell 3 — Load CSVs into the Drive-backed DB
```bash
!python scripts/load_csvs.py --data-dir conflux-duck/data --out-db "$DB_PATH"
```

Cell 4 — Run relationship inference
```bash
!python scripts/infer_relationships.py --db "$DB_PATH" --out "$REL_PATH"
```

Cell 5 — Interactive review (try this first)
```python
# Requires ipywidgets in the Colab runtime (may or may not work depending on Colab environment)
try:
    from scripts.review_relationships import review_relationships
    accepted = review_relationships(REL_PATH, db=DB_PATH)
    print("Accepted (in-memory):", len(accepted))
except Exception as e:
    print("Interactive widgets not available or failed:", e)
    # Fallback instructions follow in the next cell.
```

Cell 6 — Fallback: DataFrame review + manual accept
```python
# Fallback if ipywidgets doesn't behave: show suggestions as DataFrame,
# select indices you want to accept, and write them into the DB.
import json, pandas as pd, duckdb
sugg = json.load(open(REL_PATH))
df = pd.json_normalize(sugg)
df.index.name = 'index'
display(df)  # inspect rows and pick indices

# After inspecting, set accepted_indices to the selected row indices (e.g., [0,2])
accepted_indices = []  # << EDIT this list after reviewing
accepted = df.loc[accepted_indices].to_dict(orient='records')

con = duckdb.connect(DB_PATH)
con.execute("CREATE TABLE IF NOT EXISTS __relationships(from_table VARCHAR, from_col VARCHAR, to_table VARCHAR, to_col VARCHAR, reason VARCHAR, score DOUBLE)")
for r in accepted:
    con.execute("INSERT INTO __relationships VALUES(?, ?, ?, ?, ?, ?)",
                [r.get('from_table') or r.get('table'), r.get('from_col') or r.get('column'),
                 r.get('to_table'), r.get('to_col'), r.get('reason'), r.get('score')])
con.close()
print('Wrote accepted relationships to DB')
```

Cell 7 — Google Sheets export with Colab user OAuth
```python
# Install if needed (Colab sometimes already has these)
!pip install gspread google-auth --quiet

from google.colab import auth
auth.authenticate_user()  # opens an OAuth prompt

import duckdb, gspread
from google.auth import default
creds, _ = default()
gc = gspread.authorize(creds)

con = duckdb.connect(DB_PATH)
# Replace with your query
df = con.execute("SELECT * FROM transactions LIMIT 100").df()

sh = gc.create('ConfluxDuck Transactions (Colab)')
worksheet = sh.get_worksheet(0)
worksheet.update([df.columns.values.tolist()] + df.values.tolist())
print('Sheet URL:', sh.url)
```

Notes & recommendations
- Persist files to Drive; Colab VM storage is ephemeral.
- Do not commit service-account JSON to the repo. For Colab prefer user OAuth as shown.
- Provide the DataFrame fallback (Cell 6) because ipywidgets in Colab can be inconsistent.
- If you want, I can produce a complete notebooks/colab_demo.ipynb file — say the word and I’ll generate it.
