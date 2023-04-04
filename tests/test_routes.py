"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db,init_db, Shopcart, Item
from service.common import status  # HTTP Status Codes
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/shopcarts"

logger = logging.getLogger("flask.app")
######################################################################
#  S H O P C A R T T E S T   C A S E S
######################################################################
class TestShopcartServer(TestCase):
    """Shopcart REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    
    def _create_shopcarts(self, count):
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test shopcart"
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts
    
    def _create_items(self, count, shopcart):
        """Factory method to create items belong to a shopcart in bulk"""
        items = []
        for _ in range(count):
            test_item = ItemFactory(shopcart_id = shopcart.id,shopcart=shopcart)
            response = self.client.post(f"{BASE_URL}/{shopcart.id}/items", json=test_item.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test item"
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            logger.info("create new item: %s", new_item)
            items.append(test_item)
        return items
    ######################################################################
    #  S H O P C A R T   T E S T   C A S E S   
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

   
    def test_get_shopcart_list(self):
        """It should Get a list of Shopcarts"""
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_shopcart(self):
        """It should Get a Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["customer_id"], test_shopcart.customer_id)

    def test_create_shopcart(self):
        """It should CREATE a Shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["customer_id"], shopcart.customer_id, "Customer_id does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["customer_id"], shopcart.customer_id, "Customer_id does not match")
        
    def test_update_shopcart(self):
        """"It should Update a existing Shopcart"""
        #create a shopcart to update
        test_shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #update the shopcart
        new_shopcart = resp.get_json()
        new_shopcart['customer_id'] = 4
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{BASE_URL}/{new_shopcart_id}", json = new_shopcart)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["customer_id"], 4)

    def test_delete_shopcart(self):
        """It should Delete a shopcart"""
        #get the id of a shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    
######################################################################
#  I T E M   T E S T   C A S E S   
######################################################################
    def test_get_all_items_by_shopcart(self):
        """It should Get a list of items of a shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        self._create_items(5, test_shopcart)
        logger.info(test_shopcart.serialize())
        
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        items = Shopcart.find(test_shopcart.id).items
        logger.info(Shopcart.find(test_shopcart.id).serialize())
        # why this shopcart is different from the previous one??
        self.assertEqual(len(data), len(items))
        for (expected, retrived) in zip(data, items):
            self.assertEqual(retrived.serialize(), expected)

    def test_get_item(self):
        """It should Get a item"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(1, test_shopcart)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["count"], test_item.count)
        self.assertEqual(data["price"], test_item.price)
        self.assertEqual(data["name"], test_item.name)
        self.assertEqual(data["product_id"], test_item.product_id)

    def test_create_item(self):
        """It should CREATE a item"""
        # Create a shopcart and a item belong to it
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory(shopcart_id = shopcart.id, shopcart = shopcart)

        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        logger.info("test location: %s", location)

        # Check the data is correct
        new_item = resp.get_json()
        logging.debug(new_item)
        self.assertEqual(new_item["shopcart_id"], item.shopcart_id, "shopcart_id does not match")
        self.assertEqual(new_item["product_id"], item.product_id, "Product_id does not match")
        self.assertEqual(new_item["name"], item.name, "name does not match")
        self.assertEqual(new_item["count"], item.count, "count does not match")
        self.assertEqual(new_item["price"], item.price, "price does not match")

        
        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        new_item = resp.get_json()
        self.assertEqual(new_item["shopcart_id"], item.shopcart_id, "shopcart_id does not match")
        self.assertEqual(new_item["product_id"], item.product_id, "Product_id does not match")
        self.assertEqual(new_item["name"], item.name, "name does not match")
        self.assertEqual(new_item["count"], item.count, "count does not match")
        self.assertEqual(new_item["price"], item.price, "price does not match")

    def test_update_item(self):
        """"It should Update a existing item"""
        #create a item to update
        test_item = self._create_items(1,self._create_shopcarts(1)[0])[0]
        resp = self.client.get(f"{BASE_URL}/{test_item.shopcart_id}/items/{test_item.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        #update the shopcart
        new_item = resp.get_json()
        logger.info(new_item)
        new_item["price"] = 6
        new_item_id = new_item["id"]
        shopcart_id = new_item["shopcart_id"]
        resp = self.client.put(f"{BASE_URL}/{shopcart_id}/items/{new_item_id}", json = new_item)
        updated_item = resp.get_json()
        logger.info(updated_item)
        self.assertEqual(updated_item["price"], 6)

    def test_delete_item(self):
        """It should Delete a item"""
        #get the id of a item
        shopcart = self._create_shopcarts(1)[0]
        item = self._create_items(1,shopcart)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}/items/{item.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_shopcart_no_data(self):
        """It should not Create a Shopcart with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    '''
    def test_create_shopcart_no_content_type(self):
        """It should not Create a Shopcart with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_wrong_content_type(self):
        """It should not Create a Shopcart with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_shopcart_not_available(self):
        """It should not Get a Shopcart with wrong id"""
        test_shopcart = self._create_shopcarts(1)[0]
        logging.debug(test_shopcart)
        # change available to a string
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id+3}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_shopcart_not_available(self):
        """It should not Get a Shopcart with wrong id"""
        test_shopcart = self._create_shopcarts(1)[0]
        logging.debug(test_shopcart)
        # change available to a string
        response = self.client.put(f"{BASE_URL}/{test_shopcart.id+3}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_item_not_available(self):
        """It should not Get a Item with wrong id or shopcart id"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(1, test_shopcart)[0]
        logging.debug(test_item)
        # change available to a string
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id+3}/items/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    

    def test_create_shopcart_bad_gender(self):
        """It should not Create a Shopcart with bad gender data"""
        pet = PetFactory()
        logging.debug(pet)
        # change gender to a bad string
        test_pet = pet.serialize()
        test_pet["gender"] = "male"    # wrong case
        response = self.client.post(BASE_URL, json=test_pet)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    '''