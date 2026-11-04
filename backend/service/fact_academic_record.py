from ..repository import fact_academic_record
from ..dto.student_record import StudentRecordAll
from ..util.response import Response

def _transform(convert_function, raw_list):
    return list(map(convert_function, raw_list))

def _transmute(records: list[dict[str, str]]) -> dict[str, list]:
    out = {}

    for record in records:
        for key in StudentRecordAll:
            out.setdefault(key, []).append(record.get(key, None))

    return out

def import_new_records(list_of_dicts: list[dict[str, str]]) -> Response:
    dict_of_lists = _transmute(list_of_dicts)

    return fact_academic_record.import_new_records(dict_of_lists)