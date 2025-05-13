import unittest
from app import app

class TestChampomixAPIUnit(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_create_user(self):
        response = self.client.post("/users/", json={
            "pseudo": "testuser",
            "password": "securepass"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_get_users(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_create_champomi(self):
        response = self.client.post("/champomi/", json={
            "name": "Test Champomi",
            "price": 3.50,
            "description": "Produit de test"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_get_champomi(self):
        response = self.client.get("/champomi/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

if __name__ == '__main__':
    unittest.main()
