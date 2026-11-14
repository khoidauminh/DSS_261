import os
from flask import Flask, request, send_from_directory

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
APP = Flask(__name__, static_folder=FRONTEND_DIR)
APP.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

@APP.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@APP.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html", max_age=0)

@APP.route("/app.js")
def frontend_js():
    return send_from_directory(FRONTEND_DIR, "app.js", max_age=0)

@APP.route("/hello", methods=['POST'])
def hello():
    try:
        name = request.get_json()['name']
        return f"<p>Hello {name}</p>"
    
    except:
        return "Name not found", 400

from .controller import fact_academic_record as controller_far, olap, dss

@APP.route('/records', methods=['POST'])
@APP.route('/records/', methods=['POST'])
def records_insert():
    return controller_far.import_new_records(request.get_json(silent=True) or []).into_response()

@APP.route('/records/query', methods=['POST'])
def records_get():
    return controller_far.query_for_records(request.get_json(silent=True) or {}).into_response()

@APP.route('/records/olap', methods=['POST'])
def olap_on_course():
    return olap.olap_generic(request.get_json(silent=True) or {}).into_response()

@APP.route('/records/olap/cube', methods=['POST'])
def olap_cube_route():
    return olap.olap_cube(request.get_json(silent=True) or {}).into_response()

@APP.route('/records/metadata', methods=['GET'])
def records_metadata():
    return olap.get_metadata().into_response()

@APP.route('/dss/model-info', methods=['GET'])
def dss_model_info():
    retrain = request.args.get('retrain', 'false').lower() == 'true'
    return dss.get_model_info(retrain=retrain).into_response()

@APP.route('/dss/retrain', methods=['POST'])
def dss_retrain():
    return dss.get_model_info(retrain=True).into_response()

@APP.route('/dss/predict', methods=['POST'])
def dss_predict():
    return dss.predict_student_risk(request.get_json(silent=True) or {}).into_response()

@APP.route('/dss/early-warning', methods=['POST', 'GET'])
def dss_early_warning():
    body = request.get_json(silent=True) if request.method == 'POST' else dict(request.args)
    return dss.get_early_warning_list(body or {}).into_response()

from .repository import fact_academic_record as repo_far

@APP.route('/ping', methods=['GET'])
def ping():
    return repo_far.ping().into_response()

# Run the development server
if __name__ == '__main__':
    APP.run(debug=True)