from typing import Final, Any
from ..util.response import Response, ResponseCode
from ..service.fact_academic_record import query_for_records
from db.etl import column_map

ReturningObject: Final = [
    'cu_1st_sem_approved',
    'cu_1st_sem_credited',
    'cu_1st_sem_enrolled',
    'cu_1st_sem_evaluations',
    'cu_1st_sem_grade',
    'cu_1st_sem_without_evaluations',
    'cu_2nd_sem_approved',
    'cu_2nd_sem_credited',
    'cu_2nd_sem_enrolled',
    'cu_2nd_sem_evaluations',
    'cu_2nd_sem_grade',
    'cu_2nd_sem_without_evaluations',
    'previous_qualification_grade',
    'admission_grade',
    'target_outcome_id'
]

ReturningObjectMap: Final = {name: index for index, name in enumerate(ReturningObject)}
TargetOutCome: Final = ReturningObjectMap['target_outcome_id']

# Supported OLAP Group-By Dimensions & their label mappings
RAW_MAP = column_map.RAW_MAP
TARGET_LABELS = {0: "Dropout", 1: "Graduate", 2: "Enrolled"}

DIMENSION_LABEL_MAP: Final[dict[str, dict[Any, str]]] = {
    "course_id": {int(k): v for k, v in RAW_MAP["Course"].items()},
    "gender_id": {int(k): v for k, v in RAW_MAP["Gender"].items()},
    "marital_status_id": {int(k): v for k, v in RAW_MAP["Marital status"].items()},
    "application_mode_id": {int(k): v for k, v in RAW_MAP["Application mode"].items()},
    "daytime_evening_attendance_id": {int(k): v for k, v in RAW_MAP["Daytime/evening attendance"].items()},
    "previous_qualification_id": {int(k): v for k, v in RAW_MAP["Previous qualification"].items()},
    "nationality_id": {int(k): v for k, v in RAW_MAP["Nationality"].items()},
    "mother_qualification_id": {int(k): v for k, v in RAW_MAP["Mother's qualification"].items()},
    "father_qualification_id": {int(k): v for k, v in RAW_MAP["Father's qualification"].items()},
    "mother_occupation_id": {int(k): v for k, v in RAW_MAP["Mother's occupation"].items()},
    "father_occupation_id": {int(k): v for k, v in RAW_MAP["Father's occupation"].items()},
    "target_outcome_id": TARGET_LABELS,
    "scholarship_holder": {True: "Scholarship Holder", False: "No Scholarship"},
    "debtor": {True: "Debtor", False: "Non-Debtor"},
    "tuition_fees_up_to_date": {True: "Up to Date", False: "Overdue"},
    "displaced": {True: "Displaced", False: "Not Displaced"},
    "international": {True: "International", False: "Domestic"},
    "educational_special_needs": {True: "Special Needs", False: "No Special Needs"},
}

SUPPORTED_GROUP_BY: Final[set[str]] = set(DIMENSION_LABEL_MAP.keys()) | {
    "age_at_enrollment",
    "age_group",
    "application_order",
    "unemployment_rate",
    "inflation_rate",
    "gdp",
}

def _get_age_group(age: int) -> str:
    if age < 20:
        return "< 20"
    elif age <= 24:
        return "20 - 24"
    elif age <= 29:
        return "25 - 29"
    else:
        return "30+"

def _compute_group_stats(rows: list, idx_map: dict[str, int]) -> dict:
    count = len(rows)
    if count == 0:
        return {
            "count": 0,
            "dropouts": 0,
            "graduated": 0,
            "enrolled": 0,
            "dropout_rate": 0.0,
            "graduation_rate": 0.0,
            "enrolled_rate": 0.0,
            "avg_admission_grade": 0.0,
            "avg_1st_sem_grade": 0.0,
            "avg_2nd_sem_grade": 0.0,
            "avg_1st_sem_approval_rate": 0.0,
            "avg_2nd_sem_approval_rate": 0.0,
        }

    dropouts = 0
    graduated = 0
    enrolled = 0
    sum_adm = 0.0
    sum_g1 = 0.0
    sum_g2 = 0.0
    sum_app1 = 0.0
    sum_enr1 = 0.0
    sum_app2 = 0.0
    sum_enr2 = 0.0

    i_target = idx_map["target_outcome_id"]
    i_adm = idx_map["admission_grade"]
    i_g1 = idx_map["cu_1st_sem_grade"]
    i_g2 = idx_map["cu_2nd_sem_grade"]
    i_app1 = idx_map["cu_1st_sem_approved"]
    i_enr1 = idx_map["cu_1st_sem_enrolled"]
    i_app2 = idx_map["cu_2nd_sem_approved"]
    i_enr2 = idx_map["cu_2nd_sem_enrolled"]

    for r in rows:
        t = r[i_target]
        if t == 0:
            dropouts += 1
        elif t == 1:
            graduated += 1
        elif t == 2:
            enrolled += 1

        sum_adm += float(r[i_adm] or 0.0)
        sum_g1 += float(r[i_g1] or 0.0)
        sum_g2 += float(r[i_g2] or 0.0)
        sum_app1 += int(r[i_app1] or 0)
        sum_enr1 += int(r[i_enr1] or 0)
        sum_app2 += int(r[i_app2] or 0)
        sum_enr2 += int(r[i_enr2] or 0)

    return {
        "count": count,
        "dropouts": dropouts,
        "graduated": graduated,
        "enrolled": enrolled,
        "dropout_rate": round(dropouts / count, 4),
        "graduation_rate": round(graduated / count, 4),
        "enrolled_rate": round(enrolled / count, 4),
        "avg_admission_grade": round(sum_adm / count, 2),
        "avg_1st_sem_grade": round(sum_g1 / count, 2),
        "avg_2nd_sem_grade": round(sum_g2 / count, 2),
        "avg_1st_sem_approval_rate": round(sum_app1 / sum_enr1, 4) if sum_enr1 > 0 else 0.0,
        "avg_2nd_sem_approval_rate": round(sum_app2 / sum_enr2, 4) if sum_enr2 > 0 else 0.0,
    }

