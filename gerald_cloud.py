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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
            "gaming is pretty cool these days",
            "weather is proper mental innit", 
            "everyone loves good food",
            "tired but gaming sounds good",
            "proper nice when everyone chats",
            "gaming with the lads is epic",
            "why everything so expensive though",
            "love a good game session",
            "tyler probably gaming again",
            "nice to chat with you lot"
        ]
        
        # Use learned words to make it more authentic but positive
        if 'gaming' in self.learned_words and 'good' in self.learned_words:
            topics.append("gaming is good mate")
        if 'nice' in self.learned_words and 'chat' in self.learned_words:
            topics.append("nice to chat innit")
        if 'epic' in self.learned_words and 'games' in self.learned_words:
            topics.append("games are epic")
            
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
                # British basics (more positive)
                'mate', 'innit', 'proper', 'nice', 'good', 'cool', 'yeah',
                'thanks', 'cheers', 'brilliant', 'lovely', 'sound', 'right',
                # Friend group stuff
                'tyler', 'jackson', 'lads', 'guys', 'chat', 'talking', 'friends',
                'gaming', 'games', 'play', 'playing', 'fun', 'epic', 'awesome',
                'what', 'how', 'why', 'when', 'where', 'good', 'bad', 'nice',
                # Gaming vocabulary (positive)  
                'fps', 'noob', 'epic', 'gg', 'win', 'victory', 'skill', 'pro',
                # Conversation words
                'hello', 'hey', 'sup', 'wassup', 'cool', 'sweet', 'nice'
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
        connectors = [w for w in ['mate', 'innit', 'yeah', 'oh', 'hey', 'nice', 'good'] if w in self.learned_words]
        tyler_words = [w for w in ['tyler', 'massive', 'heavy', 'pounds', 'weight', 'fat', 'huge', 'big'] if w in self.learned_words]
        positive_reactions = [w for w in ['cool', 'nice', 'good', 'yeah', 'proper', 'epic'] if w in self.learned_words]
        neutral_reactions = [w for w in ['whatever', 'mental', 'cant', 'care', 'dont', 'thanks'] if w in self.learned_words]
        gaming_words = [w for w in ['gaming', 'games', 'play', 'fps', 'gg', 'epic'] if w in self.learned_words]
        descriptors = [w for w in ['real', 'proper', 'mental', 'good', 'bad', 'nice', 'cool'] if w in self.learned_words]
        
        # Analyze context to make better responses
        context_lower = context.lower() if context else ""
        
        # Build response using ONLY learned words but with better logic
        response_words = []
        
        # Context-aware responses (more friendly)
        if 'thanks' in context_lower:
            if 'yeah' in self.learned_words:
                response_words = ['yeah', 'mate'] if 'mate' in self.learned_words else ['yeah']
        elif 'cool' in context_lower or 'nice' in context_lower:
            if positive_reactions:
                response_words = [random.choice(positive_reactions)]
                if len(response_words) < 2 and 'mate' in self.learned_words:
                    response_words.append('mate')
        elif any(game_word in context_lower for game_word in ['game', 'gaming', 'play']) and gaming_words:
            response_words = [random.choice(gaming_words)]
            if descriptors and len(response_words) < 2:
                response_words.append(random.choice(descriptors))
        elif '?' in context_lower:  # Questions get helpful responses
            if connectors:
                response_words = [random.choice(connectors)]
            if len(response_words) < 2 and descriptors:
                response_words.append(random.choice(descriptors))
        else:
            # Default response building (much more friendly)
            # Start with a friendly connector
            if connectors:
                response_words.append(random.choice(connectors))
            
            # RARELY mention Tyler (only 5% chance instead of 30%)
            if tyler_words and random.random() < 0.05:  # Drastically reduced Tyler references
                response_words.append(random.choice(tyler_words))
            
            # Add positive or neutral reaction
            all_reactions = positive_reactions + neutral_reactions
            if all_reactions and len(response_words) < 3:
                response_words.append(random.choice(all_reactions))
        
        # Fill with most common words if response is too short
        if len(response_words) < 2:
            # Prefer positive and neutral words
            preferred_words = [word for word, freq in common_words[:30] 
                             if word in self.learned_words 
                             and word not in response_words 
                             and len(word) > 2
                             and word not in ['fat', 'massive', 'heavy', 'pounds', 'weight']]  # Avoid Tyler words
            
            if preferred_words:
                response_words.extend(random.sample(preferred_words, 
                                                  min(2, len(preferred_words))))
        
        # Ensure we have something friendly
        if not response_words:
            if 'yeah' in self.learned_words:
                response_words = ['yeah']
            elif 'mate' in self.learned_words:
                response_words = ['mate']
            elif self.learned_words:
                # Pick any word except Tyler-related ones
                safe_words = [w for w in self.learned_words if w not in ['fat', 'massive', 'heavy', 'pounds', 'weight', 'tyler']]
                if safe_words:
                    response_words = [random.choice(safe_words)]
                else:
                    response_words = [random.choice(list(self.learned_words))]
        
        # Keep it conversational (2-3 words usually)
        response_words = response_words[:3]
        
        result = ' '.join(response_words) if response_words else "yeah mate"
        print(f"Generated friendly response: {result}")
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
    # Get Discord token from environment variable (works for both local .env and cloud)
    token = os.environ.get('DISCORD_TOKEN') or os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("ERROR: DISCORD_TOKEN not found!")
        print("For local: Add DISCORD_TOKEN to your .env file")
        print("For cloud: Set DISCORD_TOKEN environment variable")
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
