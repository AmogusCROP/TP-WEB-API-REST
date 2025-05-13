import unittest
import requests
import time

BASE_URL = "http://backend:5000"  # Utiliser 'backend' si exécuté via Docker Compose

def wait_for_backend(timeout=30):
    """Attend que le backend soit disponible, pendant `timeout` secondes max."""
    for _ in range(timeout):
        try:
            response = requests.get(f"{BASE_URL}/users/")
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(1)
    raise Exception("Backend not reachable")

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wait_for_backend()

    def test_get_users(self):
        """Test de l'endpoint GET /users/"""
        response = requests.get(f"{BASE_URL}/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == '__main__':
    unittest.main()
