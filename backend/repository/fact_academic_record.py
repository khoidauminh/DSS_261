import psycopg2
from psycopg2.extras import execute_values

from typing import Final
from .base import get_db
from ..util.response import Response, ResponseCode

def _insert_into_table(cursor, records, keys, table_name, primary_key_name=None, unique_cols=None):
    keys_to_use: Final = [k for k in keys if k in records]
    extracted_rows: Final = {k: records[k] for k in keys_to_use}
    rows = list(zip(*extracted_rows.values()))

    if unique_cols and primary_key_name:
        conflict_cols = ", ".join(unique_cols)
        first_col = unique_cols[0]
        results = []
        upsert_query = (
            f"INSERT INTO {table_name}({', '.join(keys_to_use)}) "
            f"VALUES ({', '.join(['%s'] * len(keys_to_use))}) "
            f"ON CONFLICT ({conflict_cols}) DO UPDATE SET {first_col} = EXCLUDED.{first_col} "
            f"RETURNING {primary_key_name};"
        )
        for row in rows:
            cursor.execute(upsert_query, row)
            results.append(cursor.fetchone())
        return results

    insert_query = f"INSERT INTO {table_name}({', '.join(keys_to_use)}) VALUES %s"
    
    if primary_key_name:
        insert_query += f" RETURNING {primary_key_name}"

    insert_query += ';'
    
    return execute_values(cursor, insert_query, rows, fetch=True)

def ping() -> Response:
    try:
        _, cursor = get_db()
        cursor.execute("SELECT 1;")
    except Exception as e:
        return Response({}, ResponseCode.INTERNAL_ERROR, f'{e}')

    return Response({}, ResponseCode.OK, "")

