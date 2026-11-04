from ..dto import student_record
from ..service import fact_academic_record
from ..util.response import Response

from flask import request

def import_new_records(list_of_dicts: list[dict]):
    if not list_of_dicts:
        return Response(400, "No record in request body").into_response()

    for i, record in enumerate(list_of_dicts):
        if e := student_record.validate(record):
            e.data = f"Record {i+1}: " + e.data
            return e.into_response()

    return fact_academic_record.import_new_records(list_of_dicts).into_response()


print("Loaded routes")