#!/usr/bin/env python3
"""
The Baconator Bot - Authentic Discord Bot
Talks exactly like Jackson (The Baconator) from your Discord conversations.
"""

import discord
import asyncio
import os
import logging
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaconatorBot(discord.Client):
    """Discord bot that talks exactly like The Baconator."""
    
    def __init__(self):
        # Minimal intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        # The Baconator's EXACT phrases from your conversations
        self.baconator_phrases = {
            'why_responses': ["but why would you", "i wouldnt"],
            'how_responses': ["bruh how", "idk"],
            'server_responses': ["gotta wait for boiler", "i tried like 3 hrs ago", "also the server is a bit down rn"],
            'short_responses': ["yuh", "bruh", "probably", "ohhhh", "lolo"],
            'gaming_responses': ["im looking for calorite", "THE CONTRAPTION", "where can i buy?"],
            'tyler_responses': ["pov tyler", "make it less", "needs to be negative"],
            'corrections': ["get it right", "i replied to the mending not the wooden tools"],
            'reactions': ["^^^MENDING", "good call making tyler eat something"],
            'casual': ["sup", "idk", "nah", "maybe"]
        }
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'🥓 The Baconator (Gerald) is online as {self.user}!')
        logger.info(f'📊 Connected to {len(self.guilds)} servers')
        
        # Set bot activity
        activity = discord.Activity(type=discord.ActivityType.playing, name="Minecraft")
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        """Handle incoming messages like The Baconator would."""
        # Don't respond to self or other bots
        if message.author == self.user or message.author.bot:
            return
        
        content_lower = message.content.lower()
        original_content = message.content
        
        # Determine if The Baconator would respond
        should_respond = (
            self.user in message.mentions or  # Direct mention
            'gerald' in content_lower or
            'baconator' in content_lower or
            'jackson' in content_lower or
            # Gaming topics (his main interest)
            any(word in content_lower for word in ['server', 'minecraft', 'game', 'boiler', 'contraption', 'mending']) or
            # Questions to the group
            (original_content.strip().endswith('?') and len(original_content) > 5) or
            # Random chance like he sometimes jumps into conversations
            random.random() < 0.15
        )
        
        if should_respond:
            response = self.get_baconator_response(content_lower, original_content)
            
            if response:
                try:
                    await message.channel.send(response)
                    logger.info(f"Baconator responded: {response}")
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")
    
    def get_baconator_response(self, content_lower: str, original_content: str) -> str:
        """Get a response exactly like The Baconator would give."""
        
        # Specific triggers based on actual conversation patterns
        if 'why' in content_lower and ('would' in content_lower or 'do' in content_lower):
            return random.choice(self.baconator_phrases['why_responses'])
        
        elif 'how' in content_lower:
            return random.choice(self.baconator_phrases['how_responses'])
        
        elif any(word in content_lower for word in ['server', 'down', 'broken', 'not working', 'boiler']):
            return random.choice(self.baconator_phrases['server_responses'])
        
        elif any(word in content_lower for word in ['tyler', 'toldo']):
            return random.choice(self.baconator_phrases['tyler_responses'])
        
        elif any(word in content_lower for word in ['minecraft', 'game', 'playing', 'contraption', 'calorite']):
            return random.choice(self.baconator_phrases['gaming_responses'])
        
        elif 'mending' in content_lower:
            return random.choice(self.baconator_phrases['corrections'])
        
        elif any(word in content_lower for word in ['hello', 'hi', 'hey', 'sup', 'what\'s up']):
            return random.choice(self.baconator_phrases['short_responses'])
        
        elif original_content.strip().endswith('?'):
            return random.choice(["probably", "idk", "ohhhh", "bruh how"])
        
        elif any(word in content_lower for word in ['lol', 'lmao', 'funny', 'haha']):
            return "lolo"
        
        elif len(original_content.strip()) < 10:  # Short messages get short responses
            return random.choice(["yuh", "bruh", "probably"])
        
        else:
            # Default Baconator responses
            all_responses = []
            for responses in self.baconator_phrases.values():
                all_responses.extend(responses)
            return random.choice(all_responses)

def main():
    """Run The Baconator bot."""
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ No Discord token found!")
        logger.info("Please set DISCORD_TOKEN in your .env file")
        return
    
    # Create and run bot
    bot = BaconatorBot()
    
    try:
        logger.info("🚀 Starting The Baconator Bot...")
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token!")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()
