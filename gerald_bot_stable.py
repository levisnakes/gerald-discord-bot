#!/usr/bin/env python3
"""
Stable Discord Bot with Ollama AI Integration
Fixed version without logging issues.
"""

import discord
from discord.ext import commands
import asyncio
import os
import logging
from dotenv import load_dotenv
import json
import random
from datetime import datetime

# Load environment variables
load_dotenv()

# Simple logging setup that works on Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from utils.ollama_manager import OllamaManager
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama manager not available. Bot will run in basic mode.")

class GeraldBot(commands.Bot):
    """
    Discord bot powered by Ollama AI that responds contextually.
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
        
        # Initialize Ollama manager
        self.ollama = None
        if OLLAMA_AVAILABLE:
            self.ollama = OllamaManager()
        
        # Conversation history for context
        self.conversation_history = {}
        
        # Last response time to prevent spam
        self.last_response_time = {}
        self.cooldown_seconds = 2  # Wait 2 seconds between responses
        
        # Word learning system - only use words that have been said
        self.learned_words = set()
        self.word_frequency = {}
        self.load_learned_words()
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load bot configuration."""
        # Default configuration
        default_config = {
            "response_chance": 0.25,  # Respond to 25% of messages
            "max_history": 10,
            "ollama_model": "gemma2:2b",
            "allowed_channels": [],
            "trigger_words": ["hey", "hello", "gerald", "what do you think"],
            "personality_mode": "casual"
        }
        
        try:
            with open('config.json', 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.config = {**default_config, **loaded_config}
        except FileNotFoundError:
            self.config = default_config
            self.save_config()
        
        # Ensure all required keys exist (in case config is outdated)
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Save the updated config
        self.save_config()
    
    def load_learned_words(self):
        """Load words that Gerald has learned from conversations."""
        try:
            with open('gerald_vocabulary.json', 'r') as f:
                vocab_data = json.load(f)
                self.learned_words = set(vocab_data.get('words', []))
                self.word_frequency = vocab_data.get('frequency', {})
        except FileNotFoundError:
            # Start with basic British words if no vocabulary exists
            self.learned_words = {
                'mate', 'innit', 'bloody', 'hell', 'proper', 'mental', 'rubbish',
                'cant', 'be', 'arsed', 'whatever', 'dont', 'care', 'you', 'lot',
                'tyler', 'massive', 'heavy', 'pounds', 'weight', 'fat'
            }
            self.word_frequency = {}
            self.save_learned_words()
    
    def save_learned_words(self):
        """Save Gerald's vocabulary to file."""
        vocab_data = {
            'words': list(self.learned_words),
            'frequency': self.word_frequency,
            'last_updated': datetime.now().isoformat()
        }
        with open('gerald_vocabulary.json', 'w') as f:
            json.dump(vocab_data, f, indent=2)
    
    def learn_from_message(self, message_content):
        """Learn new words from a user message."""
        # Clean and split the message
        words = message_content.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
        
        new_words_learned = 0
        for word in words:
            # Filter out very short words and common stop words
            if len(word) > 1 and word not in ['the', 'and', 'or', 'but', 'if', 'then']:
                if word not in self.learned_words:
                    new_words_learned += 1
                
                self.learned_words.add(word)
                self.word_frequency[word] = self.word_frequency.get(word, 0) + 1
        
        if new_words_learned > 0:
            print(f"Gerald learned {new_words_learned} new words: {words}")
            self.save_learned_words()
    
    def generate_response_from_learned_words(self, context=""):
        """Generate a response using only learned words - GUARANTEED vocabulary compliance."""
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
        if tyler_words and random.random() < 0.8:  # 80% chance
            response_words.append(random.choice(tyler_words))
            if len(tyler_words) > 1 and random.random() < 0.5:
                tyler_word2 = random.choice([w for w in tyler_words if w != response_words[-1]])
                response_words.append(tyler_word2)
        
        # Add reaction word
        if reactions and len(response_words) < 5:
            response_words.append(random.choice(reactions))
        
        # Fill with most common words if needed
        if len(response_words) < 3:
            available_words = [word for word, freq in common_words[:30] 
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
        
        # Keep it short (max 6 words)
        response_words = response_words[:6]
        
        result = ' '.join(response_words) if response_words else "..."
        print(f"Vocabulary-only response: {result}")
        return result
    
    def save_config(self):
        """Save configuration to file."""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"Gerald bot is online as {self.user}!")
        print(f"Connected to {len(self.guilds)} servers")
        
        # Initialize Ollama
        if self.ollama:
            await self.ollama.initialize()
            if self.ollama.available:
                await self.ollama.set_model(self.config.get("ollama_model", "gemma2:2b"))
                print("AI: Ollama is ready!")
            else:
                print("AI: Using fallback responses")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="casual conversations"
            )
        )
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Debug logging
        print(f"Message from: {message.author.name} (ID: {message.author.id})")
        print(f"Bot user ID: {self.user.id if self.user else 'None'}")
        print(f"Is bot: {message.author.bot}")
        print(f"Content: {message.content}")
        
        # Ignore bot's own messages and other bots - STRICT CHECK
        if message.author.bot:
            print("Ignoring bot message")
            return
            
        if self.user and message.author.id == self.user.id:
            print("Ignoring own message")
            return
            
        # Extra safety: ignore messages from Gerald specifically
        if message.author.name.lower() == "gerald":
            print("Ignoring Gerald message")
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check if we should respond
        if await self.should_respond(message):
            print("Generating response...")
            # Learn from the user's message first
            self.learn_from_message(message.content)
            await self.generate_response(message)
        else:
            print("Not responding to this message")
    
    async def should_respond(self, message):
        """Determine if bot should respond to a message."""
        if message.author.bot:
            return False
        
        # Check cooldown to prevent spam
        channel_id = message.channel.id
        current_time = datetime.now().timestamp()
        
        if channel_id in self.last_response_time:
            time_since_last = current_time - self.last_response_time[channel_id]
            if time_since_last < self.cooldown_seconds:
                return False
        
        # Check allowed channels
        if (self.config["allowed_channels"] and 
            message.channel.id not in self.config["allowed_channels"]):
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
        if '?' in message.content and len(message.content) > 10:
            return random.random() < 0.6
        
        # Random response chance for any message
        return random.random() < self.config["response_chance"]
    
    async def generate_response(self, message):
        """Generate and send AI response."""
        # Final safety check - absolutely no bot responses
        if message.author.bot or (self.user and message.author.id == self.user.id):
            print("SAFETY: Blocked response to bot message")
            return
            
        try:
            async with message.channel.typing():
                response = None
                
                # Try AI first if available
                if self.ollama and self.ollama.available:
                    response = await self.generate_ai_response(message)
                
                # Use contextual fallback if AI fails
                if not response:
                    # Use learned words for fallback response
                    response = self.generate_response_from_learned_words()
                    print(f"Using learned vocabulary fallback: {response}")
                
                if response:
                    print(f"Sending response: {response}")
                    await message.channel.send(response)
                    self.store_conversation(message, response)
                    
                    # Update last response time
                    self.last_response_time[message.channel.id] = datetime.now().timestamp()
                    
        except Exception as e:
            print(f"Error generating response: {e}")
            await message.channel.send("hmm, something went wrong")
    
    async def generate_ai_response(self, message):
        """Generate response using Ollama AI with better prompting."""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Get conversation context
                context = self.get_conversation_context(message.channel.id)
                
                # Create a very specific prompt with learned vocabulary
                learned_vocab = ', '.join(sorted(list(self.learned_words)))  # Show ALL available words
                
                prompt = f"""You are Gerald, an angry British Discord user. 

CRITICAL RULE: You can ONLY use words from this exact list. Do NOT use any other words:
{learned_vocab}

USER SAID: "{message.content}"

IMPORTANT: Your response must ONLY contain words from the list above. Every single word must be from that vocabulary list.

RESPOND AS GERALD:
- Use ONLY words from the vocabulary list above
- 2-8 words maximum  
- Bad grammar and spelling
- Angry British tone
- Mention Tyler's weight if possible
- NO punctuation
- ONE response only

EXAMPLE VALID RESPONSES (if these words are in vocabulary):
- "mate tyler massive innit"
- "bloody hell tyler heavy"
- "whatever tyler fat mate"

Gerald responds using ONLY vocabulary words:"""
                
                # Generate response with the Ollama manager
                response = await self.ollama.generate_response(prompt, context, "")
                
                # Clean up response to ensure it's just one line
                if response:
                    response = response.strip()
                    # Take only the first line if multiple lines exist
                    response = response.split('\n')[0].strip()
                    # Remove any extra punctuation or formatting
                    response = response.strip('.,!?;:"')
                
                # Validate the response
                if response and self.is_good_response(response, message.content):
                    print(f"AI generated good response: {response[:50]}...")
                    return response
                else:
                    print(f"AI response rejected on attempt {attempt + 1}: '{response}'")
                    
            except Exception as e:
                print(f"AI generation failed on attempt {attempt + 1}: {e}")
        
        print("All AI attempts failed")
        return None
    
    def is_good_response(self, response, original_message):
        """Check if the AI response is good and only uses learned words."""
        if not response or len(response) < 3:
            return False
        
        # Split response into words and check each one
        response_words = response.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
        
        # STRICT CHECK: Every word must be in learned vocabulary
        for word in response_words:
            if word not in self.learned_words:
                print(f"REJECTED: '{word}' not in learned vocabulary")
                return False
        
        # Block known bad responses
        bad_responses = [
            "bruh how", "bruh, how", "probably", "idk", "yuh", "nah", 
            "ohhhh", "maybe", "but why would you", "what even"
        ]
        
        response_lower = response.lower().strip()
        for bad in bad_responses:
            if response_lower == bad.lower() or response_lower.startswith(bad.lower()):
                return False
        
        # Require short responses (1-8 words for angry British style)
        if len(response_words) > 8:  # Keep responses short and snappy
            return False
        
        # Must have at least 2 words
        if len(response_words) < 2:
            return False
        
        print(f"APPROVED: All words in vocabulary: {response_words}")
        return True
    
    def generate_contextual_fallback(self, message):
        """Generate contextual fallback responses."""
        content = message.content.lower()
        
        # Angry British fallback responses
        if '?' in message.content:
            responses = [
                "dunno mate",
                "how should i know",
                "cant be bothered",
                "ask someone else innit"
            ]
        elif any(word in content for word in ['sentence', 'grammar', 'language', 'words']):
            responses = [
                "proper mental that",
                "sounds rubbish",
                "who cares about grammar"
            ]
        elif any(word in content for word in ['tired', 'sleep', 'bed']):
            responses = [
                "stop moaning then",
                "go sleep then",
                "bloody tired all the time"
            ]
        elif any(word in content for word in ['game', 'gaming', 'play']):
            responses = [
                "games are mental",
                "waste of time innit",
                "get a life mate"
            ]
        elif any(word in content for word in ['food', 'eat', 'hungry', 'dinner']):
            responses = [
                "make your own food",
                "always eating you lot",
                "proper greedy"
            ]
        else:
            # Generic angry British responses
            responses = [
                "whatever mate",
                "dont care",
                "mental that is",
                "bloody hell",
                "what you on about",
                "cant be arsed"
            ]
        
        return random.choice(responses)
    
    def get_conversation_context(self, channel_id):
        """Get recent conversation context."""
        if channel_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[channel_id]
        if not history:
            return ""
        
        # Format recent messages for context
        context_lines = []
        for entry in history[-3:]:  # Last 3 exchanges
            context_lines.append(f"User: {entry['user_message']}")
            context_lines.append(f"Gerald: {entry['bot_response']}")
        
        return "\n".join(context_lines)
    
    def store_conversation(self, message, response):
        """Store conversation for context."""
        channel_id = message.channel.id
        
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []
        
        self.conversation_history[channel_id].append({
            'user_message': message.content,
            'bot_response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent history
        max_history = self.config["max_history"]
        if len(self.conversation_history[channel_id]) > max_history:
            self.conversation_history[channel_id] = self.conversation_history[channel_id][-max_history:]
    
    async def close(self):
        """Clean up when bot shuts down."""
        if self.ollama:
            await self.ollama.close()
        await super().close()

# Bot Commands
@commands.command(name='test_ai')
async def test_ai(ctx, *, message):
    """Test AI response directly."""
    if not ctx.bot.ollama or not ctx.bot.ollama.available:
        await ctx.send("AI not available")
        return
    
    response = await ctx.bot.generate_ai_response(type('obj', (object,), {'content': message, 'channel': ctx.channel})())
    
    if response:
        await ctx.send(f"AI: {response}")
    else:
        await ctx.send("AI couldn't generate a good response")

@commands.command(name='reset')
async def reset_ai(ctx):
    """Reset AI conversation history."""
    ctx.bot.conversation_history = {}
    await ctx.send("Memory reset!")

@commands.command(name='status')
async def bot_status(ctx):
    """Show bot status."""
    if ctx.bot.ollama and ctx.bot.ollama.available:
        status = "AI Ready"
    else:
        status = "Fallback Mode"
    
    await ctx.send(f"Status: {status}")

@commands.command(name='vocabulary')
async def show_vocabulary(ctx):
    """Show Gerald's learned vocabulary."""
    vocab_size = len(ctx.bot.learned_words)
    most_common = sorted(ctx.bot.word_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    common_words = [f"{word}({count})" for word, count in most_common]
    
    await ctx.send(f"Gerald knows {vocab_size} words. Most used: {', '.join(common_words)}")

@commands.command(name='teach')
async def teach_word(ctx, *, words):
    """Teach Gerald new words manually."""
    ctx.bot.learn_from_message(words)
    await ctx.send(f"Gerald learned from: {words}")

@commands.command(name='vocab_test')
async def test_vocabulary_response(ctx):
    """Test Gerald's vocabulary-only response generation."""
    response = ctx.bot.generate_response_from_learned_words()
    vocab_size = len(ctx.bot.learned_words)
    await ctx.send(f"Vocab test ({vocab_size} words): {response}")

@commands.command(name='clear_vocab')
async def clear_vocabulary(ctx):
    """Clear Gerald's vocabulary (admin only)."""
    ctx.bot.learned_words = {'mate', 'tyler', 'massive'}  # Reset to basics
    ctx.bot.word_frequency = {}
    ctx.bot.save_learned_words()
    await ctx.send("Gerald's vocabulary cleared! He only knows: mate, tyler, massive")

# Run the bot
async def main():
    """Main function to run the bot."""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("No Discord token found!")
        return
    
    bot = GeraldBot()
    
    # Add commands to bot
    bot.add_command(test_ai)
    bot.add_command(reset_ai)
    bot.add_command(bot_status)
    bot.add_command(show_vocabulary)
    bot.add_command(teach_word)
    bot.add_command(test_vocabulary_response)
    bot.add_command(clear_vocabulary)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
