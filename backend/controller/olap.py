from ..service import olap
from ..util.response import Response

def olap_generic(body: dict | None) -> Response:
    body = body or {}
    filters = body.get('filters', {})
    stats_only = body.get('stats_only', False)
    group_by = body.get('group_by', None)

    return olap.olap_generic(filters, stats_only, group_by=group_by)

def olap_cube(body: dict | None) -> Response:
    body = body or {}
    filters = body.get('filters', {})
    group_by = body.get('group_by', [])
    include_records = body.get('include_records', False)

    return olap.olap_cube(filters=filters, group_by=group_by, include_records=include_records)

def get_metadata() -> Response:
    return olap.get_metadata()
