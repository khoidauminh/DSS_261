from typing import Final

from ..util.response import Response, ResponseCode

# Set of required keys 
StudentRecordRequired: Final[set[str]] = {
    "marital_status_id",
    "application_mode_id",
    "application_order",
    "course_id",
    "daytime_evening_attendance_id",
    "previous_qualification_grade",
    "nationality_id",
    "admission_grade",
    "gender_id",
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
    "previous_qualification_id", # default 12
    "mother_qualification_id", # default 34
    "father_qualification_id", # default 34
    "mother_occupation_id", # default 99
    "father_occupation_id", # default 99
    "displaced", # default no
    "international", # default no
    "educational_special_needs", # default no
    "debtor", # default no
    "tuition_fees_up_to_date", # default yes
    "scholarship_holder", # default no
    "unemployment_rate", # default 0
    "inflation_rate", # default 0
    "gdp", # default null
    "target_outcome_id", # default enrolled
}

# Alias map for backwards compatibility with older payloads/docs
FieldAliases: Final[dict[str, str]] = {
    "daytime_evening_attendance": "daytime_evening_attendance_id",
    "previous_qualification": "previous_qualification_id",
    "mother_qualification": "mother_qualification_id",
    "father_qualification": "father_qualification_id",
    "mother_occupation": "mother_occupation_id",
    "father_occupation": "father_occupation_id",
    "educational special needs": "educational_special_needs",
}

StudentRecordAll: Final[set[str]] = StudentRecordOptional.union(StudentRecordRequired)

def normalize_record_keys(record: dict) -> dict:
    return {FieldAliases.get(k, k): v for k, v in record.items()}

def validate(record: dict) -> Response | None:
    passed = set()

    for raw_key in record.keys():
        key = FieldAliases.get(raw_key, raw_key)
        if key not in StudentRecordAll:
            return Response({}, ResponseCode.INSERT_INVALID_KEY, f'Invalid key "{raw_key}"')

        if key in passed:
            return Response({}, ResponseCode.INSERT_DUPLICATE, f'Duplicate "{raw_key}"')

        passed.add(key)

    if missing_keys := StudentRecordRequired - passed:
        return Response({}, ResponseCode.INSERT_MISSING_REQUIRED_KEYS, f'Missing the following keys:\n\t{'\n\t'.join(sorted(missing_keys))}')
        
    return None