from psycopg2.extras import execute_values

from typing import Final
from .base import _CURSOR, _CONNECTION
from ..util.response import Response

def _insert_into_table(cursor, records, keys, table_name, primary_key_name=None):
    keys_to_use: Final = [k for k in keys if k in records]
    extracted_rows: Final = {k: records[k] for k in keys_to_use}
    rows = zip(*extracted_rows.values())

    insert_query = f"INSERT INTO {table_name}({", ".join(keys_to_use)}) VALUES %s"
    
    if primary_key_name:
        insert_query += f"RETURNING {primary_key_name}"

    insert_query += ';'
    
    return execute_values(cursor, insert_query, rows, fetch=True)

def import_new_records(records: dict[str, list]) -> Response:
    try:
        Dim_Demographics_IDs = _insert_into_table(
            _CURSOR,
            records,
            [
                'marital_status_id',
                'nationality_id',
                'displaced',
                'gender_id',
                'age_at_enrollment',
            ],
            "Dim_Demographics",
            "Demographics_ID"
        )

        Dim_Socioeconomic_IDs = _insert_into_table(
            _CURSOR,
            records,
            [
                'mother_qualification_id',
                'father_qualification_id',
                'mother_occupation_id',
                'father_occupation_id',
                'debtor',
                'tuition_fees_up_to_date',
                'scholarship_holder',
                'educational_special_needs',
            ],
            "Dim_Socioeconomic",
            "Socioeconomic_ID"
        )

        Dim_Academic_Course_IDs = _insert_into_table(
            _CURSOR,
            records,
            [
                'course_id',
                'application_mode_id',
                'application_order',
                'previous_qualification_id',
                'previous_qualification_grade',
                'admission_grade',
                'daytime_evening_attendance_id',
            ],
            "Dim_Academic_Course",
            "Academic_Course_ID"
        )

        Dim_Macroeconomic_IDs = _insert_into_table(
            _CURSOR,
            records,    
            [
                'unemployment_rate',
                'inflation_rate',
                'gdp',
            ],
            "Dim_Macroeconomic",
            "Macroeconomic_ID"
        )

        foreign_keys = {
            'demographics_id': Dim_Demographics_IDs,
            'socioeconomic_id': Dim_Socioeconomic_IDs,
            'academic_course_id': Dim_Academic_Course_IDs,
            'macroeconomic_id': Dim_Macroeconomic_IDs,
        }

        print(foreign_keys)

        returning = _insert_into_table(
            _CURSOR,
            records | foreign_keys,
            [
                'demographics_id',
                'socioeconomic_id',
                'academic_course_id',
                'macroeconomic_id',
                'cu_1st_sem_credited',
                'cu_1st_sem_enrolled',
                'cu_1st_sem_evaluations',
                'cu_1st_sem_approved',
                'cu_1st_sem_grade',
                'cu_1st_sem_without_evaluations',
                'cu_2nd_sem_credited',
                'cu_2nd_sem_enrolled',
                'cu_2nd_sem_evaluations',
                'cu_2nd_sem_approved',
                'cu_2nd_sem_grade',
                'cu_2nd_sem_without_evaluations',
                'target_outcome_id',
            ],
            "Fact_Academic_Record",
            "*"
        )

        # _CONNECTION.rollback() # FOR TESTING
        _CONNECTION.commit()

    except Exception as e:
        _CONNECTION.rollback()
        print(f"Error {e}")
        return Response(500)

    return Response(200, returning)