def olap_generic(filters: dict, stats_only: bool, group_by: list[str] | None = None) -> Response:
    if group_by:
        return olap_cube(filters=filters, group_by=group_by, include_records=not stats_only)

    returning = query_for_records({
        "fields": ReturningObject,
        "filters": filters
    })
    
    if returning.response_code != ResponseCode.OK:
        return returning

    data = returning.data
    stats = _compute_group_stats(data, ReturningObjectMap)

    out: dict = {"stats": stats}

    if not stats_only:
        out.update({
            'records': data,
            'field_order': ReturningObject
        })
        
    return Response(out, ResponseCode.OK, "")

def olap_cube(filters: dict, group_by: list[str], include_records: bool = False) -> Response:
    """
    Thực hiện các phép toán OLAP đa chiều:
    - Slice & Dice (thông qua `filters`)
    - Roll-up & Drill-down (thông qua `group_by` 1 hoặc nhiều chiều)
    - Tự động ánh xạ nhãn tên chiều từ bảng Helper (`DIMENSION_LABEL_MAP`)
    """
    if not isinstance(group_by, list) or not group_by:
        return Response({}, ResponseCode.QUERY_INVALID_GENERIC, "group_by must be a non-empty list of dimension fields")

    for dim in group_by:
        if dim not in SUPPORTED_GROUP_BY:
            return Response({}, ResponseCode.QUERY_UNKNOWN_KEY, f"Unsupported group_by dimension: {dim}")

    query_fields = list(ReturningObject)
    for dim in group_by:
        actual_col = "age_at_enrollment" if dim == "age_group" else dim
        if actual_col not in query_fields:
            query_fields.append(actual_col)

    returning = query_for_records({
        "fields": query_fields,
        "filters": filters
    })

    if returning.response_code != ResponseCode.OK:
        return returning

    data = returning.data
    idx_map = {name: index for index, name in enumerate(query_fields)}

    overall_stats = _compute_group_stats(data, idx_map)

    grouped_rows: dict[tuple, list] = {}
    for row in data:
        key_parts = []
        for dim in group_by:
            if dim == "age_group":
                age_val = int(row[idx_map["age_at_enrollment"]])
                key_parts.append(_get_age_group(age_val))
            else:
                val = row[idx_map[dim]]
                if isinstance(val, (int, bool, str)):
                    key_parts.append(val)
                else:
                    key_parts.append(float(val))
        key_tuple = tuple(key_parts)
        grouped_rows.setdefault(key_tuple, []).append(row)

    groups_out = []
    for key_tuple, rows in grouped_rows.items():
        dim_info = {}
        for i, dim in enumerate(group_by):
            raw_val = key_tuple[i]
            dim_info[dim] = raw_val
            if dim in DIMENSION_LABEL_MAP:
                dim_info[f"{dim}_label"] = DIMENSION_LABEL_MAP[dim].get(raw_val, str(raw_val))
            elif dim == "age_group":
                dim_info["age_group_label"] = str(raw_val)

        group_metrics = _compute_group_stats(rows, idx_map)
        groups_out.append({
            "dimensions": dim_info,
            "metrics": group_metrics
        })

    groups_out.sort(key=lambda g: g["metrics"]["count"], reverse=True)

    out = {
        "group_by": group_by,
        "stats": overall_stats,
        "groups": groups_out,
    }
    if include_records:
        out["records"] = data
        out["field_order"] = query_fields

    return Response(out, ResponseCode.OK, "")

def get_metadata() -> Response:
    """
    Trả về danh mục các chiều (Dimensions) và bảng tra cứu ID -> Tên để hỗ trợ truy vấn OLAP & DSS.
    """
    return Response(
        {
            "supported_group_by": sorted(list(SUPPORTED_GROUP_BY)),
            "courses": RAW_MAP["Course"],
            "genders": RAW_MAP["Gender"],
            "marital_statuses": RAW_MAP["Marital status"],
            "application_modes": RAW_MAP["Application mode"],
            "attendances": RAW_MAP["Daytime/evening attendance"],
            "previous_qualifications": RAW_MAP["Previous qualification"],
            "nationalities": RAW_MAP["Nationality"],
            "target_outcomes": {str(k): v for k, v in TARGET_LABELS.items()},
        },
        ResponseCode.OK,
        ""
    )