def _fallback_in_memory_query(fields: list[str], filters: list[tuple[str, list]], page_num: int | None = None, page_size: int | None = None) -> list[tuple]:
    from db.etl import transform as etl_t
    n = len(etl_t.Fact_Academic_Record["Target_Outcome_ID"])
    rows = []
    for i in range(n):
        d_id = etl_t.Fact_Academic_Record["Demographics_ID"][i] - 1
        s_id = etl_t.Fact_Academic_Record["Socioeconomic_ID"][i] - 1
        c_id = etl_t.Fact_Academic_Record["Academic_Course_ID"][i] - 1
        m_id = etl_t.Fact_Academic_Record["Macroeconomic_ID"][i] - 1
        t_id = etl_t.Fact_Academic_Record["Target_Outcome_ID"][i]
        rec = {
            "student_id": i + 1,
            "marital_status_id": etl_t.Dim_Demographics["Marital_status_ID"][d_id],
            "nationality_id": etl_t.Dim_Demographics["Nationality_ID"][d_id],
            "displaced": etl_t.Dim_Demographics["Displaced"][d_id],
            "gender_id": etl_t.Dim_Demographics["Gender_ID"][d_id],
            "international": etl_t.Dim_Demographics["International"][d_id],
            "age_at_enrollment": etl_t.Dim_Demographics["Age_at_enrollment"][d_id],
            "mother_qualification_id": etl_t.Dim_Socioeconomic["Mother_qualification_ID"][s_id],
            "father_qualification_id": etl_t.Dim_Socioeconomic["Father_qualification_ID"][s_id],
            "mother_occupation_id": etl_t.Dim_Socioeconomic["Mother_occupation_ID"][s_id],
            "father_occupation_id": etl_t.Dim_Socioeconomic["Father_occupation_ID"][s_id],
            "debtor": etl_t.Dim_Socioeconomic["Debtor"][s_id],
            "tuition_fees_up_to_date": etl_t.Dim_Socioeconomic["Tuition_fees_up_to_date"][s_id],
            "scholarship_holder": etl_t.Dim_Socioeconomic["Scholarship_holder"][s_id],
            "educational_special_needs": etl_t.Dim_Socioeconomic["Educational_special_needs"][s_id],
            "course_id": etl_t.Dim_Academic_Course["Course_ID"][c_id],
            "application_mode_id": etl_t.Dim_Academic_Course["Application_mode_ID"][c_id],
            "application_order": etl_t.Dim_Academic_Course["Application_order"][c_id],
            "previous_qualification_id": etl_t.Dim_Academic_Course["Previous_qualification_ID"][c_id],
            "previous_qualification_grade": etl_t.Dim_Academic_Course["Previous_qualification_grade"][c_id],
            "admission_grade": etl_t.Dim_Academic_Course["Admission_grade"][c_id],
            "daytime_evening_attendance_id": etl_t.Dim_Academic_Course["Daytime_evening_attendance_ID"][c_id],
            "unemployment_rate": etl_t.Dim_Macroeconomic["Unemployment_rate"][m_id],
            "inflation_rate": etl_t.Dim_Macroeconomic["Inflation_rate"][m_id],
            "gdp": etl_t.Dim_Macroeconomic["GDP"][m_id],
            "cu_1st_sem_credited": etl_t.Fact_Academic_Record["CU_1st_sem_credited"][i],
            "cu_1st_sem_enrolled": etl_t.Fact_Academic_Record["CU_1st_sem_enrolled"][i],
            "cu_1st_sem_evaluations": etl_t.Fact_Academic_Record["CU_1st_sem_evaluations"][i],
            "cu_1st_sem_approved": etl_t.Fact_Academic_Record["CU_1st_sem_approved"][i],
            "cu_1st_sem_grade": etl_t.Fact_Academic_Record["CU_1st_sem_grade"][i],
            "cu_1st_sem_without_evaluations": etl_t.Fact_Academic_Record["CU_1st_sem_without_evaluations"][i],
            "cu_2nd_sem_credited": etl_t.Fact_Academic_Record["CU_2nd_sem_credited"][i],
            "cu_2nd_sem_enrolled": etl_t.Fact_Academic_Record["CU_2nd_sem_enrolled"][i],
            "cu_2nd_sem_evaluations": etl_t.Fact_Academic_Record["CU_2nd_sem_evaluations"][i],
            "cu_2nd_sem_approved": etl_t.Fact_Academic_Record["CU_2nd_sem_approved"][i],
            "cu_2nd_sem_grade": etl_t.Fact_Academic_Record["CU_2nd_sem_grade"][i],
            "cu_2nd_sem_without_evaluations": etl_t.Fact_Academic_Record["CU_2nd_sem_without_evaluations"][i],
            "target_outcome_id": t_id,
            "target_outcome": etl_t.Target_Outcome.get(t_id, ""),
        }

        matched = True
        for clause, args in filters:
            if "= ANY(%s)" in clause:
                col = clause.split(" = ANY(%s)")[0].strip()
                if rec.get(col) not in args[0]:
                    matched = False
                    break
            elif ">=" in clause and "<=" in clause:
                inverted = clause.startswith("NOT (")
                clean_c = clause[5:-1] if inverted else clause
                col = clean_c.split(" >= %s")[0].strip()
                val = float(rec.get(col) or 0.0)
                in_range = (args[0] <= val <= args[1])
                if (not in_range and not inverted) or (in_range and inverted):
                    matched = False
                    break

        if matched:
            rows.append(tuple(rec[f] for f in fields))

    if page_num is not None and page_size is not None and page_num > 0 and page_size > 0:
        start = (page_num - 1) * page_size
        rows = rows[start : start + page_size]

    return rows

