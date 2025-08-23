import sqlite3
conn = sqlite3.connect('./certalert.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(subscriptions);")
for row in cursor.fetchall():
    print(row)
conn.close()