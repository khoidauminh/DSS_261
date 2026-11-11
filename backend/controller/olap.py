from ..service import olap
from ..util.response import Response, ResponseCode

def olap_generic(body: dict) -> Response:
    filters = body.get('filters', {})
    stats_only = body.get('stats_only', False)

    return olap.olap_generic(filters, stats_only)
