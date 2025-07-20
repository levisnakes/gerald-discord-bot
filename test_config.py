#!/usr/bin/env python3
"""
Test the config loading to make sure it handles missing keys properly
"""

import json
import os

def test_config_loading():
    """Test the config loading logic."""
    
    # Default configuration
    default_config = {
        "response_chance": 0.25,
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
            config = {**default_config, **loaded_config}
    except FileNotFoundError:
        config = default_config
    
    # Ensure all required keys exist (in case config is outdated)
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    print("Current config:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Test the problematic key
    ollama_model = config.get("ollama_model", "gemma2:2b")
    print(f"\nOllama model: {ollama_model}")
    
    # Save updated config
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Config test completed successfully!")

if __name__ == "__main__":
    test_config_loading()
