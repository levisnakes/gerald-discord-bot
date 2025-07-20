#!/usr/bin/env python3
"""
Discord Bot with Ollama AI Integration
Uses Ollama for true AI responses instead of predetermined messages.
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

# Set up logging with UTF-8 encoding for Windows
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from utils.ollama_manager import OllamaManager
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama manager not available. Bot will run in basic mode.")

class BaconatorAIBot(commands.Bot):
    """
    Discord bot powered by Ollama AI that mimics Baconator's personality.
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
        
        # Track recent responses to avoid repetition
        self.recent_responses = []
        self.max_recent_responses = 5
        
        # Load configuration
        self.load_config()
        
        # Load Baconator's training data for personality context
        self.baconator_phrases = self.load_baconator_data()
    
    def load_config(self):
        """Load bot configuration."""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "response_chance": 0.25,  # Respond to 25% of messages
                "max_history": 10,
                "ollama_model": "gemma2:2b",  # Faster, smaller model
                "allowed_channels": [],
                "trigger_words": ["hey", "hello", "gerald", "what do you think"],  # Removed "baconator"
                "personality_mode": "casual"  # Changed from "baconator" to "casual"
            }
            self.save_config()
    
    def save_config(self):
        """Save configuration to file."""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_baconator_data(self):
        """Load Baconator's message data for personality context."""
        try:
            with open('data/baconator_messages.json', 'r') as f:
                data = json.load(f)
                phrases = [msg['content'] for msg in data if len(msg['content']) < 100]
                logger.info(f"Loaded {len(phrases)} Baconator phrases for personality context")
                return phrases
        except Exception as e:
            logger.warning(f"Could not load Baconator data: {e}")
            return []
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Initialize Ollama
        if self.ollama:
            await self.ollama.initialize()
            if self.ollama.available:
                await self.ollama.set_model(self.config["ollama_model"])
                logger.info("AI: Ollama AI is ready!")
            else:
                logger.warning("AI: Ollama not available - using fallback responses")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="casual conversations"
            )
        )
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check if we should respond
        if await self.should_respond(message):
            await self.generate_response(message)
    
    async def should_respond(self, message):
        """Determine if bot should respond to a message."""
        if message.author.bot:
            return False
        
        # Check allowed channels
        if (self.config["allowed_channels"] and 
            message.channel.id not in self.config["allowed_channels"]):
            return False
        
        # Always respond to mentions
        if self.user in message.mentions:
            return True
        
        # Check for trigger words - respond to anyone saying these
        content_lower = message.content.lower()
        for trigger in self.config["trigger_words"]:
            if trigger.lower() in content_lower:
                return True
        
        # Respond to questions directed at the group
        if '?' in message.content and len(message.content) > 10:
            return random.random() < 0.6  # Higher chance for questions
        
        # Random response chance for any message
        return random.random() < self.config["response_chance"]
    
    async def generate_response(self, message):
        """Generate and send AI response."""
        try:
            async with message.channel.typing():
                response = None
                ai_used = False
                
                # Always try AI first if available
                if self.ollama and self.ollama.available:
                    logger.info(f"Trying AI for message: {message.content[:50]}...")
                    response = await self.generate_ollama_response(message)
                    if response:
                        ai_used = True
                        logger.info(f"AI succeeded: {response[:50]}...")
                    else:
                        logger.warning("AI failed, using fallback")
                
                # Only use fallback if AI completely fails
                if not response:
                    logger.info("Using contextual fallback")
                    response = self.generate_baconator_fallback(message)
                
                if response:
                    await message.channel.send(response)
                    self.store_conversation(message, response)
                    
                    # Log which system was used
                    system_used = "AI" if ai_used else "Fallback"
                    logger.info(f"Sent {system_used} response: {response}")
                    
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            await message.channel.send("hmm, something went wrong there")
    
    async def generate_ollama_response(self, message):
        """Generate response using Ollama AI with retry logic."""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Get conversation context
                context = self.get_conversation_context(message.channel.id)
                
                # Create personality prompt
                personality_prompt = self.create_personality_prompt()
                
                # Generate response
                response = await self.ollama.generate_response(
                    prompt=message.content,
                    context=context,
                    personality_prompt=personality_prompt
                )
                
                # If we got a good response, return it
                if response and len(response) > 10:
                    logger.info(f"AI generated good response on attempt {attempt + 1}: {response[:50]}...")
                    return response
                else:
                    logger.info(f"AI response too short on attempt {attempt + 1}, retrying...")
                    
            except Exception as e:
                logger.error(f"Ollama generation failed on attempt {attempt + 1}: {e}")
        
        logger.warning("All AI attempts failed, using fallback")
        return None
    
    def create_personality_prompt(self):
        """Create personality prompt for contextual responses."""
        # Don't provide predetermined examples - let AI be creative
        base_prompt = """You are Gerald, a friendly Discord user chatting in a group. 

Your job is to:
- Read what the person just said and respond specifically to it
- Be natural and conversational, like a real friend would
- Generate fresh, relevant responses based on the context
- Show you understand what they're talking about
- Be helpful, funny, or engaging as appropriate to the situation

DO NOT use predetermined phrases. Instead, respond naturally to whatever the person said."""
        
        return base_prompt
    
    def generate_baconator_fallback(self, message):
        """Generate contextual fallback responses when AI fails."""
        content = message.content.lower()
        
        # Try to be contextual even in fallback
        if '?' in message.content:
            contextual_responses = [
                "That's a good question!",
                "Hmm, let me think about that...",
                "Not sure about that one",
                "What do you think?",
                "Interesting question"
            ]
        elif any(word in content for word in ['tired', 'sleep', 'bed']):
            contextual_responses = [
                "You should get some rest!",
                "Sleep sounds good right now",
                "Yeah, being tired sucks"
            ]
        elif any(word in content for word in ['game', 'play', 'gaming']):
            contextual_responses = [
                "Gaming time!",
                "What are you playing?",
                "Nice, games are fun"
            ]
        elif any(word in content for word in ['food', 'eat', 'hungry', 'dinner', 'lunch']):
            contextual_responses = [
                "Food sounds good!",
                "What are you thinking of eating?",
                "I could go for some food too"
            ]
        else:
            # Generic but still better than "bruh how"
            contextual_responses = [
                "That's interesting!",
                "Tell me more about that",
                "I see what you mean",
                "That makes sense",
                "Ah, gotcha"
            ]
        
        import random
        return random.choice(contextual_responses)
    
    def get_conversation_context(self, channel_id):
        """Get recent conversation context for better AI understanding."""
        if channel_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[channel_id]
        if not history:
            return ""
        
        # Format recent messages with more context
        context_lines = []
        for entry in history[-4:]:  # Last 4 exchanges for better context
            user_msg = entry['user_message']
            bot_response = entry['bot_response']
            
            # Include both sides of conversation for context
            context_lines.append(f"Someone said: {user_msg}")
            context_lines.append(f"Gerald replied: {bot_response}")
        
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
@commands.command(name='force_ai')
async def force_ai_response(ctx, *, message):
    """Force AI to respond to a message (for testing)."""
    if not ctx.bot.ollama or not ctx.bot.ollama.available:
        await ctx.send("❌ AI is not available")
        return
    
    logger.info(f"Force AI test for: {message}")
    
    # Test the AI multiple times
    for i in range(3):
        async with ctx.typing():
            response = await ctx.bot.ollama.generate_response(
                prompt=message,
                context="",
                personality_prompt=""
            )
            
            if response:
                await ctx.send(f"**Attempt {i+1}:** {response}")
            else:
                await ctx.send(f"**Attempt {i+1}:** ❌ No response generated")

