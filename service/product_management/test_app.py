import unittest
import json
from app import create_app, db
from models import Product, Category, Review

class ProductServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_category(self):
        response = self.client.post('/api/categories', json={'name': 'Shoes'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIsInstance(data, int)

    def test_create_product(self):
        # First create category
        response = self.client.post('/api/categories', json={'name': 'Shoes'})
        category_id = response.get_json()

        product_data = {
            'name': 'Running Shoes',
            'description': 'Comfortable running shoes',
            'price': 99.99,
            'category_id': category_id
        }
        response = self.client.post('/api/products', json=product_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'Running Shoes')
        self.assertEqual(data['category_name'], 'Shoes')

    def test_get_products_with_pagination(self):
        # Create category and products
        response = self.client.post('/api/categories', json={'name': 'Shoes'})
        category_id = response.get_json()

        for i in range(15):
            product_data = {
                'name': f'Shoe {i}',
                'description': 'Test shoe',
                'price': 50 + i,
                'category_id': category_id
            }
            self.client.post('/api/products', json=product_data)

        response = self.client.get('/api/products?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['items']), 10)
        self.assertEqual(data['total'], 15)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['pages'], 2)

    def test_create_review_and_get_product(self):
        # Create category and product
        response = self.client.post('/api/categories', json={'name': 'Shoes'})
        category_id = response.get_json()

        product_data = {
            'name': 'Running Shoes',
            'description': 'Comfortable running shoes',
            'price': 99.99,
            'category_id': category_id
        }
        response = self.client.post('/api/products', json=product_data)
        product_id = response.get_json()['id']

        # Create review
        review_data = {
            'product_id': product_id,
            'user_name': 'John Doe',
            'rating': 5,
            'comment': 'Great shoes!'
        }
        response = self.client.post('/api/reviews', json=review_data)
        self.assertEqual(response.status_code, 201)
        review = response.get_json()
        self.assertEqual(review['user_name'], 'John Doe')

        # Get product with reviews
        response = self.client.get(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)
        product = response.get_json()
        self.assertEqual(len(product['reviews']), 1)
        self.assertEqual(product['reviews'][0]['comment'], 'Great shoes!')

if __name__ == '__main__':
    unittest.main()
