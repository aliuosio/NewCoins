from abc import ABC, abstractmethod
from typing import Dict, Any

class TradingClient(ABC):
    @abstractmethod
    def get_balance(self, asset: str) -> float:
        pass

    @abstractmethod
    def place_order(self, action: str, symbol: str, asset: str) -> Dict[str, Any]:
        pass
