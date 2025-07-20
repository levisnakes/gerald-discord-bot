#!/usr/bin/env python3
"""
Gerald Bot - Cloud Version (No Ollama dependency)
Optimized for free hosting on Render
"""

import discord
from discord.ext import commands
import asyncio
import os
import logging
import json
import random
from datetime import datetime

# Simple logging for cloud
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeraldBot(commands.Bot):
    """
    Discord bot that learns vocabulary from users and responds using only learned words.
    Cloud-optimized version without Ollama.
    """
    
    def __init__(self):
        # Set up bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Word learning system - only use words that have been said
        self.learned_words = set()
        self.word_frequency = {}
        self.load_learned_words()
        
        # Conversation history for context
        self.conversation_history = {}
        
        # Last response time to prevent spam
        self.last_response_time = {}
        self.cooldown_seconds = 3  # Wait 3 seconds between responses
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load bot configuration."""
        # Default configuration
        self.config = {
            "response_chance": 0.3,  # Respond to 30% of messages
            "max_history": 10,
            "trigger_words": ["hey", "hello", "gerald", "what do you think"],
        }
    
    def load_learned_words(self):
        """Load words that Gerald has learned from conversations."""
        # Start with basic British words
        self.learned_words = {
            'mate', 'innit', 'bloody', 'hell', 'proper', 'mental', 'rubbish',
            'cant', 'be', 'arsed', 'whatever', 'dont', 'care', 'you', 'lot',
            'tyler', 'massive', 'heavy', 'pounds', 'weight', 'fat', 'huge',
            'what', 'how', 'why', 'when', 'where', 'good', 'bad', 'nice'
        }
        self.word_frequency = {}
        print(f"Gerald starts with {len(self.learned_words)} words")
    
    def learn_from_message(self, message_content):
        """Learn new words from a user message."""
        # Clean and split the message
        words = message_content.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
        
        new_words_learned = 0
        for word in words:
            # Filter out very short words and common stop words
            if len(word) > 1 and word not in ['the', 'and', 'or', 'but', 'if', 'then', 'is', 'am', 'are']:
                if word not in self.learned_words:
                    new_words_learned += 1
                
                self.learned_words.add(word)
                self.word_frequency[word] = self.word_frequency.get(word, 0) + 1
        
        if new_words_learned > 0:
            print(f"Gerald learned {new_words_learned} new words from: {words}")
    
    def generate_response(self, context=""):
        """Generate a response using only learned words."""
        # Get most common words (more likely to be used)
        common_words = sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Split words into categories from learned vocabulary only
        connectors = [w for w in ['mate', 'innit', 'bloody', 'proper', 'hell'] if w in self.learned_words]
        tyler_words = [w for w in ['tyler', 'massive', 'heavy', 'pounds', 'weight', 'fat', 'huge', 'big'] if w in self.learned_words]
        reactions = [w for w in ['whatever', 'mental', 'rubbish', 'cant', 'arsed', 'care', 'dont'] if w in self.learned_words]
        
        # Build response using ONLY learned words
        response_words = []
        
        # Always start with a connector if available
        if connectors:
            response_words.append(random.choice(connectors))
        
        # Add Tyler reference (high priority)
        if tyler_words and random.random() < 0.7:  # 70% chance
            response_words.append(random.choice(tyler_words))
        
        # Add reaction word
        if reactions and len(response_words) < 4:
            response_words.append(random.choice(reactions))
        
        # Fill with most common words if needed
        if len(response_words) < 3:
            available_words = [word for word, freq in common_words[:20] 
                             if word in self.learned_words and word not in response_words]
            if available_words:
                response_words.extend(random.sample(available_words, 
                                                  min(2, len(available_words))))
        
        # Ensure we have something
        if not response_words and 'mate' in self.learned_words:
            response_words = ['mate']
        elif not response_words:
            # Use any learned word as last resort
            if self.learned_words:
                response_words = [random.choice(list(self.learned_words))]
        
        # Keep it short (max 5 words)
        response_words = response_words[:5]
        
        result = ' '.join(response_words) if response_words else "mate"
        print(f"Generated response: {result}")
        return result
    
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"Gerald bot is online as {self.user}!")
        print(f"Connected to {len(self.guilds)} servers")
        print(f"Vocabulary size: {len(self.learned_words)} words")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="learning your words"
            )
        )
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot's own messages and other bots
        if message.author.bot:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Learn from the user's message
        self.learn_from_message(message.content)
        
        # Check if we should respond
        if await self.should_respond(message):
            await self.send_response(message)
    
    async def should_respond(self, message):
        """Determine if bot should respond to a message."""
        # Check cooldown to prevent spam
        channel_id = message.channel.id
        current_time = datetime.now().timestamp()
        
        if channel_id in self.last_response_time:
            time_since_last = current_time - self.last_response_time[channel_id]
            if time_since_last < self.cooldown_seconds:
                return False
        
        # Always respond to mentions
        if self.user in message.mentions:
            return True
        
        # Check for trigger words
        content_lower = message.content.lower()
        for trigger in self.config["trigger_words"]:
            if trigger.lower() in content_lower:
                return True
        
        # Respond to questions more often
        if '?' in message.content and len(message.content) > 5:
            return random.random() < 0.8
        
        # Random response chance for any message
        return random.random() < self.config["response_chance"]
    
    async def send_response(self, message):
        """Generate and send response."""
        try:
            response = self.generate_response()
            if response:
                await message.channel.send(response)
                
                # Update last response time
                self.last_response_time[message.channel.id] = datetime.now().timestamp()
                
        except Exception as e:
            print(f"Error sending response: {e}")

# Bot Commands
@commands.command(name='vocabulary')
async def show_vocabulary(ctx):
    """Show Gerald's learned vocabulary."""
    vocab_size = len(ctx.bot.learned_words)
    most_common = sorted(ctx.bot.word_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    common_words = [f"{word}({count})" for word, count in most_common]
    
    await ctx.send(f"Gerald knows {vocab_size} words. Most used: {', '.join(common_words)}")

@commands.command(name='test')
async def test_response(ctx):
    """Test Gerald's response generation."""
    response = ctx.bot.generate_response()
    vocab_size = len(ctx.bot.learned_words)
    await ctx.send(f"Test response ({vocab_size} words): {response}")

@commands.command(name='teach')
async def teach_word(ctx, *, words):
    """Teach Gerald new words manually."""
    ctx.bot.learn_from_message(words)
    await ctx.send(f"Gerald learned from: {words}")

# Run the bot
async def main():
    """Main function to run the bot."""
    # Get Discord token from environment variable
    token = os.environ.get('DISCORD_TOKEN')
    
    if not token:
        print("ERROR: DISCORD_TOKEN environment variable not set!")
        return
    
    bot = GeraldBot()
    
    # Add commands to bot
    bot.add_command(show_vocabulary)
    bot.add_command(test_response)
    bot.add_command(teach_word)
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
