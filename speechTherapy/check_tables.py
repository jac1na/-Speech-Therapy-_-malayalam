import sqlite3
con = sqlite3.connect('db.sqlite3')
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print(tables)
