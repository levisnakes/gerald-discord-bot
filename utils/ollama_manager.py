#!/usr/bin/env python3
"""
Ollama Integration for Discord Bot
Handles AI responses using Ollama local models.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OllamaManager:
    """
    Manages communication with Ollama API for AI responses.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "llama3.2"  # Default model
        self.session = None
        self.available = False
        
    async def initialize(self):
        """Initialize the Ollama connection."""
        self.session = aiohttp.ClientSession()
        await self.check_availability()
        
    async def check_availability(self):
        """Check if Ollama is running and available."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    models = await response.json()
                    self.available = True
                    logger.info(f"Ollama is available with {len(models.get('models', []))} models")
                    return True
        except aiohttp.ClientConnectorError:
            logger.info("Ollama service not running on localhost:11434")
            self.available = False
            return False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self.available = False
            return False
        
        return False
    
    async def generate_response(self, prompt: str, context: str = "", personality_prompt: str = "") -> Optional[str]:
        """
        Generate AI response using Ollama.
        
        Args:
            prompt: The user's message
            context: Previous conversation context
            personality_prompt: Instructions for bot personality
        """
        if not self.available:
            await self.check_availability()
            if not self.available:
                return None
        
        try:
            # Build the full prompt with personality and context
            full_prompt = self.build_prompt(prompt, context, personality_prompt)
            
            # Make request to Ollama
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,  # Good balance of creativity and coherence
                    "top_p": 0.9,
                    "max_tokens": 150,  # Allow longer, more natural responses
                    "stop": ["\n\n", "Human:", "User:", "Discord:", "Gerald responds naturally"],
                    "repeat_penalty": 1.1,  # Light penalty to avoid repetition
                    "num_ctx": 2048  # More context for better understanding
                }
            }
            
            async with self.session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get("response", "").strip()
                    
                    # Clean up the response
                    ai_response = self.clean_response(ai_response)
                    
                    if ai_response:
                        logger.info(f"Generated AI response: {ai_response[:50]}...")
                        return ai_response
                        
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            
        return None
    
    def build_prompt(self, user_message: str, context: str = "", personality_prompt: str = "") -> str:
        """Build the complete prompt for the AI model."""
        
        # Add randomization to prevent identical responses
        import random
        
        # Default personality - much more specific instructions
        if not personality_prompt:
            personality_prompt = f"""You are Gerald, a friendly person chatting in Discord. 

CRITICAL INSTRUCTIONS:
- You must respond directly to what the user just said
- Do NOT use phrases like "bruh how", "probably", or other predetermined responses
- Generate a unique, thoughtful response every time
- Understand the context and respond appropriately
- Be conversational and natural, like talking to a friend

For example:
- If someone asks "what even are you forming a sentence?" respond about forming sentences, communication, or ask for clarification
- If someone mentions food, respond about food
- If someone asks a question, give a helpful answer
- If someone makes a statement, acknowledge it and add your thoughts

Random seed: {random.randint(1000, 9999)} (ignore this, it's just for variation)"""

        # Format the conversation context better
        if context:
            context_formatted = f"Previous conversation:\n{context}\n"
        else:
            context_formatted = "This is a new conversation.\n"

        # Create a more specific prompt
        prompt = f"""{personality_prompt}

{context_formatted}
Current message from user: "{user_message}"

Gerald's response (must be unique and relevant to what the user just said):"""
        
        return prompt
    
    def clean_response(self, response: str) -> str:
        """Clean and format the AI response."""
        if not response:
            return ""
        
        # Remove common AI artifacts
        response = response.strip()
        
        # Remove any prefixes that might have leaked through
        prefixes_to_remove = ["Gerald:", "Bot:", "AI:", "Response:", "Gerald responds naturally", "Gerald's response"]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Remove quotes if the entire response is quoted
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1].strip()
        
        # Aggressively block problematic responses
        blocked_responses = [
            "bruh how", "bruh, how", "bruh how?", "bruh, how?",
            "probably", "idk", "ohhhh", "yuh", "nah", "maybe",
            "but why would you", "how", "what even", "fair enough"
        ]
        
        # Check if response is in blocked list
        if response.lower().strip() in [blocked.lower() for blocked in blocked_responses]:
            logger.info(f"Blocked repetitive response: {response}")
            return ""  # Force regeneration or fallback
        
        # Check for very short non-contextual responses
        if len(response.split()) <= 2 and not response.endswith('?'):
            logger.info(f"Blocked short non-contextual response: {response}")
            return ""
        
        # Only accept if response seems contextual and substantial
        if len(response) < 5:
            return ""
        
        # Ensure it's not too long for Discord
        if len(response) > 2000:
            response = response[:1997] + "..."
        
        # Clean up extra whitespace but preserve natural line breaks
        response = " ".join(response.split())
        
        return response
    
    async def set_model(self, model_name: str) -> bool:
        """Set the Ollama model to use."""
        try:
            # Check if model exists
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    models = await response.json()
                    available_models = [m["name"] for m in models.get("models", [])]
                    
                    if model_name in available_models:
                        self.model_name = model_name
                        logger.info(f"Switched to model: {model_name}")
                        return True
                    else:
                        logger.warning(f"Model {model_name} not found. Available: {available_models}")
                        return False
        except Exception as e:
            logger.error(f"Error setting model: {e}")
            return False
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model from Ollama."""
        try:
            payload = {"name": model_name}
            
            async with self.session.post(f"{self.base_url}/api/pull", json=payload) as response:
                if response.status == 200:
                    logger.info(f"Successfully pulled model: {model_name}")
                    return True
                else:
                    logger.error(f"Failed to pull model {model_name}: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
