import requests
from django.conf import settings  # Assume API credentials are stored in settings.py

class APIClient:
    BASE_URL = "https://api.copilot.com/v1/clients"
    
    @staticmethod
    def get_headers():
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.API_KEY}"  # Assuming you store your API key in settings
        }
    
    @classmethod
    def list_clients(cls, limit=100):
        url = f"{cls.BASE_URL}?limit={limit}"
        response = requests.get(url, headers=cls.get_headers())
        return response.json()
    
    @classmethod
    def retrieve_client(cls, client_id):
        url = f"{cls.BASE_URL}/{client_id}"
        response = requests.get(url, headers=cls.get_headers())
        return response.json()

    @classmethod
    def create_client(cls, data):
        response = requests.post(cls.BASE_URL, headers=cls.get_headers(), json=data)
        return response.json()

    @classmethod
    def delete_client(cls, client_id):
        url = f"{cls.BASE_URL}/{client_id}"
        response = requests.delete(url, headers=cls.get_headers())
        return response.json()
