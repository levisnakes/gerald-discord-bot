#!/usr/bin/env python3
"""
Simple Ollama Discord Bot Test
A minimal version to test if Ollama AI integration works.
"""

import discord
from discord.ext import commands
import asyncio
import os
import logging
from dotenv import load_dotenv
import json
import random
import aiohttp

# Load environment variables
load_dotenv()

# Simple logging setup for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleOllamaBot(commands.Bot):
    """Simple Discord bot with Ollama AI."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.ollama_url = "http://localhost:11434"
        self.model_name = "gemma2:2b"
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Bot {self.user} is online!')
        logger.info(f'Connected to {len(self.guilds)} servers')
        
        # Test Ollama connection
        if await self.test_ollama():
            logger.info("Ollama AI is ready!")
        else:
            logger.warning("Ollama not available - using simple responses")
    
    async def test_ollama(self):
        """Test if Ollama is working."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    return response.status == 200
        except:
            return False
    
    async def on_message(self, message):
        """Handle messages."""
        if message.author == self.user or message.author.bot:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check if bot should respond
        if (self.user in message.mentions or 
            'baconator' in message.content.lower() or
            random.random() < 0.3):
            
            await self.generate_response(message)
    
    async def generate_response(self, message):
        """Generate and send response."""
        try:
            async with message.channel.typing():
                # Try Ollama AI first
                response = await self.generate_ollama_response(message.content)
                
                if not response:
                    # Fallback to simple responses
                    response = self.generate_simple_response(message.content)
                
                if response:
                    await message.channel.send(response)
                    
        except Exception as e:
            logger.error(f"Error: {e}")
            await message.channel.send("bruh my brain broke")
    
    async def generate_ollama_response(self, prompt):
        """Generate response using Ollama."""
        try:
            full_prompt = f"""You are Baconator, a casual Discord friend. Respond briefly and naturally like:
- "bruh how"
- "probably" 
- "but why would you"
- "idk"
- "ohhhh"

Keep it short and casual. User says: {prompt}

Baconator:"""
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "max_tokens": 50
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result.get("response", "").strip()
                        
                        # Clean up response
                        if ai_response and len(ai_response) < 200:
                            return ai_response
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
        
        return None
    
    def generate_simple_response(self, content):
        """Simple fallback responses."""
        simple_responses = [
            "bruh",
            "probably", 
            "but why would you",
            "idk",
            "ohhhh",
            "yuh",
            "how",
            "what even"
        ]
        return random.choice(simple_responses)

# Commands
@commands.command(name='test')
async def test_ai(ctx):
    """Test AI response."""
    response = await ctx.bot.generate_ollama_response("how are you?")
    if response:
        await ctx.send(f"AI: {response}")
    else:
        await ctx.send("AI not available")

@commands.command(name='status')
async def status(ctx):
    """Show bot status."""
    ollama_working = await ctx.bot.test_ollama()
    status_msg = "🟢 Ollama AI Ready" if ollama_working else "🟡 Simple Mode"
    await ctx.send(f"Status: {status_msg}")

async def main():
    """Run the bot."""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("No Discord token found!")
        return
    
    bot = SimpleOllamaBot()
    bot.add_command(test_ai)
    bot.add_command(status)
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
