# API

Hiện tại server có 2 api chính, một dùng để thêm dữ liệu vào database, và cái còn lại để query dữ liệu.

## POST /records/

API yêu cầu một list các json object, mỗi object là một record mới để thêm vào. Các trường của object phải được viết tương ứng với các tên trường trong bảng database. Xem trong đây để biết các trường nào
bắt buộc và trường nào không bắt buộc:

[student_record.py](./validator/student_record.py)

Lưu ý, các dữ liệu trong bảng khác (như `nationality`, `gender`, `course`, vv), phải được nhập theo giá trị id của chúng trong database, không phải giá trị thật. Tra cứu giá trị tại đây:

[column_map.py](../db/etl/column_map.py)

### Input

Ví dụ input như sau:

```json
[
    {
        "admission_grade": 10.0,
        "age_at_enrollment": 10,
        "application_mode_id": 1,
        "application_order": 1,
        "course_id": 33,
        "cu_1st_sem_approved": 1,
        "cu_1st_sem_credited": 1,
        "cu_1st_sem_enrolled": 1,
        "cu_1st_sem_evaluations": 1,
        "cu_1st_sem_grade": 10.0,
        "cu_1st_sem_without_evaluations": 1,
        "cu_2nd_sem_approved": 1,
        "cu_2nd_sem_credited": 1,
        "cu_2nd_sem_enrolled": 1,
        "cu_2nd_sem_evaluations": 1,
        "cu_2nd_sem_grade": 10.0,
        "cu_2nd_sem_without_evaluations": 1,
        "daytime_evening_attendance": 1,
        "gender_id": 0,
        "marital_status_id": 1,
        "nationality_id": 1,
        "previous_qualification_grade": 10.0
    }
]

```

### Response

Trả về một json object khi thành công, hoặc text khi lỗi

#### 200

Ví dụ:

```json
{
    "code": "OK",
    "data": [
        [
            4430
        ]
    ],
    "message": ""
}
```

#### 400

Sai tên trường:

```json
{
    "code": "INSERT_INVALID_KEY",
    "data": {},
    "message": "Record 1: Invalid key \"gender\""
}
```

Thiếu các trường bắt buộc:

```json
{
    "code": "INSERT_MISSING_REQUIRED_KEYS",
    "data": {},
    "message": "Record 1: Missing the following keys:\n\tgender_id"
}
```

#### 500

Lỗi khác:

```json
{
    "code": "INTERNAL_ERROR",
    "data": {},
    "message": "insert or update on table \"dim_academic_course\" violates foreign key constraint \"dim_academic_course_application_mode_id_fkey\"\nDETAIL:  Key (application_mode_id)=(12) is not present in table \"application_mode\".\n"
}
```

## POST /records/query

Input mang template như sau:

```json
{
    "fields": [...],
    "filters": {
        "..." : {...}
    }
}
```

Trường `fields` chứa danh sách các cột để trả về. Chỉ có thể trả về các cột trong bảng Dim_* và bảng Fact_*, các dữ liệu trong bảng khác cần tra trong [column_map.py](../db/etl/column_map.py).

Trường `filters` là một object chứa các bộ lọc. Có 2 bộ lọc chính:

### Filter by values (lọc chính xác)

```json
"age_at_enrollment": {
    "type": "values",
    "values": [20, 21]
}
```

`Values` là một danh sách các giá trị để lọc, so sánh chính xác với dữ liệu trong database.

### Filter by range (lọc trong khoảng)

```json
"age_at_enrollment": {
    "type": "range",
    "left": 0,
    "right": 20,
    "inverted": false
}
```

`left` và `right` lần lượt là chặn trái và chặn phải của khoảng: `[left, right]`.

`inverted` (không bắt buộc), khi `true` đảo ngược điều kiện: `(-inf, left) U (right, +inf)`.

### Ví dụ

```json
{
    "fields": ["student_id", "cu_1st_sem_grade"],
    "filters": {
        "gender_id": {
            "type": "values",
            "values": [0]
        },

        "age_at_enrollment": {
            "type": "range",
            "left": 0,
            "right": 20
        }
    }
}
```

Lấy danh sách `student_id` và `cu_1st_sem_grade` lọc theo giới tính 0 (nữ), và độ tuổi từ 0 đến 20.

### Response

#### 200

```json
    {
    "code": "OK",
    "data": [
        [
            "6.17",
            5
        ],
        [
            "6.94",
            9
        ],

        ...

        [
            "5.83",
            4424
        ]
    "message": ""
}
```

#### 400

Không có trường type trong filter:

```json
{
    "code": "QUERY_MISSING_FILTER_TYPE",
    "data": {},
    "message": "Missing required type of filter"
}
```

Filter type values nhưng trường value là list rỗng:

```json
{
    "code": "QUERY_FILTER_MISSING_VALUE",
    "data": {},
    "message": "No values in value filter"
}
```

Thiếu trường left, right hoặc cả hai:

```json
{
    "code": "QUERY_FILTER_MISSING_VALUE",
    "data": {},
    "message": "Missing required range value of range type filter"
}
```

Sai tên cột trong filter:

```json
{
    "code": "QUERY_UNKNOWN_KEY",
    "data": {},
    "message": "Unknown filter age_at_enrollmen in filters"
}
```

Sai tên kiểu filter:

```json
{
    "code": "QUERY_INVALID_GENERIC",
    "data": {},
    "message": "Unknown filter type for filter age_at_enrollment: s"
}
```

Sai tên cột trong fields:

```json
{
    "code": "QUERY_UNKNOWN_KEY",
    "data": {},
    "message": "Unknown key student in query"
}
```

Lỗi khác:

```json
{
    "code": "INTERNAL_ERROR",
    "data": {},
    "message": "An unkown error has occured: operator does not exist: integer = text\nLINE 9:     WHERE gender_id = ANY(ARRAY['range']) AND NOT (age_at_en...\n                            ^\nHINT:  No operator matches the given name and argument types. You might need to add explicit type casts.\n"
}
```
