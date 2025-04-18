import requests
from typing import Any
from .interfaces import HTTPClient

class RequestsHTTPClient(HTTPClient):
    def get(self, url: str) -> Any:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
