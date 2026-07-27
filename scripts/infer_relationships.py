#!/usr/bin/env python3
"""
Heuristics to propose relationships:
- name heuristics: column names ending with _id or id
- value overlap: for pairs of columns, check if many values in A appear in B
Outputs JSON of suggested relationships.
"""
import duckdb
import argparse
from collections import defaultdict
import json


def propose_by_name(cols):
    proposals = []
    for table, columns in cols.items():
        for c in columns:
            if c.lower() == "id" or c.lower().endswith("_id"):
                proposals.append((table, c))
    return proposals


def load_table_columns(con):
    # simple information_schema read
    q = """
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema='main'
    ORDER BY table_name
    """
    rows = con.execute(q).fetchall()
    cols = defaultdict(list)
    for table_name, column_name in rows:
        if table_name.startswith("__"):
            continue
        cols[table_name].append(column_name)
    return cols


def value_overlap_score(con, table_a, col_a, table_b, col_b, sample_limit=1000):
    q = f"SELECT {col_a} FROM {table_a} WHERE {col_a} IS NOT NULL LIMIT {sample_limit}"
    a_vals = [r[0] for r in con.execute(q).fetchall()]
    if not a_vals:
        return 0.0
    con.execute("CREATE TEMPORARY TABLE __vals(v VARCHAR)")
    for v in a_vals:
        con.execute("INSERT INTO __vals VALUES (?)", [str(v)])
    cnt_total = con.execute("SELECT COUNT(*) FROM __vals").fetchone()[0]
    cnt_overlap = con.execute(f"SELECT COUNT(DISTINCT v) FROM __vals JOIN {table_b} ON __vals.v = CAST({table_b}.{col_b} AS VARCHAR)").fetchone()[0]
    con.execute("DROP TABLE __vals")
    return float(cnt_overlap) / max(1, cnt_total)


def main(db_path, out_json):
    con = duckdb.connect(db_path)
    cols = load_table_columns(con)
    suggestions = []
    name_hits = propose_by_name(cols)
    for table, col in name_hits:
        suggestions.append({
            "table": table, "column": col, "reason": "name_pattern"
        })
    id_columns = [(t,c) for t,cols_list in cols.items() for c in cols_list if c.lower().endswith("_id") or c.lower()=="id"]
    for (ta, ca) in id_columns:
        for tb, cols_tb in cols.items():
            if ta == tb:
                continue
            for cb in cols_tb:
                score = value_overlap_score(con, ta, ca, tb, cb)
                if score > 0.5:
                    suggestions.append({
                        "from_table": ta, "from_col": ca,
                        "to_table": tb, "to_col": cb,
                        "reason": "value_overlap", "score": score
                    })
    con.close()
    with open(out_json, "w") as f:
        json.dump(suggestions, f, indent=2)
    print(f"Wrote suggestions to {out_json}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="unified.duckdb")
    p.add_argument("--out", default="relationships.json")
    args = p.parse_args()
    main(args.db, args.out)
