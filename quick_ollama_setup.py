#!/usr/bin/env python3
"""
Quick Ollama Check and Setup
Simple script to get Ollama running for your Discord bot.
"""

import subprocess
import sys
import os
import time

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✅ Ollama is installed!")
            print(f"Version: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    
    print("❌ Ollama is not installed")
    return False

def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("✅ Ollama service is running!")
            models = data.get('models', [])
            print(f"Available models: {len(models)}")
            for model in models:
                print(f"  - {model['name']}")
            return True
    except Exception:
        pass
    
    print("❌ Ollama service is not running")
    return False

def install_ollama():
    """Guide user through Ollama installation."""
    print("\n🚀 To install Ollama:")
    print("1. Go to: https://ollama.ai/download")
    print("2. Download Ollama for Windows")
    print("3. Run the installer")
    print("4. Restart PowerShell/Terminal")
    print("\nOr use winget:")
    print("winget install Ollama.Ollama")

def start_ollama():
    """Start Ollama service."""
    print("\n🔄 To start Ollama:")
    print("1. Open a new PowerShell window")
    print("2. Run: ollama serve")
    print("3. Keep that window open")
    print("\nOr Ollama should auto-start after installation.")

def pull_model():
    """Pull a lightweight model."""
    print("\n📦 To download a fast AI model:")
    print("1. In PowerShell, run: ollama pull gemma2:2b")
    print("2. This downloads a 1.6GB model (fast and good)")
    print("3. Wait for download to complete")
    
    choice = input("\nDo you want me to try pulling the model now? (y/n): ").lower()
    if choice == 'y':
        try:
            print("Downloading gemma2:2b model...")
            result = subprocess.run(['ollama', 'pull', 'gemma2:2b'], 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Model downloaded successfully!")
            else:
                print(f"❌ Error: {result.stderr}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🤖 Ollama Quick Setup for Discord Bot")
    print("=" * 40)
    
    # Check installation
    if not check_ollama_installed():
        install_ollama()
        print("\nRun this script again after installation.")
        return
    
    # Check if running
    if not check_ollama_running():
        start_ollama()
        
        # Wait and check again
        print("\nWaiting for Ollama to start...")
        time.sleep(3)
        
        if not check_ollama_running():
            print("\nPlease start Ollama manually and run this script again.")
            return
    
    # Check for models
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        data = response.json()
        models = data.get('models', [])
        
        if not models:
            print("\n📦 No models found!")
            pull_model()
        else:
            print(f"\n✅ You have {len(models)} model(s) ready!")
    except:
        pass
    
    print("\n🎉 Setup complete!")
    print("Your Discord bot can now use AI responses!")
    print("Run: python ollama_bot.py")

if __name__ == "__main__":
    main()
