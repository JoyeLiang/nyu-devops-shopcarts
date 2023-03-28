"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  LIST ALL SHOPCART
######################################################################
@app.route("/shopcarts",methods = ['GET'])
def list_all_shopcarts():
    """Returns all of the shopcarts"""
    app.logger.info("Request for shopcart list")
    shopcarts = []
    shopcarts = Shopcart.all()

    results = [s.serialize() for s in shopcarts]
    app.logger.info("Return %d shopcarts", len(results))
    return jsonify(results), status.HTTP_200_OK


