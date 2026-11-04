import json
import psycopg2

with open("env.json") as env_file:
    conf = json.load(env_file)
    _CONNECTION = psycopg2.connect(**conf)
    _CURSOR = _CONNECTION.cursor()

