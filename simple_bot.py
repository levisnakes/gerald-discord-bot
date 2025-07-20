#!/usr/bin/env python3
"""
Simple Discord Friend AI Bot - Minimal Version
Test version that works without privileged intents.
"""

import discord
import asyncio
import os
import logging
from dotenv import load_dotenv
import json
import random

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFriendBot(discord.Client):
    """Simple Discord bot for testing."""
    
    def __init__(self):
        # Minimal intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        # Load simple model if available
        self.responses = self.load_responses()
    
    def load_responses(self):
        """Load response patterns based on The Baconator's actual typing style."""
        # The Baconator's real responses - all lowercase, casual, gaming-focused
        baconator_responses = [
            # His actual short responses
            "yuh", "bruh", "probably", "ohhhh", "lolo", "i wouldnt", 
            "but why would you", "get it right", "bruh how", "where can i buy?",
            
            # Gaming related (his main interest)
            "gotta wait for boiler", "i tried like 3 hrs ago", "im looking for calorite",
            "also the server is a bit down rn", "make it less", "needs to be negative",
            "im not doing anything", "THE CONTRAPTION", "^^^MENDING",
            
            # His reactions and comments
            "pov tyler", "good call making tyler eat something", "i replied to the mending not the wooden tools",
            
            # Very casual/short
            "sup", "idk", "nah", "yeah", "maybe", "true", "facts"
        ]
        
        logger.info(f"Loaded {len(baconator_responses)} authentic Baconator responses")
        return baconator_responses
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'✅ Bot connected as {self.user}!')
        logger.info(f'📊 Connected to {len(self.guilds)} servers')
        
        # Set bot activity
        activity = discord.Activity(type=discord.ActivityType.listening, name="friend messages")
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Don't respond to self or other bots
        if message.author == self.user or message.author.bot:
            return
        
        # Respond like The Baconator - more selective but contextual
        content_lower = message.content.lower()
        triggers = ['gerald', 'baconator', 'jackson']
        
        # The Baconator responds when:
        # 1. Directly mentioned
        # 2. Gaming/server topics (his main interest)
        # 3. Questions directed at the group
        # 4. Sometimes randomly like he does
        should_respond = (
            self.user in message.mentions or  # Direct mention
            any(trigger in content_lower for trigger in triggers) or  # Name mentioned
            any(word in content_lower for word in ['server', 'minecraft', 'game', 'boiler', 'contraption']) or  # Gaming topics
            (message.content.startswith(('why', 'how', 'what', 'where')) and '?' in message.content) or  # Questions
            random.random() < 0.12  # 12% chance to respond randomly (Baconator sometimes jumps in)
        )
        
        if should_respond:
            # Respond like The Baconator based on what was actually said
            content_lower = message.content.lower()
            original_content = message.content
            
            # The Baconator's actual response patterns
            if any(word in content_lower for word in ['why', 'why would', 'why do']):
                responses = ["but why would you", "i wouldnt", "bruh why"]
            elif any(word in content_lower for word in ['how', 'how do', 'how are']):
                responses = ["bruh how", "idk how", "probably"]
            elif any(word in content_lower for word in ['server', 'down', 'broken', 'not working']):
                responses = ["gotta wait for boiler", "i tried like 3 hrs ago", "also the server is a bit down rn"]
            elif any(word in content_lower for word in ['tyler', 'toldo']):
                responses = ["pov tyler", "make it less", "needs to be negative"]
            elif any(word in content_lower for word in ['minecraft', 'game', 'playing', 'play']):
                responses = ["im looking for calorite", "THE CONTRAPTION", "where can i buy?"]
            elif any(word in content_lower for word in ['hello', 'hi', 'hey', 'what\'s up', 'whats up']):
                responses = ["yuh", "sup", "bruh"]
            elif any(word in content_lower for word in ['good', 'nice', 'cool', 'awesome']):
                responses = ["yuh", "probably", "i guess"]
            elif any(word in content_lower for word in ['agree', 'right', 'exactly', 'true']):
                responses = ["yuh", "exactly", "get it right"]
            elif '?' in original_content:
                responses = ["probably", "idk", "ohhhh", "where can i buy?", "bruh how"]
            elif any(word in content_lower for word in ['lol', 'lmao', 'funny', 'haha']):
                responses = ["lolo", "bruh", "pov tyler"]
            elif len(original_content) < 10:  # Short messages
                responses = ["yuh", "bruh", "probably", "ohhhh"]
            else:
                # Contextual responses based on message length and content
                if 'mending' in content_lower:
                    responses = ["^^^MENDING", "get it right"]
                elif any(word in content_lower for word in ['contraption', 'build', 'making']):
                    responses = ["THE CONTRAPTION", "bruh how"]
                else:
                    responses = ["yuh", "bruh", "probably", "i wouldnt", "but why would you"]
            
            response = random.choice(responses)
            
            # The Baconator's typing style - no capital letters, casual
            response = response.lower() if response not in ["THE CONTRAPTION", "^^^MENDING"] else response
            
            # Sometimes add his casual additions
            if random.random() < 0.2:  # 20% chance
                if random.random() < 0.5:
                    response += " bruh"
                else:
                    response += " lol"
            
            try:
                await message.channel.send(response)
                logger.info(f"Responded to {message.author}: {response}")
            except Exception as e:
                logger.error(f"Failed to send message: {e}")

def main():
    """Run the bot."""
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ No Discord token found!")
        logger.info("Please set DISCORD_TOKEN in your .env file")
        return
    
    # Create and run bot
    bot = SimpleFriendBot()
    
    try:
        logger.info("🚀 Starting Friend AI Bot...")
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token!")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()
