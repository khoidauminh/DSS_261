from ..validator import student_record
from ..service import fact_academic_record
from ..util.response import Response, ResponseCode

from flask import request

def import_new_records(list_of_dicts: list[dict]) -> Response:
    if not list_of_dicts:
        return Response({}, ResponseCode.INSERT_INVALID_GENERIC, "No record in request body")

    for i, record in enumerate(list_of_dicts):
        if e := student_record.validate(record):
            e.response_message = f"Record {i+1}: " + e.response_message
            return e

    return fact_academic_record.import_new_records(list_of_dicts)

def query_for_records(query: dict[str, str]) -> Response:
    return fact_academic_record.query_for_records(query)