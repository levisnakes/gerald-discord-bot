#!/usr/bin/env python3
"""
Bot Status Checker
Checks if the Discord bot is online and shows its status.
"""

import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check_bot_status():
    """Check if bot can connect to Discord."""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ No Discord token found in .env file!")
        return
    
    try:
        # Create minimal bot client
        intents = discord.Intents.default()
        intents.message_content = True
        
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"✅ Bot '{client.user}' is ONLINE!")
            print(f"📊 Bot ID: {client.user.id}")
            print(f"🌐 Connected to {len(client.guilds)} servers:")
            
            for guild in client.guilds:
                print(f"   - {guild.name} (ID: {guild.id})")
            
            print(f"\n🔗 Invite link:")
            print(f"https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=2048&scope=bot")
            
            await client.close()
        
        await client.start(token)
        
    except discord.LoginFailure:
        print("❌ Invalid Discord token!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_bot_status())
