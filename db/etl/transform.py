"""
Hướng dẫn đọc ETL

Các biến Mother's Qualification và Father's Qualification được kết hợp thành Parent Qualification.
Tương tự với Parent Occupation.

Thông tin trong EXTRACT_RECORD sau đó được làm sạch (clean), kiểm tra miền giá trị (validate),
loại bỏ trùng lặp các bảng chiều (Deduplicate Dimensions - Surrogate Keys) và ánh xạ khóa ngoại vào bảng Fact.
"""

from typing import Final
from .extract import EXTRACT_RECORDS, COLUMN_MAP
from .util import transform

# Helper/trivial tables
Marital_Status: Final = COLUMN_MAP["Marital status"]
Nationality: Final = COLUMN_MAP["Nationality"]
Parent_Qualification: Final = COLUMN_MAP["Parent's qualification"]
Parent_Occupation: Final = COLUMN_MAP["Parent's occupation"]
Course: Final = COLUMN_MAP["Course"]
Application_Mode: Final = COLUMN_MAP["Application mode"]
Previous_Qualification: Final = COLUMN_MAP["Previous qualification"]
Daytime_Evening_Attendance: Final = COLUMN_MAP["Daytime/evening attendance"]
Gender: Final = COLUMN_MAP["Gender"]

Target_Outcome: Final = dict(enumerate(COLUMN_MAP["Target"]))
TARGET_OUTCOME_INVERT: Final = {value: key for key, value in Target_Outcome.items()} # To convert Target to its IDs

def to_bool(x: str) -> bool:
    match str(x).strip():
        case '1' | 'true' | 'True':
            return True
        case '0' | 'false' | 'False':
            return False
        
    raise ValueError(f'Invalid boolean value "{x}": must be 0 or 1')

def clean_int(x: str, min_val: int | None = None, max_val: int | None = None) -> int:
    val = int(str(x).strip())
    if min_val is not None and val < min_val:
        raise ValueError(f"Value {val} < min {min_val}")
    if max_val is not None and val > max_val:
        raise ValueError(f"Value {val} > max {max_val}")
    return val

def clean_float(x: str, min_val: float | None = None, max_val: float | None = None, digits: int = 3) -> float:
    val = round(float(str(x).strip()), digits)
    if min_val is not None and val < min_val:
        raise ValueError(f"Value {val} < min {min_val}")
    if max_val is not None and val > max_val:
        raise ValueError(f"Value {val} > max {max_val}")
    return val

def deduplicate_dimension(raw_columns: dict[str, list]) -> tuple[dict[str, list], list[int]]:
    """
    Gom các dòng trùng lặp trong bảng Dimension thành các dòng duy nhất (Unique Dimension Rows)
    và trả về:
      1. Bảng Dimension đã deduplicate (với surrogate ID từ 1..K)
      2. Danh sách khóa ngoại (chiều dài N bằng bảng Fact) trỏ tới surrogate ID tương ứng
    """
    keys = list(raw_columns.keys())
    num_rows = len(raw_columns[keys[0]]) if keys else 0

    unique_map: dict[tuple, int] = {}
    dedup_columns: dict[str, list] = {k: [] for k in keys}
    fk_list: list[int] = []

    for i in range(num_rows):
        row_tuple = tuple(raw_columns[k][i] for k in keys)
        if row_tuple not in unique_map:
            new_id = len(unique_map) + 1
            unique_map[row_tuple] = new_id
            for k_idx, k in enumerate(keys):
                dedup_columns[k].append(row_tuple[k_idx])
        fk_list.append(unique_map[row_tuple])

    return dedup_columns, fk_list

# Raw dimension columns (before deduplication)
_raw_demographics = {
    'Marital_status_ID': transform(clean_int, EXTRACT_RECORDS["Marital status"]),
    'Nationality_ID': transform(clean_int, EXTRACT_RECORDS.get("Nacionality") or EXTRACT_RECORDS["Nationality"]),
    'Displaced': transform(to_bool, EXTRACT_RECORDS["Displaced"]),
    'Gender_ID': transform(clean_int, EXTRACT_RECORDS["Gender"]),
    'International': transform(to_bool, EXTRACT_RECORDS['International']),
    'Age_at_enrollment': transform(lambda x: clean_int(x, min_val=1), EXTRACT_RECORDS["Age at enrollment"]),
}

