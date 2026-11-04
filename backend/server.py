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

from .controller import fact_academic_record

@APP.route('/records', methods=['POST'])
def records():
    return fact_academic_record.import_new_records(request.get_json())


# Run the development server
if __name__ == '__main__':
    APP.run(debug=True)