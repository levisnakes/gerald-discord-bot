#!/usr/bin/env python3
"""
Smart Baconator AI Bot
Uses actual AI to learn and generate responses like The Baconator.
"""

import discord
import asyncio
import os
import logging
from dotenv import load_dotenv
import random
import json
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

try:
    from utils.model_manager import ModelManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartBaconatorBot(discord.Client):
    """AI-powered Discord bot that learns to talk like The Baconator."""
    
    def __init__(self):
        # Minimal intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        # Initialize AI model if available
        self.ai_model = None
        self.conversation_history = []
        self.baconator_data = self.load_baconator_data()
        
        if AI_AVAILABLE:
            try:
                self.ai_model = ModelManager("microsoft/DialoGPT-small")
                self.ai_model.load_pretrained_model()
                logger.info("AI model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load AI model: {e}")
                self.ai_model = None
        
        # Fallback responses from actual conversations
        self.baconator_phrases = [
            "yuh", "bruh", "probably", "ohhhh", "lolo", "but why would you", 
            "i wouldnt", "bruh how", "gotta wait for boiler", "i tried like 3 hrs ago",
            "im looking for calorite", "where can i buy?", "pov tyler", "get it right",
            "also the server is a bit down rn", "make it less", "needs to be negative"
        ]
    
    def load_baconator_data(self):
        """Load The Baconator's conversation data for context."""
        try:
            with open('data/baconator_messages.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} Baconator messages for AI training")
            return data
        except Exception as e:
            logger.warning(f"Could not load Baconator data: {e}")
            return []
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'🤖 Smart Baconator AI is online as {self.user}!')
        logger.info(f'📊 Connected to {len(self.guilds)} servers')
        logger.info(f'🧠 AI Model: {"Available" if self.ai_model else "Fallback mode"}')
        
        # Set bot activity
        activity = discord.Activity(type=discord.ActivityType.playing, name="with AI")
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        """Handle incoming messages with AI responses."""
        # Don't respond to self or other bots
        if message.author == self.user or message.author.bot:
            return
        
        # Store conversation context
        self.conversation_history.append({
            'author': message.author.display_name,
            'content': message.content,
            'timestamp': message.created_at.isoformat()
        })
        
        # Keep only recent messages for context
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        content_lower = message.content.lower()
        
        # Determine if should respond (more selective than before)
        should_respond = (
            self.user in message.mentions or  # Direct mention
            'gerald' in content_lower or
            'baconator' in content_lower or
            # Gaming topics he's interested in
            any(word in content_lower for word in ['server', 'minecraft', 'boiler', 'contraption']) or
            # Questions that seem directed at the group
            (message.content.strip().endswith('?') and 
             any(word in content_lower for word in ['why', 'how', 'what', 'where', 'when'])) or
            # Random chance to jump in (like real Baconator)
            random.random() < 0.12
        )
        
        if should_respond:
            response = await self.generate_smart_response(message.content, message.author.display_name)
            
            if response:
                try:
                    await message.channel.send(response)
                    logger.info(f"AI Baconator responded: {response}")
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")
    
    async def generate_smart_response(self, user_message: str, user_name: str) -> str:
        """Generate an AI response that sounds like The Baconator."""
        
        # Try AI generation first
        if self.ai_model and self.ai_model.model_loaded:
            try:
                # Create context from conversation history
                recent_context = self.build_conversation_context()
                
                # Create prompt in Baconator's style
                prompt = self.create_baconator_prompt(recent_context, user_message, user_name)
                
                # Generate AI response
                ai_response = self.ai_model.generate_response(prompt, max_length=50)
                
                if ai_response:
                    # Clean and style the response like Baconator
                    cleaned_response = self.clean_ai_response(ai_response)
                    if cleaned_response and len(cleaned_response) > 2:
                        return cleaned_response
                        
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback to contextual pattern matching
        return self.generate_contextual_response(user_message.lower())
    
    def build_conversation_context(self) -> str:
        """Build conversation context for AI prompt."""
        if not self.conversation_history:
            return ""
        
        context_lines = []
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            context_lines.append(f"{msg['author']}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def create_baconator_prompt(self, context: str, user_message: str, user_name: str) -> str:
        """Create a prompt that encourages Baconator-style responses."""
        
        # Include some of his actual messages as examples
        baconator_examples = [
            "The Baconator: but why would you",
            "The Baconator: gotta wait for boiler", 
            "The Baconator: yuh",
            "The Baconator: bruh how",
            "The Baconator: im looking for calorite",
            "The Baconator: probably"
        ]
        
        prompt = f"""Here are some examples of how The Baconator talks:
{chr(10).join(baconator_examples)}

Recent conversation:
{context}
{user_name}: {user_message}
The Baconator:"""
        
        return prompt
    
    def clean_ai_response(self, response: str) -> str:
        """Clean AI response to match Baconator's style."""
        if not response:
            return ""
        
        # Remove common AI artifacts
        response = response.strip()
        response = response.replace("The Baconator:", "").strip()
        response = response.replace("Baconator:", "").strip()
        
        # Split on newlines and take first meaningful line
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if not lines:
            return ""
        
        response = lines[0]
        
        # Make it lowercase like Baconator (except special phrases)
        if response not in ["THE CONTRAPTION", "^^^MENDING"]:
            response = response.lower()
        
        # Remove excessive punctuation
        while response.endswith('...'):
            response = response[:-3].strip()
        
        # Limit length (Baconator keeps it short)
        if len(response) > 100:
            # Find last complete word under 100 chars
            words = response.split()
            short_response = ""
            for word in words:
                if len(short_response + " " + word) <= 100:
                    short_response += " " + word if short_response else word
                else:
                    break
            response = short_response
        
        return response
    
    def generate_contextual_response(self, user_message_lower: str) -> str:
        """Generate contextual response when AI is not available."""
        
        # Pattern-based responses that actually relate to what was said
        if 'why' in user_message_lower and ('would' in user_message_lower or 'do' in user_message_lower):
            return "but why would you"
        elif 'how' in user_message_lower:
            return random.choice(["bruh how", "idk"])
        elif any(word in user_message_lower for word in ['server', 'down', 'broken']):
            return random.choice(["gotta wait for boiler", "i tried like 3 hrs ago"])
        elif any(word in user_message_lower for word in ['tyler', 'toldo']):
            return "pov tyler"
        elif any(word in user_message_lower for word in ['game', 'minecraft', 'playing']):
            return random.choice(["im looking for calorite", "where can i buy?"])
        elif user_message_lower.strip().endswith('?'):
            return random.choice(["probably", "idk", "ohhhh"])
        elif any(word in user_message_lower for word in ['hello', 'hi', 'hey']):
            return "yuh"
        else:
            return random.choice(self.baconator_phrases)

def main():
    """Run the Smart Baconator AI bot."""
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ No Discord token found!")
        logger.info("Please set DISCORD_TOKEN in your .env file")
        return
    
    # Create and run bot
    bot = SmartBaconatorBot()
    
    try:
        logger.info("🚀 Starting Smart Baconator AI Bot...")
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token!")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()
