from ..service import olap
from ..util.response import Response, ResponseCode

def olap_on_course(course_ids_str: str) -> Response:
    splitted = course_ids_str.split(',')

    try:
        course_ids = [
            int(x) for x in splitted
        ]

        print(course_ids)
    except ValueError as e:
        return Response({}, ResponseCode.QUERY_INVALID_GENERIC, f"Failed to parse query parameter: {e}")

    return olap.olap_on_course(course_ids)