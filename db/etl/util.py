from psycopg2.extras import execute_batch

def transform(convert_function, raw_list):
    return list(map(convert_function, raw_list))

def extract(dictReader):
    out = {}

    idx = 0

    for row in dictReader:
        idx += 1
        for key, value in row.items():
            out.setdefault(key, [])
            out[key].append(value)

    out['__count__'] = idx

    return out
