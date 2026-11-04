from typing import Final

from ..util.response import Response

# Set of required keys 
StudentRecordRequired: Final[set[str]] = {
    "marital_status_id",
    "application_mode_id",
    "application_order",
    "course_id",
    "daytime_evening_attendance",
    "previous_qualification_grade",
    "nationality_id",
    "admission_grade",
    "gender",
    "age_at_enrollment",
    "cu_1st_sem_credited",
    "cu_1st_sem_enrolled",
    "cu_1st_sem_evaluations",
    "cu_1st_sem_approved",
    "cu_1st_sem_grade",
    "cu_1st_sem_without_evaluations",
    "cu_2nd_sem_credited",
    "cu_2nd_sem_enrolled",
    "cu_2nd_sem_evaluations",
    "cu_2nd_sem_approved",
    "cu_2nd_sem_grade",
    "cu_2nd_sem_without_evaluations",
}

StudentRecordOptional: Final[set[str]] = {
    "previous_qualification", # default 12
    "mother_qualification", # default 34
    "father_qualification", # default 34
    "mother_occupation", # default 99
    "father_occupation", # default 99
    "displaced", # default no
    "educational special needs", # default no
    "debtor", # default no
    "tuition_fees_up_to_date", # default yes
    "scholarship_holder", # default no
    "unemployment_rate", # default 0
    "inflation_rate", # default 0
    "gdp", # default null
    "target", # default enrolled
}

StudentRecordAll: Final[set[str]] = StudentRecordOptional.union(StudentRecordRequired)

def validate(record: dict) -> Response | None:
    input_keys: Final = record.keys()

    for key in input_keys:
        if key not in StudentRecordAll:
            return Response(400, f'Invalid key "{key}"') 

    if missing_keys := StudentRecordRequired - input_keys:
        return Response(400, f'Missing the following keys:\n\t{'\n\t'.join(sorted(missing_keys))}')
        
    return None