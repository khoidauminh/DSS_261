import psycopg2, json
import csv
import pprint

if input("Script will erase database to re-import data. Proceed? (y/N) ") != "y":
    exit()

from ..etl import load

with open("env.json") as env_file:
    conf = json.load(env_file)
    connection = psycopg2.connect(**conf)

    cursor = connection.cursor()

    with open("db/bootstrap/bootstrap.sql") as bootstrap_script:
        cursor.execute(bootstrap_script.read())

    load.load(cursor)

    cursor.close()

    connection.commit()

    connection.close()

print("Finished creating the database")
