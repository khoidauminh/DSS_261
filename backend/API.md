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

## POST /records/olap

API này dùng để tính toán, cộng gộp các records, chủ yếu dùng để tính tỷ lệ bỏ học.

### Input

Đầu vào giống như API /records/query, nhưng không có trường 'fields', các trường field được hardcode vào server.

```json
{
    "stats_only": true,
    "filters": {
        "debtor": {
            "type": "values",
            "values": [false]
        }
    }
}
```

Khi `stats_only` là `true`, server sẽ không trả về các record được tìm thấy mà chỉ trả về kết quả tính toán tỷ lệ bỏ học.

### Ouput

#### 200

Khi `stats_only` là true:

```json
{
    "code": "OK",
    "data": {
        "stats": {
            "count": 3921,
            "dropout_rate": 0.28283601122162716,
            "dropouts": 1109,
            "enrolled": 704
        }
    },
    "message": ""
}
```

Khi `stats_only` là false:

```json
{
    "code": "OK",
    "data": {
        "field_order": [
            "cu_1st_sem_approved",
            "cu_1st_sem_credited",
            "cu_1st_sem_enrolled",
            "cu_1st_sem_evaluations",
            "cu_1st_sem_grade",
            "cu_1st_sem_without_evaluations",
            "cu_2nd_sem_approved",
            "cu_2nd_sem_credited",
            "cu_2nd_sem_enrolled",
            "cu_2nd_sem_evaluations",
            "cu_2nd_sem_grade",
            "cu_2nd_sem_without_evaluations",
            "previous_qualification_grade",
            "admission_grade",
            "target_outcome_id"
        ],
        "records": [
            [
                0,
                0,
                0,
                0,
                "0.000",
                0,
                0,
                0,
                0,
                0,
                "0.000",
                0,
                "122.000",
                "127.300",
                0
            ],
            [
                6,
                0,
                6,
                6,
                "14.000",
                0,
                6,
                0,
                6,
                6,
                "13.667",
                0,
                "160.000",
                "142.500",
                1
            ],

            ...

            [
                6,
                0,
                6,
                8,
                "11.667",
                0,
                6,
                0,
                6,
                6,
                "13.000",
                0,
                "152.000",
                "152.000",
                1
            ]
        ],
        "stats": {
            "count": 3921,
            "dropout_rate": 0.2828,
            "dropouts": 1109,
            "graduated": 2108,
            "graduation_rate": 0.5376,
            "enrolled": 704,
            "enrolled_rate": 0.1795,
            "avg_admission_grade": 127.14,
            "avg_1st_sem_grade": 10.89,
            "avg_2nd_sem_grade": 10.58,
            "avg_1st_sem_approval_rate": 0.7812,
            "avg_2nd_sem_approval_rate": 0.7489
        }
    },
    "message": ""
}
```

`field_order` cho biết thứ tự các trường trong mỗi record.

---

## POST /records/olap/cube (OLAP Đa chiều - Roll-up / Drill-down / Slice & Dice)

API thực hiện gom nhóm (`group_by`) đa chiều kết hợp với bộ lọc (`filters`), tự động tính toán các độ đo (measures) và ánh xạ nhãn tên chiều từ các bảng danh mục.

### Input

```json
{
    "group_by": ["course_id", "scholarship_holder"],
    "filters": {
        "debtor": {
            "type": "values",
            "values": [false]
        }
    },
    "include_records": false
}
```

Các chiều `group_by` được hỗ trợ bao gồm:
- `course_id`, `application_mode_id`, `daytime_evening_attendance_id`, `previous_qualification_id`
- `gender_id`, `marital_status_id`, `nationality_id`, `displaced`, `international`, `age_at_enrollment`, `age_group` (`< 20`, `20 - 24`, `25 - 29`, `30+`)
- `scholarship_holder`, `debtor`, `tuition_fees_up_to_date`, `educational_special_needs`
- `unemployment_rate`, `inflation_rate`, `gdp`, `target_outcome_id`

### Output (200 OK)

