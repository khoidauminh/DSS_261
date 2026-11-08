from werkzeug.http import HTTP_STATUS_CODES
from flask import make_response
from enum import Enum, auto

class ResponseCode(Enum):
    OK                              = (200, auto())
    INSERT_MISSING_REQUIRED_KEYS    = (400, auto())
    INSERT_DUPLICATE                = (400, auto())
    INSERT_INVALID_KEY              = (400, auto())
    INSERT_INVALID_GENERIC          = (400, auto())
    QUERY_UNKNOWN_KEY               = (400, auto())
    QUERY_MISSING_FILTER_TYPE       = (400, auto())
    QUERY_DUPLICATE                 = (400, auto())
    QUERY_FILTER_MISSING_VALUE      = (400, auto())
    QUERY_FILTER_INVALID_VALUE      = (400, auto())
    QUERY_INVALID_GENERIC           = (400, auto())
    INTERNAL_ERROR                  = (500, auto())

class Response:
    def __init__(self, data, response_code: ResponseCode, response_message: str):
        self.response_code = response_code
        self.data = data
        self.response_message = response_message

    def into_response(self):
        return make_response({"data": self.data, "code": self.response_code.name, "message": self.response_message}, self.response_code.value[0])
