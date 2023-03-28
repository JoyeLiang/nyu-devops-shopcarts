"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
from service.models import Shopcart,Item, DataValidationError, db
from service import app
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcartModel(unittest.TestCase):
    """ Test Cases for Shopcart Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Item).delete()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """It should create a shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        shopcart = Shopcart(customer_id = fake_shopcart.customer_id)
        
        self.assertIsNotNone(shopcart)
        #self.assertEqual(shopcart.id, fake_shopcart.id)
        self.assertEqual(shopcart.customer_id, fake_shopcart.customer_id)

    def test_add_a_shopcart(self):
        """"It should create a shopcart and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts,[])
        shopcart = ShopcartFactory()
        shopcart.create()
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
    
    def test_read_shopcart(self):
        """It should read a shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()

        found_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.customer_id, shopcart.customer_id)
        self.assertEqual(found_shopcart.items, [])
    
    def test_update_shopcart(self):
        """It should update a shopcart"""
        shopcart = ShopcartFactory(customer_id = 111)
        shopcart.create()

        self.assertIsNotNone(shopcart.id)
        self.assertEqual(shopcart.customer_id, 111)

        shopcart = Shopcart.find(shopcart.id)
        shopcart.customer_id = 123
        shopcart.update()

        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(shopcart.customer_id, 123)
    
    def test_delete_shopcart(self):
        """It should delete a shopcart"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()

        self.assertIsNotNone(shopcart)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        shopcart = shopcarts[0]
        shopcart.delete()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)
    
    def test_list_all_shopcarts(self):
        """It should List all Shopcarts in the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        for s in ShopcartFactory.create_batch(5):
            s.create()
        # Assert that there are not 5 shopcarts in the database
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 5)
    
    def test_find_by_customer_id(self):
        """It should Find an shopcart by customer id"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Fetch it back by customer id
        same_shopcart = Shopcart.find_by_customer_id(shopcart.customer_id)[0]
        self.assertEqual(same_shopcart.id, shopcart.id)
        self.assertEqual(same_shopcart.customer_id, shopcart.customer_id)

    def test_serialize_a_shopcart(self):
        """It should Serialize an shopcart"""
        shopcart = ShopcartFactory()
        item = ItemFactory()
        shopcart.items.append(item)
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart["id"], shopcart.id)
        self.assertEqual(serial_shopcart["customer_id"], shopcart.customer_id)
        self.assertEqual(len(serial_shopcart["items"]), 1)
        items = serial_shopcart["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["shopcart_id"], item.shopcart_id)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["product_id"], item.product_id)
        self.assertEqual(items[0]["count"], item.count)
    
    def test_deserialize_a_shopcart(self):
        """It should Deserialize an shopcart"""
        shopcart = ShopcartFactory()
        shopcart.items.append(ItemFactory())
        shopcart.create()
        serial_shopcart = shopcart.serialize()
        new_shopcart = Shopcart()
        new_shopcart.deserialize(serial_shopcart)
        self.assertEqual(new_shopcart.id, shopcart.id)
        self.assertEqual(new_shopcart.customer_id, shopcart.customer_id)
        
    def test_deserialize_with_key_error(self):
        """It should not Deserialize a shopcart with a KeyError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an shopcart with a TypeError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, [])

######################################################################
#  I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestItemModel(unittest.TestCase):
    """ Test Cases for Item Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Item).delete() 
        db.session.query(Shopcart).delete()# clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_add_an_item(self):
        """It should Create an item with a shopcart and assert that it exists"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        items = Item.all()
        self.assertEqual(items,[])

        item = ItemFactory()
        item.create()
        self.assertIsNotNone(item.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts),1)

        items = Item.all()
        self.assertEqual(len(items), 1)
        new_items = Item.find_by_shopcart(shopcarts[0].id)
        self.assertEqual(new_items[0].id, item.id)
        
    def test_find_by_shopcart_and_product(self):
        """It should read an item"""
        item = ItemFactory()
        item.create()

        found_item = Item.find_by_shopcart_and_product(item.shopcart_id, item.product_id)[0]
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.count, item.count)
        self.assertEqual(found_item.id, item.id)
    
    def test_update_item(self):
        """It should update a item"""
        item = ItemFactory(count = 1)
        item.create()

        self.assertIsNotNone(item.shopcart_id)
        self.assertIsNotNone(item.product_id)
        self.assertEqual(item.count, 1)

        item = Item.find_by_shopcart_and_product(item.shopcart_id, item.product_id)[0]
        item.count = 3
        item.update()

        item = Item.find_by_shopcart_and_product(item.shopcart_id, item.product_id)[0]
        self.assertEqual(item.count, 3)
    
    def test_delete_item(self):
        """It should delete an item"""
        items = Item.all()
        self.assertEqual(items, [])
        item = ItemFactory()
        item.create()

        items = Item.all()
        self.assertEqual(len(items), 1)

        item = items[0]
        item.delete()
        items = Item.all()
        self.assertEqual(len(items), 0)
  
    def test_list_all_items(self):
        """It should List all items in the database"""
        items = Item.all()
        self.assertEqual(items, [])
        for t in ItemFactory.create_batch(5):
            t.create()
        # Assert that there are not 5 shopcarts in the database
        items = Item.all()
        self.assertEqual(len(items), 5)
 
    def test_serialize_an_item(self):
        """It should Serialize an item"""
        item = ItemFactory()
        item.create()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["shopcart_id"], item.shopcart_id)
        self.assertEqual(serial_item["product_id"], item.product_id)
        self.assertEqual(serial_item["count"], item.count)
 
    def test_deserialize_an_item(self):
        """It should Deserialize an item"""
        item = ItemFactory()
        item.create()
        serial_item = item.serialize()
        new_item = Item()
        new_item.deserialize(serial_item)
        self.assertEqual(new_item.id, item.id)
        self.assertEqual(new_item.name, item.name)
        self.assertEqual(new_item.product_id, item.product_id)
        self.assertEqual(new_item.shopcart_id, item.shopcart_id)
        self.assertEqual(new_item.count, item.count)
        
    def test_deserialize_item_key_error(self):
        """It should not Deserialize an address with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_address_type_error(self):
        """It should not Deserialize an address with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])
