from flask import Flask, jsonify, request
from flask_cors import CORS

from .status import status
from .path import path
from .image import image

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Flask Routes
    app.register_blueprint(status, url_prefix="/")
    app.register_blueprint(image, url_prefix="/")
    app.register_blueprint(path, url_prefix="/")

    return app