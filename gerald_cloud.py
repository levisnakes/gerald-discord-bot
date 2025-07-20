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
        
        # Persistent conversation memory - remembers everything
        self.all_conversations = []
        self.conversation_topics = {}
        self.user_personalities = {}
        self.load_conversations()
        
        # Last response time to prevent spam
        self.last_response_time = {}
        self.cooldown_seconds = 3
        
        # Random rant system
        self.last_rant_time = 0
        self.rant_cooldown = 300  # 5 minutes between rants
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load bot configuration."""
        # Default configuration - friend group personality
        self.config = {
            "response_chance": 0.4,  # More active in conversations
            "max_history": 50,  # Remember more messages
            "trigger_words": ["hey", "hello", "gerald", "what do you think", "games", "gaming", "play"],
            "friend_names": ["tyler", "jackson", "mate", "guys", "lads"],  # Friend group members
            "topics": ["gaming", "food", "weight", "tired", "boring", "mental", "rubbish"],
        }
    
    def load_conversations(self):
        """Load all conversation history from file."""
        try:
            with open('gerald_memory.json', 'r') as f:
                memory_data = json.load(f)
                self.all_conversations = memory_data.get('conversations', [])
                self.conversation_topics = memory_data.get('topics', {})
                self.user_personalities = memory_data.get('users', {})
                print(f"Gerald remembers {len(self.all_conversations)} conversations")
        except FileNotFoundError:
            self.all_conversations = []
            self.conversation_topics = {}
            self.user_personalities = {}
            print("Gerald starting with fresh memory")
    
    def save_conversations(self):
        """Save all conversations to persistent storage."""
        memory_data = {
            'conversations': self.all_conversations[-1000:],  # Keep last 1000 messages
            'topics': self.conversation_topics,
            'users': self.user_personalities,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open('gerald_memory.json', 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")
    
    def remember_message(self, message):
        """Store message in permanent memory."""
        memory_entry = {
            'author': message.author.name,
            'content': message.content,
            'channel': message.channel.name if hasattr(message.channel, 'name') else 'DM',
            'timestamp': datetime.now().isoformat(),
            'mentions': [m.name for m in message.mentions if m != self.user]
        }
        
        self.all_conversations.append(memory_entry)
        
        # Learn about user personality
        author_name = message.author.name.lower()
        if author_name not in self.user_personalities:
            self.user_personalities[author_name] = {
                'common_words': {},
                'topics': [],
                'message_count': 0
            }
        
        self.user_personalities[author_name]['message_count'] += 1
        
        # Save every 10 messages to avoid data loss
        if len(self.all_conversations) % 10 == 0:
            self.save_conversations()
    
    def get_random_rant_topic(self):
        """Generate a random rant about something from memory."""
        topics = [
            "tyler being massive",
            "games being rubbish these days", 
            "everyone always eating",
            "people moaning about being tired",
            "proper mental weather innit",
            "cant be arsed with anything today",
            "why everything so expensive now",
            "gaming all night then moaning",
            "tyler probably eating again",
            "bloody hell this is boring"
        ]
        
        # Use learned words to make it more authentic
        if 'gaming' in self.learned_words and 'rubbish' in self.learned_words:
            topics.append("gaming is proper rubbish mate")
        if 'tyler' in self.learned_words and 'massive' in self.learned_words:
            topics.append("tyler is getting more massive")
            
        return random.choice(topics)
    
    def load_learned_words(self):
        """Load words that Gerald has learned from conversations."""
        try:
            with open('gerald_vocabulary.json', 'r') as f:
                vocab_data = json.load(f)
                self.learned_words = set(vocab_data.get('words', []))
                self.word_frequency = vocab_data.get('frequency', {})
        except FileNotFoundError:
            # Start with friend group vocabulary
            self.learned_words = {
                # British basics
                'mate', 'innit', 'bloody', 'hell', 'proper', 'mental', 'rubbish',
                'cant', 'be', 'arsed', 'whatever', 'dont', 'care', 'you', 'lot',
                # Friend group stuff
                'tyler', 'jackson', 'massive', 'heavy', 'pounds', 'weight', 'fat', 'huge',
                'gaming', 'games', 'play', 'playing', 'tired', 'boring', 'food', 'eating',
                'what', 'how', 'why', 'when', 'where', 'good', 'bad', 'nice', 'lads', 'guys',
                # Gaming vocabulary  
                'lag', 'fps', 'noob', 'epic', 'gg', 'rip', 'op', 'sus', 'cringe'
            }
            self.word_frequency = {}
        print(f"Gerald starts with {len(self.learned_words)} words")
    
    def save_learned_words(self):
        """Save Gerald's vocabulary to file."""
        vocab_data = {
            'words': list(self.learned_words),
            'frequency': self.word_frequency,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open('gerald_vocabulary.json', 'w') as f:
                json.dump(vocab_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save vocabulary: {e}")
    
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
            self.save_learned_words()  # Save immediately
    
    def generate_response(self, context=""):
        """Generate a response using only learned words with better context awareness."""
        # Get most common words (more likely to be used)
        common_words = sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Split words into categories from learned vocabulary only
        connectors = [w for w in ['mate', 'innit', 'bloody', 'proper', 'hell', 'yeah', 'oh'] if w in self.learned_words]
        tyler_words = [w for w in ['tyler', 'massive', 'heavy', 'pounds', 'weight', 'fat', 'huge', 'big'] if w in self.learned_words]
        reactions = [w for w in ['whatever', 'mental', 'rubbish', 'cant', 'arsed', 'care', 'dont', 'cool', 'thanks'] if w in self.learned_words]
        descriptors = [w for w in ['real', 'proper', 'bloody', 'mental', 'massive', 'good', 'bad', 'nice'] if w in self.learned_words]
        
        # Analyze context to make better responses
        context_lower = context.lower() if context else ""
        
        # Build response using ONLY learned words but with better logic
        response_words = []
        
        # Context-aware responses
        if 'thanks' in context_lower and 'thanks' in self.learned_words:
            response_words = ['yeah', 'whatever'] if all(w in self.learned_words for w in ['yeah', 'whatever']) else ['mate']
        elif 'cool' in context_lower and any(w in self.learned_words for w in ['yeah', 'proper', 'nice']):
            if 'yeah' in self.learned_words:
                response_words = ['yeah']
            if len(response_words) < 2 and descriptors:
                response_words.append(random.choice(descriptors))
        elif 'memory' in context_lower and reactions:
            response_words.append(random.choice(reactions))
        else:
            # Default response building
            # Start with a connector
            if connectors:
                response_words.append(random.choice(connectors))
            
            # Add Tyler reference (lower chance for better variety)
            if tyler_words and random.random() < 0.3:  # Reduced from 70% to 30%
                response_words.append(random.choice(tyler_words))
            
            # Add reaction word
            if reactions and len(response_words) < 3:
                response_words.append(random.choice(reactions))
        
        # Fill with most common words if response is too short
        if len(response_words) < 2:
            available_words = [word for word, freq in common_words[:30] 
                             if word in self.learned_words and word not in response_words and len(word) > 2]
            if available_words:
                response_words.extend(random.sample(available_words, 
                                                  min(2, len(available_words))))
        
        # Ensure we have something
        if not response_words:
            if 'mate' in self.learned_words:
                response_words = ['mate']
            elif self.learned_words:
                response_words = [random.choice(list(self.learned_words))]
        
        # Keep it short but not too short (2-4 words for better conversation)
        response_words = response_words[:4]
        if len(response_words) == 1 and len(self.learned_words) > 10:
            # Add one more word if we have vocabulary
            extra_words = [w for w in self.learned_words if w not in response_words and len(w) > 2]
            if extra_words:
                response_words.append(random.choice(extra_words))
        
        result = ' '.join(response_words) if response_words else "mate"
        print(f"Generated contextual response: {result}")
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
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("mate you forgot something")
        else:
            print(f"Command error: {error}")
            await ctx.send("bloody hell something went wrong")
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot's own messages and other bots
        if message.author.bot:
            return
        
        # Process commands FIRST before anything else
        ctx = await self.get_context(message)
        if ctx.valid:
            await self.invoke(ctx)
            return  # Don't do anything else if it's a command
        
        # Remember EVERY message permanently
        self.remember_message(message)
        
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
        
        # Respond to friend names being mentioned
        for friend in self.config["friend_names"]:
            if friend in content_lower:
                return random.random() < 0.6  # 60% chance
        
        # Random rants (every 5+ minutes)
        if current_time - self.last_rant_time > self.rant_cooldown:
            if random.random() < 0.1:  # 10% chance for random rant
                self.last_rant_time = current_time
                return True
        
        # Respond to questions more often
        if '?' in message.content and len(message.content) > 5:
            return random.random() < 0.8
        
        # Gaming talk gets more responses
        gaming_words = ['game', 'gaming', 'play', 'fps', 'lag', 'gg']
        if any(word in content_lower for word in gaming_words):
            return random.random() < 0.7
        
        # Random response chance for any message
        return random.random() < self.config["response_chance"]
    
    async def send_response(self, message):
        """Generate and send response."""
        try:
            # Check if this should be a random rant
            current_time = datetime.now().timestamp()
            if current_time - self.last_rant_time <= 1:  # Just triggered rant
                response = self.get_random_rant_topic()
            else:
                # Pass the message content as context for better responses
                response = self.generate_response(context=message.content)
                
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

@commands.command(name='memory')
async def show_memory(ctx):
    """Show Gerald's conversation memory stats."""
    total_convos = len(ctx.bot.all_conversations)
    users_remembered = len(ctx.bot.user_personalities)
    recent_convos = ctx.bot.all_conversations[-5:] if ctx.bot.all_conversations else []
    
    memory_info = f"Gerald remembers {total_convos} conversations from {users_remembered} people.\n"
    if recent_convos:
        memory_info += "Recent memories:\n"
        for convo in recent_convos:
            memory_info += f"- {convo['author']}: {convo['content'][:50]}...\n"
    
    await ctx.send(memory_info)

@commands.command(name='rant')
async def force_rant(ctx):
    """Make Gerald rant about something random."""
    rant = ctx.bot.get_random_rant_topic()
    await ctx.send(f"Random rant: {rant}")

@commands.command(name='save')
async def save_memory(ctx):
    """Manually save Gerald's memory (admin only)."""
    ctx.bot.save_conversations()
    ctx.bot.save_learned_words()
    await ctx.send("Gerald's memory saved!")

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
    bot.add_command(show_memory)
    bot.add_command(force_rant)
    bot.add_command(save_memory)
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
