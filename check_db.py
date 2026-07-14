import sqlite3

conn = sqlite3.connect("triageflow.db")
cursor = conn.cursor()

print("=== TABLES THAT EXIST ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
if tables:
    for t in tables:
        print(t[0])
else:
    print("NO TABLES FOUND")

print()
print("=== ALL TICKETS ===")
try:
    cursor.execute("SELECT ticket_id, status, created_at FROM tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"ID: {row[0][:8]}...  STATUS: {row[1]}  DATE: {row[2]}")
    else:
        print("NO TICKETS IN DATABASE")
except Exception as e:
    print(f"ERROR reading tickets table: {e}")

conn.close()
