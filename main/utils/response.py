from flask import jsonify

def success(data=None, message="OK", status=200):
    body = {"status":"ok","message":message}
    if data is not None: body["data"] = data
    return jsonify(body), status

def success_list(items, count=None, message="OK", status=200):
    return jsonify({"status":"ok","message":message,"count":count if count is not None else len(items),"data":items}), status

def error(message, error_code="ERROR", details=None, status=400):
    body = {"status":"error","error_code":error_code,"message":message}
    if details: body["details"] = details
    return jsonify(body), status

def server_error(message="An unexpected error occurred.", details=None):
    return error(message, error_code="INTERNAL_ERROR", details=details, status=500)