def query_for_records(fields: list[str], filters: list[tuple[str, list]], page_num: int | None = None, page_size: int | None = None) -> Response:
    select_str = f"""
    SELECT {",".join(fields)} FROM
        Fact_Academic_Record 
        NATURAL JOIN Dim_Demographics
        NATURAL JOIN Dim_Socioeconomic
        NATURAL JOIN Dim_Academic_Course
        NATURAL JOIN Dim_Macroeconomic
        NATURAL JOIN Target_Outcome
    """

    where_clauses = ""
    arguments: tuple = ()
    if filters:
        where_clauses = f" WHERE {' AND '.join(map(lambda x: x[0], filters))}"
        arguments = sum(map(lambda x: x[1], filters), ())

    pagination_clause = ""
    if page_num is not None and page_size is not None and page_num > 0 and page_size > 0:
        offset = (page_num - 1) * page_size
        pagination_clause = f" ORDER BY student_id ASC LIMIT {int(page_size)} OFFSET {int(offset)}"

    final_query = select_str + where_clauses + pagination_clause + ';'

    conn = None
    try:
        conn, cursor = get_db()
        cursor.execute(final_query, arguments)
        res = cursor.fetchall()
        
    except psycopg2.OperationalError:
        # Fallback to ETL in-memory DW tables when PostgreSQL service is offline
        res = _fallback_in_memory_query(fields, filters, page_num, page_size)
    except Exception as e:
        if conn and not conn.closed:
            conn.rollback()
        return Response({}, ResponseCode.INTERNAL_ERROR, f"An unkown error has occured: {e}")

    return Response(res, ResponseCode.OK, "")

CACHED_RECORDS_COUNT: int | None = None

def get_records_count() -> int:
    global CACHED_RECORDS_COUNT

    if CACHED_RECORDS_COUNT:
        return CACHED_RECORDS_COUNT

    _, cursor = get_db()
    cursor.execute("SELECT COUNT(*) FROM Fact_Academic_Record;")
    CACHED_RECORDS_COUNT = int(cursor.fetchall()[0][0])

    return CACHED_RECORDS_COUNT

def import_new_records(records: dict[str, list]) -> Response:
    conn = None
    try:
        conn, cursor = get_db()
        Dim_Demographics_IDs = [
            row[0] for row in _insert_into_table(
                cursor,
                records,
                [
                    'marital_status_id',
                    'nationality_id',
                    'displaced',
                    'gender_id',
                    'age_at_enrollment',
                    'international',
                ],
                "Dim_Demographics",
                "Demographics_ID",
                unique_cols=['marital_status_id', 'nationality_id', 'displaced', 'gender_id', 'age_at_enrollment', 'international']
            )
        ]

        Dim_Socioeconomic_IDs = [
            row[0] for row in _insert_into_table(
                cursor,
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
                "Socioeconomic_ID",
                unique_cols=[
                    'mother_qualification_id', 'father_qualification_id',
                    'mother_occupation_id', 'father_occupation_id',
                    'debtor', 'tuition_fees_up_to_date',
                    'scholarship_holder', 'educational_special_needs'
                ]
            )
        ]

        Dim_Academic_Course_IDs = [
            row[0] for row in _insert_into_table(
                cursor,
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
                "Academic_Course_ID",
                unique_cols=[
                    'course_id', 'application_mode_id', 'application_order',
                    'previous_qualification_id', 'previous_qualification_grade',
                    'admission_grade', 'daytime_evening_attendance_id'
                ]
            )
        ]

        Dim_Macroeconomic_IDs = [
            row[0] for row in _insert_into_table(
                cursor,
                records,    
                [
                    'unemployment_rate',
                    'inflation_rate',
                    'gdp',
                ],
                "Dim_Macroeconomic",
                "Macroeconomic_ID",
                unique_cols=['unemployment_rate', 'inflation_rate', 'gdp']
            )
        ]

        foreign_keys = {
            'demographics_id': Dim_Demographics_IDs,
            'socioeconomic_id': Dim_Socioeconomic_IDs,
            'academic_course_id': Dim_Academic_Course_IDs,
            'macroeconomic_id': Dim_Macroeconomic_IDs,
        }

        returning = _insert_into_table(
            cursor,
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
            "student_id"
        )

        conn.commit()

    except Exception as e:
        if conn and not conn.closed:
            conn.rollback()
        print(f"Error {e}")
        return Response({}, ResponseCode.INTERNAL_ERROR, f"{e}")

    # Remove cached records count
    global CACHED_RECORDS_COUNT
    CACHED_RECORDS_COUNT = None

    return Response(returning, ResponseCode.OK, "")