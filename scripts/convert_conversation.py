#!/usr/bin/env python3
"""
Conversation Data Converter
Converts raw conversation text into training format.
"""

import json
import re
from datetime import datetime

def parse_conversation_text(text: str, friend_name: str) -> list:
    """
    Parse conversation text into message format.
    
    Supports formats like:
    - "Friend: message text"
    - "YourName: message text" 
    - Or just raw messages
    """
    messages = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try to parse "Name: message" format
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                author = parts[0].strip()
                content = parts[1].strip()
                
                # Only keep friend's messages
                if author.lower() == friend_name.lower():
                    messages.append({
                        "author": friend_name,
                        "content": content,
                        "timestamp": datetime.now().isoformat()
                    })
        else:
            # Assume it's a friend message if no format specified
            messages.append({
                "author": friend_name,
                "content": line,
                "timestamp": datetime.now().isoformat()
            })
    
    return messages

def save_conversation_data(messages: list, filename: str = "data/messages.json"):
    """Save messages to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(messages)} messages to {filename}")

if __name__ == "__main__":
    print("Conversation Data Converter")
    print("=" * 40)
    
    friend_name = input("Enter your friend's name: ").strip()
    if not friend_name:
        friend_name = "Friend"
    
    print(f"\nPaste your conversation below.")
    print("Supported formats:")
    print("- 'Friend: message text'")
    print("- Just the friend's messages (one per line)")
    print("Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done:")
    print()
    
    # Read multi-line input
    conversation_lines = []
    try:
        while True:
            line = input()
            conversation_lines.append(line)
    except EOFError:
        pass
    
    conversation_text = '\n'.join(conversation_lines)
    
    if conversation_text.strip():
        messages = parse_conversation_text(conversation_text, friend_name)
        
        if messages:
            save_conversation_data(messages)
            print(f"\n🚀 Next steps:")
            print("1. Run: python scripts/prepare_data.py")
            print("2. Run: python scripts/train_model.py")
            print("3. Restart Gerald to use the new training data")
        else:
            print("❌ No messages found. Check the format and try again.")
    else:
        print("❌ No conversation data provided.")
