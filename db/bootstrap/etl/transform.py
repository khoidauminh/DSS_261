from typing import Final
from .extract import EXTRACT_RECORDS, COLUMN_MAP

# Helper/trivial tables
MARITAL_STATUS: Final = COLUMN_MAP["Marital status"]
NATIONALITY: Final = COLUMN_MAP["Nationality"]
PARENT_QUALIFICATION: Final = COLUMN_MAP["Parent's qualification"]
PARENT_OCCUPATION: Final = COLUMN_MAP["Parent's occupation"]
COURSE: Final = COLUMN_MAP["Course"]
APPLICATION_MODE: Final = COLUMN_MAP["Application mode"]
PREVIOUS_QUALIFICATION: Final = COLUMN_MAP["Previous qualification"]
DAYTIME_EVENING_ATTENDACE: Final = COLUMN_MAP["Daytime/evening attendance"]
GENDER: Final = COLUMN_MAP["Gender"]

TARGET_OUTCOME: Final = dict(enumerate(COLUMN_MAP["Target"]))
TARGET_OUTCOME_INVERT: Final = {value: key for key, value in TARGET_OUTCOME.items()} # To convert Target to its IDs

def transform(convert_function, raw_list):
    return list(map(convert_function, raw_list))

Fact_Academic_Record: Final = {
    'CU_1st_sem_credited': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (credited)"]),
    'CU_1st_sem_enrolled': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (enrolled)"]),
    'CU_1st_sem_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (evaluations)"]),
    'CU_1st_sem_approved': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (approved)"]),
    'CU_1st_sem_grade': transform(float, EXTRACT_RECORDS["Curricular units 1st sem (grade)"]),
    'CU_1st_sem_without_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 1st sem (without evaluations)"]),
    'CU_2nd_sem_credited': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (credited)"]),
    'CU_2nd_sem_enrolled': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (enrolled)"]),
    'CU_2nd_sem_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (evaluations)"]),
    'CU_2nd_sem_approved': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (approved)"]),
    'CU_2nd_sem_grade': transform(float, EXTRACT_RECORDS["Curricular units 2nd sem (grade)"]),
    'CU_2nd_sem_without_evaluations': transform(int, EXTRACT_RECORDS["Curricular units 2nd sem (without evaluations)"]),
    'Target_Outcome_ID': transform(lambda x: TARGET_OUTCOME_INVERT[x], EXTRACT_RECORDS["Target"]),
}

Dim_Demographics: Final = {
    'Marital_status_ID': transform(int, EXTRACT_RECORDS["Marital status"]),
    'Nationality_ID': transform(int, EXTRACT_RECORDS["Nacionality"]), # Nacionality because the csv has that typo
    'Displaced': transform(bool, EXTRACT_RECORDS["Displaced"]),
    'Gender_ID': transform(int, EXTRACT_RECORDS["Gender"]),
    'Age_at_enrollment': transform(int, EXTRACT_RECORDS["Age at enrollment"]),
}

Dim_Socioeconomic: Final = {
    'Mother_qualification_ID': transform(int, EXTRACT_RECORDS["Mother's qualification"]),
    'Father_qualification_ID': transform(int, EXTRACT_RECORDS["Father's qualification"]),
    'Mother_occupation_ID': transform(int, EXTRACT_RECORDS["Mother's occupation"]),
    'Father_occupation_ID': transform(int, EXTRACT_RECORDS["Father's occupation"]),
    'Debtor': transform(bool, EXTRACT_RECORDS["Debtor"]),
    'Tuition_fees_up_to_date': transform(bool, EXTRACT_RECORDS["Tuition fees up to date"]),
    'Scholarship_holder': transform(bool, EXTRACT_RECORDS["Scholarship holder"]),
}

Dim_Academic_Course: Final = {
    'Course_ID': transform(int, EXTRACT_RECORDS["Course"]),
    'Application_mode_ID': transform(int, EXTRACT_RECORDS["Application mode"]),
    'Application_order': transform(int, EXTRACT_RECORDS["Application order"]),
    'Previous_qualification_ID': transform(int, EXTRACT_RECORDS["Previous qualification"]),
    'Daytime_evening_attendance_ID': transform(int, EXTRACT_RECORDS["Daytime/evening attendance\t"]), # Has a tabulator character in the csv
}

Dim_Macroeconomic: Final = {
    'Unemployment_rate': transform(float, EXTRACT_RECORDS["Unemployment rate"]),
    'Unemployment_rate': transform(float, EXTRACT_RECORDS["Inflation rate"]),
    'Unemployment_rate': transform(float, EXTRACT_RECORDS["GDP"]),
}

print("[ETL] Finished transforming the raw data structure into tables")