```json
{
    "code": "OK",
    "data": {
        "group_by": ["course_id", "scholarship_holder"],
        "stats": {
            "count": 3921,
            "dropouts": 1109,
            "graduated": 2108,
            "enrolled": 704,
            "dropout_rate": 0.2828,
            "graduation_rate": 0.5376,
            "enrolled_rate": 0.1795,
            "avg_admission_grade": 127.14,
            "avg_1st_sem_grade": 10.89,
            "avg_2nd_sem_grade": 10.58,
            "avg_1st_sem_approval_rate": 0.7812,
            "avg_2nd_sem_approval_rate": 0.7489
        },
        "groups": [
            {
                "dimensions": {
                    "course_id": 9500,
                    "course_id_label": "Nursing",
                    "scholarship_holder": false,
                    "scholarship_holder_label": "No Scholarship"
                },
                "metrics": {
                    "count": 512,
                    "dropouts": 89,
                    "graduated": 340,
                    "enrolled": 83,
                    "dropout_rate": 0.1738,
                    "graduation_rate": 0.6641,
                    "enrolled_rate": 0.1621,
                    "avg_admission_grade": 130.45,
                    "avg_1st_sem_grade": 12.41,
                    "avg_2nd_sem_grade": 12.15,
                    "avg_1st_sem_approval_rate": 0.8612,
                    "avg_2nd_sem_approval_rate": 0.8420
                }
            }
        ]
    },
    "message": ""
}
```

---

## GET /records/metadata

Trả về danh sách các chiều hỗ trợ `group_by` và từ điển tra cứu ID $\rightarrow$ Tên hiển thị của tất cả các bảng Helper (`courses`, `genders`, `marital_statuses`, `application_modes`, `attendances`, `previous_qualifications`, `nationalities`, `target_outcomes`).

---

## Hệ hỗ trợ quyết định (DSS Endpoints)

### 1. GET /dss/model-info (và POST /dss/retrain)

Trả về thông tin đánh giá mô hình dự báo nguy cơ bỏ học (`Accuracy`, `Precision`, `Recall`, `F1-Score`, `ROC-AUC`, `Confusion Matrix`) và bảng xếp hạng mức độ ảnh hưởng của các thuộc tính (`feature_importance`).

### 2. POST /dss/predict (Dự báo cá nhân & Phân tích kịch bản What-If)

Dự đoán xác suất bỏ học cho một sinh viên có sẵn trong Data Warehouse (qua `student_id`) hoặc một hồ sơ sinh viên giả định, đồng thời mô phỏng các kịch bản can thiệp (*What-If Scenarios*) và sinh khuyến nghị cho cố vấn học tập.

#### Input (Theo `student_id` kèm tùy chọn ghi đè `overrides`)

```json
{
    "student_id": 1,
    "overrides": {
        "scholarship_holder": true
    }
}
```

Hoặc truyền hồ sơ trực tiếp:

```json
{
    "course_id": 9119,
    "gender_id": 1,
    "age_at_enrollment": 19,
    "tuition_fees_up_to_date": false,
    "debtor": true,
    "scholarship_holder": false,
    "admission_grade": 125.0,
    "previous_qualification_grade": 130.0,
    "cu_1st_sem_enrolled": 6,
    "cu_1st_sem_approved": 2,
    "cu_1st_sem_grade": 10.5,
    "cu_2nd_sem_enrolled": 6,
    "cu_2nd_sem_approved": 2,
    "cu_2nd_sem_grade": 9.8
}
```

#### Output (200 OK)

Trả về `dropout_probability`, `risk_level` (`HIGH` / `MEDIUM` / `LOW`), `risk_factors`, `what_if_scenarios` (3 kịch bản: Hỗ trợ tài chính, Phụ đạo học thuật, Can thiệp toàn diện kèm độ giảm rủi ro `probability_delta`), và `recommendations`.

### 3. POST /dss/early-warning (Danh sách cảnh báo sớm sinh viên đang theo học)

Quét toàn bộ 794 sinh viên đang ở trạng thái `Enrolled` (`target_outcome_id = 2`), chấm điểm rủi ro bỏ học bằng mô hình DSS và trả về danh sách ưu tiên can thiệp sớm.

#### Input

```json
{
    "limit": 20,
    "risk_level": "HIGH",
    "course_id": 9119
}
```
(Tất cả các trường đều là tùy chọn).