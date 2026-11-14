import json
import psycopg2

with open("env.json") as env_file:
    _CONF = json.load(env_file)

_CONNECTION = None
_CURSOR = None

try:
    _CONNECTION = psycopg2.connect(**_CONF)
    _CURSOR = _CONNECTION.cursor()
except Exception as _e:
    print(f"[DB Warning] Could not connect to PostgreSQL on import ({_e}). Will retry when needed.")

def get_db():
    global _CONNECTION, _CURSOR
    if _CONNECTION is None or _CONNECTION.closed:
        _CONNECTION = psycopg2.connect(**_CONF)
        _CURSOR = _CONNECTION.cursor()
    return _CONNECTION, _CURSOR

