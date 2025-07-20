#!/usr/bin/env python3
"""
Bot Status Checker
Check if the AI bot is working and responding properly.
"""

import asyncio
import discord
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_bot_connection():
    """Test if bot can connect and show its capabilities."""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ No Discord token found!")
        return
    
    try:
        # Create test client
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"✅ Bot '{client.user}' is online and working!")
            print(f"🌐 Connected to {len(client.guilds)} servers:")
            
            for guild in client.guilds:
                print(f"   - {guild.name} (ID: {guild.id})")
                print(f"     Members: {guild.member_count}")
            
            # Check if training data exists
            try:
                with open('data/baconator_messages.json', 'r') as f:
                    data = json.load(f)
                print(f"🧠 Training data: {len(data)} Baconator messages loaded")
                
                # Show some example phrases
                examples = [msg['content'] for msg in data[:5]]
                print(f"📝 Example phrases: {examples}")
                
            except Exception as e:
                print(f"⚠️  Training data issue: {e}")
            
            # Check AI model availability
            try:
                import torch
                import transformers
                print(f"🤖 AI Libraries: Available (PyTorch {torch.__version__})")
            except ImportError:
                print(f"⚠️  AI Libraries: Not available (using fallback responses)")
            
            print(f"\n🎯 To test the bot:")
            print(f"1. In Discord, try: '@{client.user.name} why would you do that?'")
            print(f"2. Expected response: 'but why would you' or similar Baconator phrase")
            print(f"3. Try: '@{client.user.name} how are you?'")
            print(f"4. Expected response: 'bruh how' or 'probably'")
            
            await client.close()
        
        await client.start(token)
        
    except discord.LoginFailure:
        print("❌ Invalid Discord token!")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🔍 Checking Bot Status...")
    asyncio.run(test_bot_connection())