@commands.command(name='ask')
async def ask_ai(ctx, *, question):
    """Ask Gerald a direct question to test AI responses."""
    if not ctx.bot.ollama or not ctx.bot.ollama.available:
        await ctx.send("❌ AI is not available right now")
        return
    
    async with ctx.typing():
        # Create a fake message object for the AI
        class FakeMessage:
            def __init__(self, content):
                self.content = content
                self.channel = ctx.channel
        
        fake_msg = FakeMessage(question)
        response = await ctx.bot.generate_ollama_response(fake_msg)
        
        if response:
            await ctx.send(f"🤖 {response}")
        else:
            await ctx.send("🤔 I couldn't think of a good response to that")

@commands.command(name='reset')
async def reset_ai(ctx):
    """Reset AI conversation history to fix repetitive responses."""
    ctx.bot.conversation_history = {}
    ctx.bot.recent_responses = []
    await ctx.send("🔄 AI memory reset! Should be more varied now.")

@commands.command(name='model')
async def change_model(ctx, model_name: str):
    """Change the Ollama model being used."""
    if not ctx.bot.ollama or not ctx.bot.ollama.available:
        await ctx.send("❌ Ollama is not available")
        return
    
    success = await ctx.bot.ollama.set_model(model_name)
    if success:
        ctx.bot.config["ollama_model"] = model_name
        ctx.bot.save_config()
        await ctx.send(f"✅ Switched to model: {model_name}")
    else:
        await ctx.send(f"❌ Model {model_name} not found")

@commands.command(name='status')
async def bot_status(ctx):
    """Show bot status and AI availability."""
    embed = discord.Embed(title="🤖 Gerald Bot Status", color=0x00ff00)
    
    if ctx.bot.ollama and ctx.bot.ollama.available:
        embed.add_field(name="AI Engine", value="🟢 Ollama (Active)", inline=False)
        embed.add_field(name="Model", value=ctx.bot.ollama.model_name, inline=True)
    else:
        embed.add_field(name="AI Engine", value="🟡 Fallback Mode", inline=False)
    
    embed.add_field(name="Response Chance", value=f"{ctx.bot.config['response_chance']*100:.0f}%", inline=True)
    embed.add_field(name="Personality", value="Casual & Natural", inline=True)
    
    await ctx.send(embed=embed)

# Run the bot
async def main():
    """Main function to run the bot."""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("No Discord token found in environment variables!")
        return
    
    bot = BaconatorAIBot()
    
    # Add commands to bot
    bot.add_command(force_ai_response)
    bot.add_command(ask_ai)
    bot.add_command(reset_ai)
    bot.add_command(change_model)
    bot.add_command(bot_status)
    
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
