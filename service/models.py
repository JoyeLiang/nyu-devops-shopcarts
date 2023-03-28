"""
Models for Account

All of the models are stored in this module
"""
import logging
from datetime import date
from abc import abstractmethod
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    Shopcart.init_db(app)

class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""

######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

   #def __init__(self):
        #self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    @abstractmethod
    def create(self) -> None:
        """
        Creates an object to the database
        """

    @abstractmethod
    def update(self) -> None:
        """
        Updates an object to the database
        """
        
    def delete(self):
        """Removes an object from the data store"""
        logger.info("Deleting %s", self.__class__.__name__)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)




######################################################################
#  I T E M M O D E L
######################################################################
class Item(db.Model,PersistentBase):
    """
    Class that represents an Item 
    an item is one line belongs to shopcart  
    """


    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key =  True)
    shopcart_id = db.Column(db.Integer, db.ForeignKey("shopcart.id"))
    name = db.Column(db.String(64)) # only for better test,a redundant column
    product_id =db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable = False)
    
    def __repr__(self):
        return f"<Item shopcart=[{self.shopcart_id}] product=[{self.product_id}]>"

    def create(self):
        """Create an item to the database"""
        self.id = None
        logger.info("Creating item for shopcart %s, product %s", self.shopcart_id, self.product_id)
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        """Update an item to the database"""
        logger.info("Updating item for shopcart %s, product %s", self.shopcart_id, self.product_id)
        db.session.commit()
    
    def serialize(self):
        """Converts an Product into a dictionary"""
        item = {
            "id":self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name,
            "product_id":self.product_id,
            "count":self.count
        }
        return item

    def deserialize(self, data):
        """
        Populates an Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data['id']
            self.name = data["name"]
            self.shopcart_id = data["shopcart_id"]
            self.product_id = data["product_id"]
            self.count = data["count"]
        except KeyError as error:
            raise DataValidationError("Invalid Account: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self
    
    @classmethod
    def find_by_shopcart_and_product(cls, shopcart, product):
        """Return item with given shopcart id and product id"""
        logger.info("Processing item id query for %s and %s ...", shopcart, product)
        return cls.query.filter(cls.shopcart_id == shopcart, cls.product_id == product)

    @classmethod
    def find_by_shopcart(cls, shopcart):
        """Return items with given shopcart id"""
        logger.info("Processing item id query for shopcart %s ...", shopcart)
        return cls.query.filter(cls.shopcart_id == shopcart)
    


######################################################################
#  S H O P C A R T  M O D E L
######################################################################
class Shopcart(db.Model,PersistentBase):
    """
    Class that represents an Shopcart
    """
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    items = db.relationship("Item", backref = "shopcart", passive_deletes=True)
    def __repr__(self):
        return f"<Shopcart {self.id} customer=[{self.customer_id}]>"

    def create(self):
        """Create an shopcart to the database"""
        self.id = None
        logger.info("Creating shopcart %s", self.id)
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        """Update an shopcart to the database"""
        logger.info("Updating shopcart %s",self.id)
        db.session.commit()

    def serialize(self):
        """Converts an Shopcart into a dictionary"""
        shopcart = {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": []
        }
        for item in self.items:
            shopcart["items"].append(item.serialize())
        return shopcart

    def deserialize(self, data):
        """
        Populates an Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.customer_id = data["customer_id"]
            items_list = data.get("items")
            for json_item in items_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid Account: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self
    
    @classmethod
    def find_by_customer_id(cls, c_id):
        """Return shopcart with given customer id"""
        logger.info("Processing shopcart id query for customer %s ...", c_id)
        return cls.query.filter(cls.customer_id == c_id)


   