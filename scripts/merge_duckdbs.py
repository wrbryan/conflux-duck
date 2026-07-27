#!/usr/bin/env python3
"""
Attach one or more DuckDB files and copy their tables into the target DB.
This is conservative: it ignores name collisions unless --overwrite is set.
"""
import duckdb
import argparse
from pathlib import Path


def copy_attached_tables(con, alias, overwrite=False):
    # list tables from attached DB
    rows = con.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{alias}'").fetchall()
    for (t,) in rows:
        tgt = t
        if overwrite:
            con.execute(f"DROP TABLE IF EXISTS {tgt}")
        print(f"Copying {alias}.{t} -> {tgt}")
        con.execute(f"CREATE OR REPLACE TABLE {tgt} AS SELECT * FROM {alias}.{t}")


def main(out_db, attaches, overwrite):
    con = duckdb.connect(out_db)
    for i, path in enumerate(attaches):
        alias = f"src{i}"
        print(f"ATTACH {path} AS {alias}")
        con.execute(f"ATTACH DATABASE '{path}' AS {alias}")
        copy_attached_tables(con, alias, overwrite=overwrite)
        con.execute(f"DETACH DATABASE {alias}")
    con.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--out-db", default="unified.duckdb")
    p.add_argument("--attach", action="append", dest="attaches", required=True,
                   help="Path to an existing duckdb file to merge; can be provided multiple times.")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    main(args.out_db, args.attaches, args.overwrite)
