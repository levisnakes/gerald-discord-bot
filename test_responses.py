#!/usr/bin/env python3
"""
Test the new Ollama responses to make sure they're not repetitive
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ollama_manager import OllamaManager

async def test_responses():
    """Test if Ollama gives varied responses."""
    print("Testing Ollama responses...")
    
    ollama = OllamaManager()
    await ollama.initialize()
    
    if not ollama.available:
        print("❌ Ollama not available")
        return
    
    test_messages = [
        "what even are you forming a sentence?",
        "how are you doing today?",
        "what's up?",
        "do you like pizza?",
        "tell me a joke"
    ]
    
    print("Testing responses:")
    for i, msg in enumerate(test_messages):
        print(f"\n--- Test {i+1}: '{msg}' ---")
        
        for attempt in range(3):
            response = await ollama.generate_response(msg, "", "")
            print(f"Attempt {attempt+1}: {response}")
        
    await ollama.close()

if __name__ == "__main__":
    asyncio.run(test_responses())
