#!/usr/bin/env python3
"""
Discord Friend AI Bot
A Discord bot with a custom language model trained on friend's messages.
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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from utils.model_manager import ModelManager
    from utils.message_processor import MessageProcessor
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    logger.warning("Model utilities not available. Bot will run in basic mode.")

class FriendAIBot(commands.Bot):
    """
    Discord bot with AI capabilities trained on friend's messages.
    """
    
    def __init__(self):
        # Set up bot intents (minimal required intents)
        intents = discord.Intents.default()
        intents.message_content = True
        # Don't require privileged intents for basic functionality
        intents.members = False
        intents.presences = False
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize components
        self.model_manager = None
        self.message_processor = None
        self.conversation_history = {}
        self.friend_personality = {}
        
        if MODEL_AVAILABLE:
            self.model_manager = ModelManager()
            self.message_processor = MessageProcessor()
            
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load bot configuration from file."""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                "friend_name": "Friend",
                "response_chance": 0.3,
                "max_history": 10,
                "model_name": "gpt2",
                "enable_learning": True,
                "allowed_channels": [],
                "trigger_words": ["hey", "hello", "what do you think"]
            }
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Load trained model if available
        if self.model_manager:
            await self.load_friend_model()
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"messages like {self.config['friend_name']} 🤖"
            )
        )
    
    async def load_friend_model(self):
        """Load the trained friend model."""
        try:
            self.model_manager.load_model("models/friend_model")
            logger.info("Friend AI model loaded successfully!")
        except Exception as e:
            logger.warning(f"Could not load friend model: {e}")
            logger.info("Bot will use basic responses")
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check if we should respond to this message
        if await self.should_respond(message):
            await self.generate_response(message)
    
    async def should_respond(self, message):
        """Determine if bot should respond to a message."""
        # Don't respond to other bots
        if message.author.bot:
            return False
        
        # Check allowed channels
        if (self.config["allowed_channels"] and 
            message.channel.id not in self.config["allowed_channels"]):
            return False
        
        # Check if bot is mentioned
        if self.user in message.mentions:
            return True
        
        # Check for trigger words
        content_lower = message.content.lower()
        for trigger in self.config["trigger_words"]:
            if trigger.lower() in content_lower:
                return True
        
        # Random response chance
        return random.random() < self.config["response_chance"]
    
    async def generate_response(self, message):
        """Generate and send AI response."""
        try:
            # Add typing indicator
            async with message.channel.typing():
                if self.model_manager and self.model_manager.model_loaded:
                    # Use trained AI model
                    response = await self.generate_ai_response(message)
                else:
                    # Use fallback responses
                    response = self.generate_fallback_response(message)
                
                # Add some personality
                response = self.add_personality(response)
                
                # Send response
                if response:
                    await message.channel.send(response)
                    
                    # Store conversation history
                    self.store_conversation(message, response)
                    
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            await message.channel.send("Sorry, I'm having trouble thinking right now! 😅")
    
    async def generate_ai_response(self, message):
        """Generate response using trained AI model."""
        try:
            # Prepare context
            context = self.get_conversation_context(message)
            prompt = f"{context}\n{message.author.display_name}: {message.content}\n{self.config['friend_name']}:"
            
            # Generate response
            response = self.model_manager.generate_response(prompt)
            
            # Clean up response
            if self.message_processor:
                response = self.message_processor.clean_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return None
    
    def generate_fallback_response(self, message):
        """Generate basic response when AI model is not available."""
        fallback_responses = [
            "That's interesting! 🤔",
            "I see what you mean!",
            "Hmm, tell me more about that",
            "That reminds me of something...",
            "Haha, totally!",
            "I'm still learning to respond like your friend! 🤖",
            "What do you think about that?",
            "That's a good point!"
        ]
        
        # Simple keyword-based responses
        content_lower = message.content.lower()
        
        if any(word in content_lower for word in ['funny', 'lol', 'haha']):
            return random.choice(["😂", "Haha that's hilarious!", "I love that! 😄"])
        
        if any(word in content_lower for word in ['sad', 'down', 'upset']):
            return random.choice(["Aw, hope you feel better! 💙", "I'm here if you need to talk"])
        
        if '?' in message.content:
            return random.choice([
                "That's a great question!",
                "Hmm, what do you think?",
                "I'd have to think about that one!"
            ])
        
        return random.choice(fallback_responses)
    
    def add_personality(self, response):
        """Add personality traits to responses."""
        if not response:
            return response
            
        # Add random emoji occasionally
        if random.random() < 0.2:
            emojis = ["😊", "🤔", "😄", "👍", "✨", "🎉"]
            response += " " + random.choice(emojis)
        
        return response
    
    def get_conversation_context(self, message):
        """Get recent conversation context."""
        channel_id = message.channel.id
        if channel_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[channel_id]
        recent_messages = history[-self.config["max_history"]:]
        
        context_lines = []
        for msg_data in recent_messages:
            context_lines.append(f"{msg_data['author']}: {msg_data['content']}")
        
        return "\n".join(context_lines)
    
    def store_conversation(self, message, response):
        """Store conversation in history."""
        channel_id = message.channel.id
        
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []
        
        # Store user message
        self.conversation_history[channel_id].append({
            'author': message.author.display_name,
            'content': message.content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Store bot response
        self.conversation_history[channel_id].append({
            'author': self.config['friend_name'],
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit history size
        max_size = self.config["max_history"] * 2
        if len(self.conversation_history[channel_id]) > max_size:
            self.conversation_history[channel_id] = self.conversation_history[channel_id][-max_size:]

# Bot Commands
@commands.command(name='chat')
async def chat_command(ctx, *, message):
    """Chat with the friend AI."""
    bot = ctx.bot
    
    # Create a mock message object for processing
    class MockMessage:
        def __init__(self, content, author, channel):
            self.content = content
            self.author = author
            self.channel = channel
            self.mentions = []
    
    mock_msg = MockMessage(message, ctx.author, ctx.channel)
    await bot.generate_response(mock_msg)

@commands.command(name='personality')
async def personality_command(ctx):
    """Show learned personality traits."""
    embed = discord.Embed(
        title=f"{ctx.bot.config['friend_name']}'s AI Personality",
        color=discord.Color.blue()
    )
    
    if ctx.bot.model_manager and ctx.bot.model_manager.model_loaded:
        embed.add_field(
            name="Model Status",
            value="✅ Custom AI model loaded",
            inline=False
        )
    else:
        embed.add_field(
            name="Model Status", 
            value="⚠️ Using basic responses (train model for better responses)",
            inline=False
        )
    
    embed.add_field(
        name="Response Chance",
        value=f"{ctx.bot.config['response_chance']*100:.0f}%",
        inline=True
    )
    
    embed.add_field(
        name="Conversation Memory",
        value=f"{ctx.bot.config['max_history']} messages",
        inline=True
    )
    
    await ctx.send(embed=embed)

@commands.command(name='config')
async def config_command(ctx, setting=None, *, value=None):
    """Configure bot settings."""
    if not setting:
        # Show current config
        embed = discord.Embed(title="Bot Configuration", color=discord.Color.green())
        for key, val in ctx.bot.config.items():
            embed.add_field(name=key, value=str(val), inline=False)
        await ctx.send(embed=embed)
        return
    
    if setting in ctx.bot.config and value:
        # Update setting
        try:
            # Try to convert to appropriate type
            if setting == "response_chance":
                ctx.bot.config[setting] = float(value)
            elif setting in ["max_history"]:
                ctx.bot.config[setting] = int(value)
            elif setting in ["trigger_words", "allowed_channels"]:
                ctx.bot.config[setting] = value.split(',')
            else:
                ctx.bot.config[setting] = value
            
            ctx.bot.save_config()
            await ctx.send(f"✅ Updated {setting} to: {value}")
        except ValueError:
            await ctx.send(f"❌ Invalid value for {setting}")
    else:
        await ctx.send(f"❌ Unknown setting: {setting}")

async def main():
    """Main function to run the bot."""
    # Check for Discord token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.info("Please create a .env file with your Discord bot token:")
        logger.info("DISCORD_TOKEN=your_token_here")
        return
    
    # Create and run bot
    bot = FriendAIBot()
    
    # Add commands to bot
    bot.add_command(chat_command)
    bot.add_command(personality_command)
    bot.add_command(config_command)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
