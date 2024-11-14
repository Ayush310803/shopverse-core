from fastapi.testclient import TestClient
from main import app
from mongoengine import connect, disconnect
import unittest
from urllib.parse import quote_plus
from app.config import settings
from jose import jwt
from app.auth import create_access_token

client = TestClient(app)

class TestReadUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        username = quote_plus(settings.USERNAME)
        password = quote_plus(settings.PASSWORD)
        connection_string = f"mongodb+srv://{username}:{password}@cluster0.top9b.mongodb.net/?retryWrites=true&w=majority"
        connect(db='test_db', host=connection_string)

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_read_user_valid(self):
        username = "ayush"
        response = client.get(f"/api/v1/get_user/{username}")
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "username": "ayush",
            "email": "ayushsrivastava310803@gmail.com",  
            "role": "admin",
            "phone_no": "+91 8429543263"
        }
        self.assertEqual(response.json(), expected_response)

    def test_read_user_not_found(self):
        username = "nonexistentuser"
        response = client.get(f"/api/v1/get_user/{username}")
        self.assertEqual(response.status_code, 404)
        expected_response = {"detail": "User not found"}
        self.assertEqual(response.json(), expected_response)


    def setUp(self):

        self.valid_user = {
            "username": "ayush",
            "password": "310803"
        }
        self.invalid_user = {
            "username": "ayush",
            "password": "123"
        }

    def test_login_valid_credentials(self):
        response = client.post(
            "/api/v1/auth/User_login",
            data={"username": self.valid_user["username"], "password": self.valid_user["password"]}
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("access_token", json_response)
        self.assertEqual(json_response["token_type"], "bearer")

    def test_login_invalid_credentials(self):
        response = client.post(
            "/api/v1/auth/User_login",
            data={"username": self.invalid_user["username"], "password": self.invalid_user["password"]}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid credentials"})

    def test_access_current_user_with_valid_token(self):
        login_response = client.post(
            "/api/v1/auth/User_login",
            data={"username": self.valid_user["username"], "password": self.valid_user["password"]}
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/get_current_user/",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], self.valid_user["username"])

    def test_access_current_user_with_invalid_token(self):
        invalid_token = "invalid_token"
        response = client.get(
            "/api/v1/get_current_user/",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid token"})


