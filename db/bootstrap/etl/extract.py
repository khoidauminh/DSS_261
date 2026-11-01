# Extraction is run on first import

from functools import reduce
from typing import Final
import json, csv, pprint
from . import column_map

COLUMN_MAP = column_map.RAW_MAP

# To prevent typos
MOTHER_QUALIFICATION: Final = "Mother's qualification"
FATHER_QUALIFICATION: Final = "Father's qualification"
MOTHER_OCCUPATION: Final = "Mother's occupation"
FATHER_OCCUPATION: Final = "Father's occupation"
PARENT_QUALIFICATION: Final = "Parent's qualification"
PARENT_OCCUPATION: Final = "Parent's occupation"

# Safe merge
def merge_dicts_strict(d1, d2):
    
    common_keys = d1.keys() & d2.keys()
    for key in common_keys:
        if d1[key] != d2[key]:
            raise ValueError(f"Key {key} has different values:\n\t{d1[key]}\n\t{d2[key]}")
    
    return d1 | d2

COLUMN_MAP[PARENT_QUALIFICATION] = merge_dicts_strict(COLUMN_MAP[MOTHER_QUALIFICATION], COLUMN_MAP[FATHER_QUALIFICATION])
COLUMN_MAP[PARENT_OCCUPATION] = merge_dicts_strict(COLUMN_MAP[MOTHER_OCCUPATION], COLUMN_MAP[FATHER_OCCUPATION])

with open("db/bootstrap/data.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=';')

    def merge(reader):
        out = {}

        idx = 0

        for row in reader:
            idx += 1
            for key, value in row.items():
                out.setdefault(key, [])
                out[key].append(value)

        out['__count__'] = idx

        return out

    EXTRACT_RECORDS: Final = merge(reader)

print("[ETL] Finished extracting the csv into a raw data structure")