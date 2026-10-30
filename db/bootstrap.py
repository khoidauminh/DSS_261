import sqlite3

conn = sqlite3.connect("data.db")

cursor = conn.cursor()

with open("bootstrap.sql") as bootstrap_script:
    cursor.executescript(bootstrap_script.read())

print("Finished")