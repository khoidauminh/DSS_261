"""
Hướng dẫn đọc ETL

Các biến Mother's Qualification và Father's Qualification được kết hợp thành Parent Qualification.
Tương tự với Parent Occupation.

Thông tin trong EXTRACT_RECORD sau đó được tách thành các bảng helper, các bảng dimension, và bảng fact.
Các dữ liệu điểm được chuẩn hoá thành thang 10 và ép kiểu thành dạng float.
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

foreign_keys: Final = list(range(1, EXTRACT_RECORDS['__count__']+1))

def to_bool(x: str) -> bool:
    match x.strip():
        case '1':
            return True
        case '0':
            return False
        
    raise ValueError(f'Invalid value "{x}": must be 0 or 1')

Fact_Academic_Record: Final = {
    'Demographics_ID': foreign_keys,
    'Socioeconomic_ID': foreign_keys,
    'Academic_Course_ID': foreign_keys,
    'Macroeconomic_ID': foreign_keys,

    'CU_1st_sem_credited': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (credited)"]),
    'CU_1st_sem_enrolled': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (enrolled)"]),
    'CU_1st_sem_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (evaluations)"]),
    'CU_1st_sem_approved': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (approved)"]),

    'CU_1st_sem_grade': transform(lambda x: float(x), EXTRACT_RECORDS["Curricular units 1st sem (grade)"]),
    
    'CU_1st_sem_without_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (without evaluations)"]),
    'CU_2nd_sem_credited': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (credited)"]),
    'CU_2nd_sem_enrolled': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (enrolled)"]),
    'CU_2nd_sem_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (evaluations)"]),
    'CU_2nd_sem_approved': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (approved)"]),

    'CU_2nd_sem_grade': transform(lambda x: float(x), EXTRACT_RECORDS["Curricular units 2nd sem (grade)"]),
    
    'CU_2nd_sem_without_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (without evaluations)"]),
    'Target_Outcome_ID': transform(lambda x: TARGET_OUTCOME_INVERT[x], EXTRACT_RECORDS["Target"]),
}

Dim_Demographics: Final = {
    'Marital_status_ID': transform(int, EXTRACT_RECORDS["Marital status"]),
    'Nationality_ID': transform(int, EXTRACT_RECORDS["Nacionality"]), # Nacionality because the csv has that typo
    'Displaced': transform(to_bool, EXTRACT_RECORDS["Displaced"]),
    'Gender_ID': transform(int, EXTRACT_RECORDS["Gender"]),
    'International': transform(to_bool, EXTRACT_RECORDS['International']),
    'Age_at_enrollment': transform(int, EXTRACT_RECORDS["Age at enrollment"]),
}

Dim_Socioeconomic: Final = {
    'Mother_qualification_ID': transform(int, EXTRACT_RECORDS["Mother's qualification"]),
    'Father_qualification_ID': transform(int, EXTRACT_RECORDS["Father's qualification"]),
    'Mother_occupation_ID': transform(int, EXTRACT_RECORDS["Mother's occupation"]),
    'Father_occupation_ID': transform(int, EXTRACT_RECORDS["Father's occupation"]),
    'Debtor': transform(to_bool, EXTRACT_RECORDS["Debtor"]),
    'Tuition_fees_up_to_date': transform(to_bool, EXTRACT_RECORDS["Tuition fees up to date"]),
    'Scholarship_holder': transform(to_bool, EXTRACT_RECORDS["Scholarship holder"]),
    'Educational_special_needs': transform(to_bool, EXTRACT_RECORDS["Educational special needs"])
}

Dim_Academic_Course: Final = {
    'Course_ID': transform(int, EXTRACT_RECORDS["Course"]),
    'Application_mode_ID': transform(int, EXTRACT_RECORDS["Application mode"]),
    'Application_order': transform(int, EXTRACT_RECORDS["Application order"]),
    'Previous_qualification_ID': transform(int, EXTRACT_RECORDS["Previous qualification"]),

    'Previous_qualification_grade': transform(lambda x: float(x), EXTRACT_RECORDS["Previous qualification (grade)"]),
    'Admission_grade': transform(lambda x: float(x), EXTRACT_RECORDS['Admission grade']),
    
    'Daytime_evening_attendance_ID': transform(int, EXTRACT_RECORDS["Daytime/evening attendance\t"]), # Has a tabulator character in the csv
}

Dim_Macroeconomic: Final = {
    'Unemployment_rate': transform(float, EXTRACT_RECORDS["Unemployment rate"]),
    'Unemployment_rate': transform(float, EXTRACT_RECORDS["Inflation rate"]),
    'Unemployment_rate': transform(float, EXTRACT_RECORDS["GDP"]),
}

print("[ETL] Finished transforming the raw data structure into tables")