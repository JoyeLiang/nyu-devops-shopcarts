"""
My Service

Paths:
------
GET /shopcarts - Return a list of all shopcarts
GET /shopcarts/{shopcart_id} - Return the shopcart with a given id
GET /shopcarts/{shopcart_id}/items - Return all items of a shopcart
GET /shopcarts/{shopcart_id}/items/{item_id} - Return a item of a shopcart
POST /shopcarts - create a new shopcart in the database
POST /shopcarts/{shopcart_id}/items - create a new item of a shopcart in the database
DELETE /shopcarts/{shopcart_id} - Delete the shopcart with a given id
DELETE /shopcarts/{shopcart_id}/items/{item_id} - Delete a item of a shopcart
PUT /shopcarts/{shopcart_id} - Update the shopcart with a given id
PUT /shopcarts/{shopcart_id}/items/{item_id} - Update a item of a shopcart
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item 
import logging

# Import Flask application
from . import app


logger = logging.getLogger("flask.app")
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

# ---------------------------------------------------------------------
#               S H O P C A R T   M E T H O D S
# ---------------------------------------------------------------------

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

######################################################################
#  LIST A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>",methods = ['GET'])
def get_shopcarts(shopcart_id):
    """Returns a shopcart by id"""
    app.logger.info("Request for a shopcart with id %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)

    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found")
    
    logger.info("Returning shopcart: %s", shopcart_id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK

######################################################################
#  CREATE A SHOPCART
######################################################################
@app.route("/shopcarts", methods = ["POST"])
def create_shopcart():
    """ Creates a shopcart
    This endpoint will create a shopcart based the data in the body that is posted
    """
    logger.info("Request to create a shopcart")
    check_content_type("application/json")

    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)

    logger.info("Shopcart with ID [%s] created.", shopcart.id)
    logger.info("Location: %s", location_url)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  UPDATE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods = ["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a shopcart
    This endpoint will update a shopcart based the body that is posted
    """

    app.logger.info("Request to update shopcart with id %s", shopcart_id)
    check_content_type("application/json")

    #see if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found")
    
    #update from the json in the body of the request
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

@app.route("/shopcarts/<int:shopcart_id>", methods = ["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a shopcart
    This endpoint will delete a shopcart based the id specified in path
    """
    app.logger.info("Request to delete shopcart with id: %d", shopcart_id)

    # Retrieve the account to delete and delete it if it exists
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        shopcart.delete()
    
    return make_response("", status.HTTP_204_NO_CONTENT)

# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------

######################################################################
#  LIST ALL ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items",methods = ['GET'])
def list_all_items(shopcart_id):
    """Returns all of the items of a shopcart"""
    app.logger.info("Request for item list of shopcart: %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    items = shopcart.items

    results = [s.serialize() for s in items]
    app.logger.info("Return %d items", len(items))
    return jsonify(results), status.HTTP_200_OK

######################################################################
#  LIST A ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>",methods = ['GET'])
def get_items(shopcart_id, item_id):
    """Returns a item by id"""
    logger.info("Request for a item belong to shopchart %s with id %s", shopcart_id, item_id)
    item = Item.find(item_id)

    if not item:
        logger.info("Item with id %s was not found", item_id)
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found")
    if not item.shopcart_id or item.shopcart_id!=shopcart_id:
        logger.info("Item with id %s was not belong to shopcart %s: shopcart %s", item_id,shopcart_id,item.shopcart_id)
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not belong to shopcart '{shopcart_id}'")
    
    logger.info("Returning item: %s", item_id)
    return jsonify(item.serialize()), status.HTTP_200_OK

######################################################################
#  CREATE A ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods = ["POST"])
def create_item(shopcart_id):
    """ 
    Creates a item
    This endpoint will create a item based the data in the body that is posted
    """
    logger.info("Request to create a item belong to shopcart %s", shopcart_id)
    check_content_type("application/json")

    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND,f"Shopcart with id '{shopcart_id}' could not be found.")

    item_json = request.get_json()
    logger.info(item_json)
    item = None
    old_item = Item.find_by_shopcart_and_product(shopcart_id, item_json["product_id"])
    if old_item:
        logger.info("Item [%s] existed: product id %s, count %s.", old_item.id, old_item.product_id, old_item.count)
        old_item.count = old_item.count+item_json["count"]
        old_item.update()
        item = old_item
    else:
        item = Item()
        new_item = item.deserialize(request.get_json())
        new_item.create()
        logger.info("Item [%s] created.", new_item.id)
        item = new_item
    message = item.serialize()
    location_url = url_for("get_items", shopcart_id = shopcart_id, item_id=item.id, _external=True)

    logger.info("Location %s", location_url)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  UPDATE A ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods = ["PUT"])
def update_items(shopcart_id, item_id):
    """
    Update a item
    This endpoint will update a item based the body that is posted
    """

    logger.info("Request to update item with id %s", item_id)
    check_content_type("application/json")

    #see if the shopcart exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found")
    if not item.shopcart_id or item.shopcart_id != shopcart_id:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'")
    
    new_item = request.get_json()
    # see if the request is reliable
    if new_item["count"] <= 0:
        abort(status.HTTP_400_BAD_REQUEST, f"Item '{item_id}' count should larger than 0")
    if new_item["price"] < 0.0:
        abort(status.HTTP_400_BAD_REQUEST, f"Item '{item_id}' price should larger than 0")
    
    #update from the json in the body of the request
    item.deserialize(new_item)
    item.id = item_id
    item.update()

    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods = ["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete a item
    This endpoint will delete a item based the id specified in path
    """
    app.logger.info("Request to delete item with id: %d", item_id)

    # Retrieve the account to delete and delete it if it exists
    item = Item.find(item_id)
    if item and item.shopcart_id == shopcart_id:
        item.delete()
    
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )