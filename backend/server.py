from flask import Flask, request

APP = Flask(__name__)

@APP.route("/")
def index():
    return "<p>Index</p>"

@APP.route("/hello", methods=['POST'])
def hello():
    try:
        name = request.get_json()['name']
        return f"<p>Hello {name}</p>"
    
    except:
        return "Name not found", 400

from .controller import fact_academic_record as controller_far

@APP.route('/records', methods=['POST'])
def records_insert():
    return controller_far.import_new_records(request.get_json()).into_response()

@APP.route('/records/query', methods=['POST'])
def records_get():
    return controller_far.query_for_records(request.get_json()).into_response()

from .repository import fact_academic_record as repo_far

@APP.route('/ping', methods=['GET'])
def ping():
    return repo_far.ping().into_response()

# Run the development server
if __name__ == '__main__':
    APP.run(debug=True)