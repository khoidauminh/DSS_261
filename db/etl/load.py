"""
Hướng dẫn đọc ETL

Các dữ liệu đã sàng lọc và chuẩn hoá được insert tuần tự vào database. 
Hàm insert_helpers và insert_tables dự vào tên khoá của các dictionary để tự động nhập cột.

Bảng Fact_Academic_Record được nhập sau cùng do yêu cầu khoá ngoại.
Các khoá ngoại được tạo tuần tự, do đó không bắt buộc query lại sau khi nhập. 
"""

from psycopg2.extras import execute_batch

from itertools import count

from typing import Final
from .transform import (
    Marital_Status,
    Nationality,
    Parent_Qualification,
    Parent_Occupation,
    Course,
    Application_Mode,
    Previous_Qualification,
    Daytime_Evening_Attendance,
    Gender,
    Target_Outcome,

    Fact_Academic_Record,
    Dim_Demographics,
    Dim_Socioeconomic,
    Dim_Academic_Course,
    Dim_Macroeconomic
)

def insert_helpers(cursor, table, table_name, value_field_name=None):
    if not value_field_name:
        value_field_name = table_name

    insert_query: Final = f"INSERT INTO {table_name}({table_name}_ID, {value_field_name}) VALUES (%s, %s);"
    rows = list(table.items())

    execute_batch(cursor, insert_query, rows)

def insert_tables(cursor, table, table_name):
    keys = list(table.keys())
    rows = zip(*table.values())

    insert_query: Final = f"INSERT INTO {table_name}({", ".join(keys)}) VALUES ({", ".join(["%s"] * len(keys))});"
    
    execute_batch(cursor, insert_query, rows)

def load(cursor):
    insert_helpers(cursor, Marital_Status, "Marital_Status")
    insert_helpers(cursor, Nationality, "Nationality")
    insert_helpers(cursor, Gender, "Gender")

    insert_tables(cursor, Dim_Demographics, "Dim_Demographics")

    insert_helpers(cursor, Parent_Occupation, "Parent_Occupation", "Occupation")
    insert_helpers(cursor, Parent_Qualification, "Parent_Qualification", "Qualification")

    insert_tables(cursor, Dim_Socioeconomic, "Dim_Socioeconomic")

    insert_helpers(cursor, Course, "Course")
    insert_helpers(cursor, Application_Mode, "Application_Mode")
    insert_helpers(cursor, Previous_Qualification, "Previous_Qualification")
    insert_helpers(cursor, Daytime_Evening_Attendance, "Daytime_Evening_Attendance")

    insert_tables(cursor, Dim_Academic_Course, "Dim_Academic_Course")

    insert_tables(cursor, Dim_Macroeconomic, "Dim_Macroeconomic")

    insert_helpers(cursor, Target_Outcome, "Target_Outcome")

    insert_tables(cursor, Fact_Academic_Record, "Fact_Academic_Record")

    print("[ETL] Finished loading all values into PostgresSQL connection")
