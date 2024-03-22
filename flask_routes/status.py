from flask import Blueprint, jsonify

from .helper import clear_images, get_extended_path, setup_img_folders

status = Blueprint('status', __name__)

@status.route('/status', methods=['GET'])
def connection_check():
    """
    FLASK ROUTE: CONNECTION CHECK
    This is a health check endpoint to check if the server is running

    Return: a json object with a key "result" and value s"ok"
    """

    setup_img_folders()
    clear_images()
    return jsonify({"result": "ok"})