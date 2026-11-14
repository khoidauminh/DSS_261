from ..service import dss
from ..util.response import Response

def get_model_info(retrain: bool = False) -> Response:
    return dss.get_model_info(retrain=retrain)

def predict_student_risk(body: dict | None) -> Response:
    return dss.predict_student_risk(body or {})

def get_early_warning_list(body: dict | None) -> Response:
    return dss.get_early_warning_list(body or {})
