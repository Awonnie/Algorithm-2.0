from flask import Blueprint, jsonify

status = Blueprint('status', __name__)

@status.route('/status', methods=['GET'])
def connection_check():
    """
    FLASK ROUTE: CONNECTION CHECK
    This is a health check endpoint to check if the server is running

    Return: a json object with a key "result" and value s"ok"
    """
    return jsonify({"result": "ok"})