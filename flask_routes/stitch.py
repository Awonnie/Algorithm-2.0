from flask import Blueprint, jsonify

from .helper import *

stitch = Blueprint('stitch', __name__)

@stitch.route('/stitch', methods=['GET'])
def stitch_images():
    """
    FLASK ROUTE: STITCH IMAGES
    This route enables us to stitch the results of all our captured images together

    Return: a json object with a key "result" and value s"ok"
    """

    # Call Stitiching method here
    stitched_raw = stitch_raw_imgs()
    stitched_raw.show()
    stitched_annotated = stitch_annotated_imgs()
    stitched_annotated.show()

    # Return okay response
    return jsonify({"result": "ok"})