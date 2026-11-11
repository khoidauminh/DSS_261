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
TargetOutCome: Final = ReturningObjectMap['target_outcome_id']

def olap_generic(filters: dict, stats_only: bool) -> Response:
    returning = query_for_records({
        "fields": ReturningObject,
        "filters": filters
    })
    
    if returning.response_code != ResponseCode.OK:
        return returning

    data = returning.data

    count = len(data)
    dropouts = 0
    enrolled = 0

    for record in data:
        if record[TargetOutCome] == 0:
            dropouts += 1

        if record[TargetOutCome] == 2:
            enrolled += 1

    stats = {
        'count': count,
        'dropouts': dropouts,
        'enrolled': enrolled,

        'dropout_rate': dropouts / count
    }

    out: dict = {"stats": stats}

    if not stats_only:
        out.update({
            'records': data,
            'field_order': ReturningObject
        })
        
    return Response(out, ResponseCode.OK, "")
