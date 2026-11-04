from werkzeug.http import HTTP_STATUS_CODES
from flask import make_response

class Response:
    def __init__(self, status_code: int = 200, data={}):
        self.status_code = status_code
        self.data = data

    def into_response(self):
        return make_response(self.data, self.status_code)
