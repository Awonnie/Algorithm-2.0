from flask import Blueprint, jsonify

from model import *

stitch = Blueprint('stitch', __name__)

@stitch.route('/stitch', methods=['GET'])
def stitch_images():
    """
    FLASK ROUTE: STITCH IMAGES
    This route enables us to stitch the results of all our captured images together

    Return: a json object with a key "result" and value s"ok"
    """

    # Call Stitiching method here
    img = stitch_image()
    img.show()
    img2 = stitch_image_own()
    img2.show()
    return jsonify({"result": "ok"})


    # Return an okay response
    return jsonify({"result": "ok"})