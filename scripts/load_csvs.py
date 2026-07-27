#!/usr/bin/env python3
"""
Scan a directory for CSV files and load each into a DuckDB table named by the file (snake_case).
Records a small schema table in the DB: __table_schemas.
"""
import duckdb
import pandas as pd
import argparse
from pathlib import Path
import re


def table_name_from_path(p: Path):
    name = p.stem
    name = re.sub(r'[^0-9a-zA-Z_]', '_', name)
    return name.lower()


def main(data_dir, out_db, overwrite):
    con = duckdb.connect(out_db)
    con.execute("PRAGMA threads=4")
    csvs = list(Path(data_dir).glob("*.csv"))
    schemas = []
    for csv in csvs:
        tbl = table_name_from_path(csv)
        print(f"Loading {csv} -> table {tbl}")
        df = pd.read_csv(csv)
        # Basic normalize: strip column names
        df.columns = [c.strip() for c in df.columns]
        # Write to duckdb (overwrite)
        con.register("tmp_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {tbl} AS SELECT * FROM tmp_df")
        # record schema
        schema = {"table": tbl, "columns": list(df.columns)}
        schemas.append(schema)
    # store schemas
    con.execute("CREATE OR REPLACE TABLE __table_schemas(table_name VARCHAR, columns JSON)")
    for s in schemas:
        con.execute("INSERT INTO __table_schemas VALUES(?, ?)", [s["table"], str(s["columns"])])
    con.close()
    print("Done.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True)
    p.add_argument("--out-db", default="unified.duckdb")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    main(args.data_dir, args.out_db, args.overwrite)
