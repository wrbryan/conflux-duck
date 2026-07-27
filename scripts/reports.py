import duckdb
con = duckdb.connect("unified.duckdb")
# assumes a transactions table exists
if con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='transactions'").fetchone()[0] > 0:
    by_category = con.sql("""
        SELECT
            category,
            SUM(amount) AS net_amount,
            -SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS total_spent,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income
        FROM transactions
        GROUP BY category
        ORDER BY total_spent DESC;
    """).df()
    print(by_category)
else:
    print("No transactions table found in unified.duckdb")
