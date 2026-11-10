from psycopg2.extras import execute_values

from ..util.response import Response, ResponseCode
from typing import Final
from ..repository.base import _CURSOR, _CONNECTION
from ..repository.fact_academic_record import get_records_count
from ..service.fact_academic_record import query_for_records

import statistics

ReturningObject: Final = [
    'cu_1st_sem_approved',
    'cu_1st_sem_credited',
    'cu_1st_sem_enrolled',
    'cu_1st_sem_evaluations',
    'cu_1st_sem_grade',
    'cu_1st_sem_without_evaluations',
    'cu_2nd_sem_approved',
    'cu_2nd_sem_credited',
    'cu_2nd_sem_enrolled',
    'cu_2nd_sem_evaluations',
    'cu_2nd_sem_grade',
    'cu_2nd_sem_without_evaluations',
    'previous_qualification_grade',

    'admission_grade',
    'target_outcome_id'
]

ReturningObjectMap: Final = {name: index for index, name in enumerate(ReturningObject)}

def olap_on_course(course_ids: list[int]) -> Response:
    returning = query_for_records({
        "fields": ReturningObject,
        "filters": {
            "course_id": {
                "type": 'values',
                "values": course_ids
            }
        }
    })

    if returning.response_code != ResponseCode.OK:
        return returning

    data = [
        {
            name: record[index] for name, index in ReturningObjectMap.items()
        }
        for record in returning.data
    ]

    count = len(data)
    dropouts = 0
    enrolled = 0
    for record in data:
        if record['target_outcome_id'] == 0:
            dropouts += 1

        if record['target_outcome_id'] == 2:
            enrolled += 1

    stats = {
        'count': count,
        'dropouts': dropouts,
        'enrolled': enrolled,

        'dropout_rate': dropouts / count
    }
        
    return Response({"records": data, "stats": stats}, ResponseCode.OK, "")