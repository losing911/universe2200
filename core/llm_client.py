"""
LLM Client for Universe 2200

Abstracts interactions with Large Language Models (OpenAI, OpenRouter, Anthropic).
Handles configuration, retries, and structured output parsing.
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

try:
    from openai import OpenAI, APIError, RateLimitError
except ImportError:
    OpenAI = None
    APIError = None
    RateLimitError = None

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM Client."""
    provider: str = "openai"  # openai, openrouter, anthropic
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-4o-mini"
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.7

class LLMClient:
    """
    Client for interacting with LLM APIs.
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        
        if OpenAI is None:
            logger.error("OpenAI package not installed. Please run 'pip install openai'")
            return
            
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the appropriate API client based on provider."""
        api_key = self.config.api_key or os.getenv("LLM_API_KEY")
        if not api_key:
            logger.warning("No API key provided for LLM Client. AI features will be disabled.")
            return

        if self.config.provider == "anthropic":
            # For Anthropic, we would use the anthropic package, but for now 
            # we can use OpenAI client if using OpenRouter to access Claude,
            # or implement native Anthropic client later.
            # Assuming OpenRouter for generic access or native OpenAI.
            pass
            
        # Default to OpenAI client (compatible with OpenRouter)
        base_url = self.config.base_url
        if self.config.provider == "openrouter" and not base_url:
            base_url = "https://openrouter.ai/api/v1"
            
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self.config.timeout
            )
            logger.info(f"LLM Client initialized with provider: {self.config.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")

    def generate_json(self, 
                      system_prompt: str, 
                      user_prompt: str, 
                      temperature: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Generate structured JSON output from LLM.
        
        Args:
            system_prompt: Context and instruction for the AI
            user_prompt: Specific task input
            temperature: Override default temperature
            
        Returns:
            Parsed JSON dictionary or None if failure
        """
        if not self.client:
            logger.warning("LLM Client not initialized. Skipping generation.")
            return None

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        retries = 0
        while retries < self.config.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=temperature or self.config.temperature,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                if not content:
                    logger.error("Received empty response from LLM")
                    return None
                    
                # Parse JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {content[:100]}...")
                    return None
                    
            except RateLimitError:
                logger.warning("Rate limit hit. Retrying...")
                retries += 1
                time.sleep(2 ** retries)  # Exponential backoff
            except APIError as e:
                logger.error(f"API Error: {e}")
                retries += 1
            except Exception as e:
                logger.error(f"Unexpected error during generation: {e}")
                return None
                
        logger.error("Max retries exceeded for LLM generation")
        return None

    def generate_text(self, 
                      system_prompt: str, 
                      user_prompt: str,
                      temperature: Optional[float] = None) -> Optional[str]:
        """Generate unstructured text output."""
        if not self.client:
            return None

        # Similar implementation but returning string
        # For brevity, reusing the core logic concept
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature or self.config.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Text Generation failed: {e}")
            return None
