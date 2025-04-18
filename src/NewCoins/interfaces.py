from abc import ABC, abstractmethod
from typing import Any

class HTTPClient(ABC):
    @abstractmethod
    def get(self, url: str) -> Any:
        pass
