from ..repository import fact_academic_record
from ..validator.student_record import StudentRecordAll, normalize_record_keys
from ..validator import student_record_query 

from ..util.response import Response

# Default values matching PostgreSQL schema defaults when optional keys are omitted in batch insert
DEFAULT_VALUES = {
    "marital_status_id": 1,
    "displaced": False,
    "international": False,
    "mother_qualification_id": 34,
    "father_qualification_id": 34,
    "mother_occupation_id": 99,
    "father_occupation_id": 99,
    "debtor": False,
    "tuition_fees_up_to_date": True,
    "scholarship_holder": False,
    "educational_special_needs": False,
    "previous_qualification_id": 12,
    "unemployment_rate": 0.0,
    "inflation_rate": 0.0,
    "gdp": 0.0,
    "target_outcome_id": 2, # Default Enrolled (2) or Graduate (1)
}

def _transform(convert_function, raw_list):
    return list(map(convert_function, raw_list))

def _transmute(records: list[dict[str, str]]) -> dict[str, list]:
    out = {}

    for raw_record in records:
        record = normalize_record_keys(raw_record)
        for key in StudentRecordAll:
            val = record.get(key, DEFAULT_VALUES.get(key, None))
            out.setdefault(key, []).append(val)

    return out

def query_for_records(query: dict) -> Response:
    if isinstance(res := student_record_query.parse(query), Response):
        return res

    return fact_academic_record.query_for_records(**res)

def import_new_records(list_of_dicts: list[dict[str, str]]) -> Response:
    dict_of_lists = _transmute(list_of_dicts)

    return fact_academic_record.import_new_records(dict_of_lists)