_raw_socioeconomic = {
    'Mother_qualification_ID': transform(clean_int, EXTRACT_RECORDS["Mother's qualification"]),
    'Father_qualification_ID': transform(clean_int, EXTRACT_RECORDS["Father's qualification"]),
    'Mother_occupation_ID': transform(clean_int, EXTRACT_RECORDS["Mother's occupation"]),
    'Father_occupation_ID': transform(clean_int, EXTRACT_RECORDS["Father's occupation"]),
    'Debtor': transform(to_bool, EXTRACT_RECORDS["Debtor"]),
    'Tuition_fees_up_to_date': transform(to_bool, EXTRACT_RECORDS["Tuition fees up to date"]),
    'Scholarship_holder': transform(to_bool, EXTRACT_RECORDS["Scholarship holder"]),
    'Educational_special_needs': transform(to_bool, EXTRACT_RECORDS["Educational special needs"])
}

_attendance_col = (
    EXTRACT_RECORDS.get("Daytime/evening attendance\t")
    or EXTRACT_RECORDS.get("Daytime/evening attendance")
)

_raw_academic_course = {
    'Course_ID': transform(clean_int, EXTRACT_RECORDS["Course"]),
    'Application_mode_ID': transform(clean_int, EXTRACT_RECORDS["Application mode"]),
    'Application_order': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Application order"]),
    'Previous_qualification_ID': transform(clean_int, EXTRACT_RECORDS["Previous qualification"]),
    'Previous_qualification_grade': transform(lambda x: clean_float(x, 0.0, 200.0, 3), EXTRACT_RECORDS["Previous qualification (grade)"]),
    'Admission_grade': transform(lambda x: clean_float(x, 0.0, 200.0, 3), EXTRACT_RECORDS['Admission grade']),
    'Daytime_evening_attendance_ID': transform(clean_int, _attendance_col),
}

_raw_macroeconomic = {
    'Unemployment_rate': transform(lambda x: clean_float(x, -100.0, 100.0, 2), EXTRACT_RECORDS["Unemployment rate"]),
    'Inflation_rate': transform(lambda x: clean_float(x, -100.0, 100.0, 2), EXTRACT_RECORDS["Inflation rate"]),
    'GDP': transform(lambda x: clean_float(x, -100.0, 100.0, 2), EXTRACT_RECORDS["GDP"]),
}

# Deduplicate all 4 dimensions & generate foreign key references for Fact_Academic_Record
Dim_Demographics, _fk_demographics = deduplicate_dimension(_raw_demographics)
Dim_Socioeconomic, _fk_socioeconomic = deduplicate_dimension(_raw_socioeconomic)
Dim_Academic_Course, _fk_academic_course = deduplicate_dimension(_raw_academic_course)
Dim_Macroeconomic, _fk_macroeconomic = deduplicate_dimension(_raw_macroeconomic)

Fact_Academic_Record: Final = {
    'Demographics_ID': _fk_demographics,
    'Socioeconomic_ID': _fk_socioeconomic,
    'Academic_Course_ID': _fk_academic_course,
    'Macroeconomic_ID': _fk_macroeconomic,

    'CU_1st_sem_credited': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 1st sem (credited)"]),
    'CU_1st_sem_enrolled': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 1st sem (enrolled)"]),
    'CU_1st_sem_evaluations': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 1st sem (evaluations)"]),
    'CU_1st_sem_approved': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 1st sem (approved)"]),
    'CU_1st_sem_grade': transform(lambda x: clean_float(x, 0.0, 200.0, 3), EXTRACT_RECORDS["Curricular units 1st sem (grade)"]),
    'CU_1st_sem_without_evaluations': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 1st sem (without evaluations)"]),

    'CU_2nd_sem_credited': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 2nd sem (credited)"]),
    'CU_2nd_sem_enrolled': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 2nd sem (enrolled)"]),
    'CU_2nd_sem_evaluations': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 2nd sem (evaluations)"]),
    'CU_2nd_sem_approved': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 2nd sem (approved)"]),
    'CU_2nd_sem_grade': transform(lambda x: clean_float(x, 0.0, 200.0, 3), EXTRACT_RECORDS["Curricular units 2nd sem (grade)"]),
    'CU_2nd_sem_without_evaluations': transform(lambda x: clean_int(x, min_val=0), EXTRACT_RECORDS["Curricular units 2nd sem (without evaluations)"]),

    'Target_Outcome_ID': transform(lambda x: TARGET_OUTCOME_INVERT[str(x).strip()], EXTRACT_RECORDS["Target"]),
}

ETL_SUMMARY: Final = {
    "total_extracted_rows": EXTRACT_RECORDS['__count__'],
    "fact_academic_record_rows": len(Fact_Academic_Record['Demographics_ID']),
    "dim_demographics_unique_rows": len(Dim_Demographics['Marital_status_ID']),
    "dim_socioeconomic_unique_rows": len(Dim_Socioeconomic['Debtor']),
    "dim_academic_course_unique_rows": len(Dim_Academic_Course['Course_ID']),
    "dim_macroeconomic_unique_rows": len(Dim_Macroeconomic['GDP']),
}

print(f"[ETL] Finished transforming & deduplicating raw data: {ETL_SUMMARY}")