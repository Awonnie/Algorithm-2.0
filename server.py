from flask import Flask
from flask_cors import CORS

from flask_routes import status, image, path

# Initialisation
app = Flask(__name__)
CORS(app)

# Flask Routes
app.register_blueprint(status, url_prefix="/")
app.register_blueprint(image, url_prefix="/")
app.register_blueprint(path, url_prefix="/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
