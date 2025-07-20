#!/usr/bin/env python3
"""
Ollama Setup Script
Helps set up Ollama for the Discord bot.
"""

import subprocess
import sys
import os
import json
import aiohttp
import asyncio
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is already installed!")
            print(f"Version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Ollama is not installed")
    return False

def install_ollama():
    """Guide user through Ollama installation."""
    print("\n🚀 Installing Ollama...")
    print("\nPlease follow these steps:")
    print("1. Go to https://ollama.ai/download")
    print("2. Download Ollama for Windows")
    print("3. Run the installer")
    print("4. Restart your terminal/PowerShell")
    print("5. Run this script again")
    
    input("\nPress Enter when you've completed the installation...")

async def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Ollama service is running!")
                    models = data.get('models', [])
                    print(f"📦 Available models: {len(models)}")
                    for model in models:
                        print(f"   - {model['name']}")
                    return True
    except Exception:
        pass
    
    print("❌ Ollama service is not running")
    return False

def start_ollama_service():
    """Start Ollama service."""
    print("\n🔄 Starting Ollama service...")
    print("Run this command in a separate PowerShell window:")
    print("ollama serve")
    print("\nOr Ollama should start automatically after installation.")
    input("\nPress Enter when Ollama is running...")

async def pull_recommended_models():
    """Pull recommended models for the bot."""
    recommended_models = [
        "llama3.2",      # Fast and good for chat
        "gemma2:2b",     # Very fast, smaller model
        "qwen2.5:3b"     # Good balance of speed and quality
    ]
    
    print("\n🤖 Pulling recommended models...")
    print("This may take a while depending on your internet connection.")
    
    for model in recommended_models:
        print(f"\n⬇️ Pulling {model}...")
        try:
            # Use subprocess to run ollama pull
            result = subprocess.run(['ollama', 'pull', model], 
                                  capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"✅ {model} downloaded successfully!")
            else:
                print(f"❌ Failed to download {model}: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout downloading {model} - try manually later")
        except Exception as e:
            print(f"❌ Error downloading {model}: {e}")

def update_bot_config():
    """Update bot configuration for Ollama."""
    config_path = Path("config.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Update config for Ollama
    config.update({
        "ollama_model": "llama3.2",
        "response_chance": 0.4,
        "personality_mode": "baconator",
        "ollama_url": "http://localhost:11434"
    })
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Bot configuration updated for Ollama!")

def install_python_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")

async def main():
    """Main setup function."""
    print("🤖 Ollama Discord Bot Setup")
    print("=" * 40)
    
    # Check Ollama installation
    if not check_ollama_installed():
        install_ollama()
        return
    
    # Check if Ollama is running
    if not await check_ollama_running():
        start_ollama_service()
        
        # Check again after user confirms
        if not await check_ollama_running():
            print("❌ Please make sure Ollama is running and try again")
            return
    
    # Pull recommended models
    pull_choice = input("\n🤖 Do you want to download recommended AI models? (y/n): ").lower()
    if pull_choice == 'y':
        await pull_recommended_models()
    
    # Install Python dependencies
    install_python_dependencies()
    
    # Update configuration
    update_bot_config()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Make sure your Discord token is in a .env file:")
    print("   DISCORD_TOKEN=your_bot_token_here")
    print("2. Run the bot with: python ollama_bot.py")
    print("3. Test with commands like: !status")
    print("\nYour bot now has TRUE AI responses! 🚀")

if __name__ == "__main__":
    asyncio.run(main())
