import pandas as pd
import sqlite3

# Load all sheets from the Excel file
all_sheets = pd.read_excel("nachos.xlsx", sheet_name=None)

# Create SQLite database
conn = sqlite3.connect("nachos.db")

# Loop through each sheet and save it as a table
for sheet_name, df in all_sheets.items():

    print(f"Loading sheet: {sheet_name}")
    print(df.head())

    # Save sheet to SQLite table
    df.to_sql(
        sheet_name,
        conn,
        if_exists="replace",
        index=False
    )

print("All sheets saved to SQLite")

# Show all tables created
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn
)

print("\nTables in database:")
print(tables)

conn.close()