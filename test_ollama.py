#!/usr/bin/env python3
"""
Test Ollama Connection
Simple script to test if Ollama AI is working.
"""

import requests
import json

def test_ollama():
    """Test Ollama connection and generate a response."""
    print("Testing Ollama connection...")
    
    try:
        # Test connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print(f"Connection status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"Available models: {len(models)}")
            for model in models:
                print(f"  - {model['name']}")
            
            # Test AI generation
            print("\nTesting AI generation...")
            prompt = {
                "model": "gemma2:2b",
                "prompt": "Respond like Baconator with a casual phrase like 'bruh' or 'probably'. Keep it very short.",
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "max_tokens": 20
                }
            }
            
            ai_response = requests.post("http://localhost:11434/api/generate", json=prompt, timeout=30)
            
            if ai_response.status_code == 200:
                result = ai_response.json()
                ai_text = result.get("response", "").strip()
                print(f"AI Response: '{ai_text}'")
                print("\n✅ Ollama AI is working perfectly!")
                return True
            else:
                print(f"AI generation failed: {ai_response.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    test_ollama()
