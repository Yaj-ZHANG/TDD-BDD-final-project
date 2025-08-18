# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal, InvalidOperation
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetching it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # update the description
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # fetch all and verify
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_invalid_update(self):
        """It should raise error for Invalid Update"""
        product = ProductFactory()
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete a product and make sure it doesn't exist in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # create 5 products and save to database
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # verify if the 5 products was created
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Fins a Product by Name"""
        # create 5 products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # retrive the name of first product and count the occurrences
        name = products[0].name
        count = len([product for product in products if product.name == name])
        # find the product by Name and verify
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availbility(self):
        """It should Find Products by Availability"""
        # create 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # retrive the availability of first product and count the occurrences
        available = products[0].available
        count = len([product for product in products if product.available == available])
        # find the product by Availability and verify
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        # create 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # retrive the category of first product and count the occurrences
        category = products[0].category
        count = len([product for product in products if product.category == category])
        # find the product by Category and verify
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        # create 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # retrive the price of first product and count the occurrences
        price = products[0].price
        count = len([product for product in products if product.price == price])
        # find the product by Price and verify
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_deserialize_bad_available_type(self):
        """It should not deserialize with a bad available type"""
        product = Product()
        data = ProductFactory().serialize()
        data["available"] = "yes"  # not a boolean
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertIn("Invalid type for boolean", str(context.exception))

    def test_deserialize_bad_category(self):
        """It should not deserialize with a bad category"""
        product = Product()
        data = ProductFactory().serialize()
        data["category"] = "NOT_A_CATEGORY"
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertIn("Invalid attribute", str(context.exception))

    def test_deserialize_missing_name(self):
        """It should not deserialize without a name"""
        product = Product()
        data = ProductFactory().serialize()
        del data["name"]
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertIn("missing name", str(context.exception))

    def test_deserialize_not_a_dict(self):
        """It should not deserialize with non-dict data"""
        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize("not a dict")
        self.assertIn("bad or no data", str(context.exception))
    
    def test_find_by_price_invalid_string(self):
        """It should fail when price string is not a number"""
        with self.assertRaises(InvalidOperation):
            Product.find_by_price("not-a-number")

    def test_find_by_price_empty_string(self):
        """It should fail when price string is empty"""
        with self.assertRaises(InvalidOperation):
            Product.find_by_price("")
