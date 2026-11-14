from .student_record import StudentRecordAll, FieldAliases
from ..util.response import Response, ResponseCode

def _parse_filter(field_name: str, filter_json: dict) -> Response | tuple[str, tuple]:
    if not (type := filter_json.get('type', None)):
        return Response({}, ResponseCode.QUERY_MISSING_FILTER_TYPE, "Missing required type of filter")

    match type:
        case 'range':
            try:
                left = float(filter_json['left'])
                right = float(filter_json['right'])
                raw_inv = filter_json.get('inverted', False)
                inverted = raw_inv if isinstance(raw_inv, bool) else str(raw_inv).lower() == "true"
            except KeyError:
                return Response({}, ResponseCode.QUERY_FILTER_MISSING_VALUE, "Missing required range value of range type filter")
            except ValueError:
                return Response({}, ResponseCode.QUERY_FILTER_INVALID_VALUE, "Invalid value(s) of range type filter")
            except: 
                return Response({}, ResponseCode.INTERNAL_ERROR, "An unknown error has occured")

            return ("NOT (%s)" if inverted else "%s") % (f"{field_name} >= %s AND {field_name} <= %s"), (left, right,)

        case 'values':
            try:
                vals = filter_json['values']

                if not vals:
                    return Response({}, ResponseCode.QUERY_FILTER_MISSING_VALUE, "No values in value filter")

            except KeyError:
                return Response({}, ResponseCode.QUERY_FILTER_MISSING_VALUE, "Missing required value(s) field for value type filter")

            return f"{field_name} = ANY(%s)", (vals,)

        case _:
           return Response({}, ResponseCode.QUERY_INVALID_GENERIC, f"Unknown filter type for filter {field_name}: {type}")
    
    return Response({}, ResponseCode.INTERNAL_ERROR, "An unknown error has occured")

def parse(query: dict) -> Response | dict:
    fields: list[str] = []
    filters: list[tuple[str, tuple]] = []
    seen_filters: set[str] = set()

    try:
        page = int(query['page']) if 'page' in query else None
        page_size = int(query['page_size']) if 'page_size' in query else None
    except Exception as e:
        return Response({}, ResponseCode.QUERY_INVALID_GENERIC, f"Invalid value for page and/or page_size")

    if field := query.get('fields', None):
        for raw_k in field:
            k = FieldAliases.get(raw_k, raw_k)
            if k not in StudentRecordAll and k != "student_id" and k != "target_outcome":
                return Response({}, ResponseCode.QUERY_UNKNOWN_KEY, f"Unknown key {raw_k} in query")

            if k in fields:
                return Response({}, ResponseCode.QUERY_DUPLICATE, f"Key {raw_k} specified twice in query")

            fields.append(k)
    else:
        fields = ["student_id"]

    if filter_list := query.get('filters', None):
        for raw_k, v in filter_list.items():
            k = FieldAliases.get(raw_k, raw_k)
            if k not in StudentRecordAll and k != "student_id":
                return Response({}, ResponseCode.QUERY_UNKNOWN_KEY, f'Unknown filter {raw_k} in filters')

            if k in seen_filters:
                return Response({}, ResponseCode.QUERY_DUPLICATE, f"Filter {raw_k} specified twice in filter list")

            seen_filters.add(k)

            if isinstance(clause := _parse_filter(k, v), Response):
                return clause

            filters.append(clause)

    return {'fields': fields, 'filters': filters, 'page_num': page, 'page_size': page_size}