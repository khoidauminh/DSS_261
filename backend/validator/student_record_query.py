from .student_record import StudentRecordAll
from ..util.response import Response, ResponseCode

def _parse_filter(field_name: str, filter_json: dict) -> Response | tuple[str, tuple]:
    if not (type := filter_json.get('type', None)):
        return Response({}, ResponseCode.QUERY_MISSING_FILTER_TYPE, "Missing required type of filter")

    match type:
        case 'range':
            try:
                left = float(filter_json['left'])
                right = float(filter_json['right'])
                inverted = bool(filter_json.get('inverted', "False")) == True
            except KeyError:
                return Response({}, ResponseCode.QUERY_FILTER_MISSING_VALUE, "Missing required range value of range type filter")
            except ValueError:
                return Response({}, ResponseCode.QUERY_FILTER_INVALID_VALUE, "Invalid value(s) of range type filter")
            except: 
                return Response({}, ResponseCode.INTERNAL_ERROR, "An unknown error has occured")

            print(f"{inverted=}")

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
    fields: set[str] = set()
    filters: list[tuple[str, tuple]] = []

    try:
        page = int(query.get('page', '1'))
        page_size = int(query.get('page_size', '50'))
    except Exception as e:
        return Response({}, ResponseCode.QUERY_INVALID_GENERIC, f"Invalid value for page and/or page_size")

    if field := query.get('fields', None):
        for k in field:
            if k not in StudentRecordAll and k != "student_id":
                return Response({}, ResponseCode.QUERY_UNKNOWN_KEY, f"Unknown key {k} in query")

            if k in fields:
                return Response({}, ResponseCode.QUERY_DUPLICATE, f"Key {k} specified twice in query")

            fields.add(k)

    if filter_list := query.get('filters', None):
        for k, v in filter_list.items():
            if k not in StudentRecordAll and k != "student_id":
                return Response({}, ResponseCode.QUERY_UNKNOWN_KEY, f'Unknown filter {k} in filters')

            if k in filters:
                return Response({}, ResponseCode.QUERY_DUPLICATE, f"Filter {k} specified twice in filter list")

            if isinstance(clause := _parse_filter(k, v), Response):
                return clause

            filters.append(clause)

    return {'fields': fields, 'filters': filters, 'page_num': page, 'page_size': page_size}