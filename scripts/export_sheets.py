#!/usr/bin/env python3
"""
Export a duckdb query result to Google Sheets (requires service account credentials).
This is a minimal example using gspread + oauth2client.
Fill SERVICE_ACCOUNT_FILE with a path to the JSON key file.
"""
import duckdb
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import argparse
import pandas as pd

SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']


def df_to_sheet(df, sheet_name, creds_file):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPE)
    gc = gspread.authorize(creds)
    sh = gc.create(sheet_name)
    worksheet = sh.get_worksheet(0)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("Uploaded to Google Sheets:", sh.url)


def main(db, query, sheet_name, creds):
    con = duckdb.connect(db)
    df = con.execute(query).df()
    df_to_sheet(df, sheet_name, creds)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="unified.duckdb")
    p.add_argument("--query", required=True)
    p.add_argument("--sheet", required=True)
    p.add_argument("--creds", required=True, help="Path to service account JSON")
    args = p.parse_args()
    main(args.db, args.query, args.sheet, args.creds)
