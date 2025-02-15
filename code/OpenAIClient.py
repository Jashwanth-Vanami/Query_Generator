from aiclient import AIClient
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from functools import lru_cache
from datetime import datetime, timedelta


# -------------------- AI Client Interfaces --------------------
class AIClient(ABC):
    """Abstract base class for AI clients"""
    
    @abstractmethod
    def generate_query(self, prompt: str, max_tokens: int) -> str:
        pass

class OpenAIClient(AIClient):
    """OpenAI API implementation"""
    
    def __init__(self, api_key: str):
        import openai
        openai.api_key = api_key
        
    def generate_query(self, prompt: str, max_tokens: int) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise