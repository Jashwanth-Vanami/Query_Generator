from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from functools import lru_cache
from datetime import datetime, timedelta


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



# -------------------- AI Client Interfaces --------------------
class AIClient(ABC):
    """
    Abstract base class for AI clients.

    This class defines the interface for AI clients that are responsible for
    generating queries based on a given prompt. Implementations must provide
    the logic for creating a query with a specified maximum number of tokens.
    """

    @abstractmethod
    def generate_query(self, prompt: str, max_tokens: int) -> str:
        pass