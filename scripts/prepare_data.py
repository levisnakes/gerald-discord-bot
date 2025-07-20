#!/usr/bin/env python3
"""
Data Preparation Script for Friend AI Bot
Processes raw Discord message data for training.
"""

import json
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.message_processor import MessageProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_discord_export(file_path: str) -> dict:
    """
    Load Discord data export file.
    
    Args:
        file_path: Path to Discord export JSON file
        
    Returns:
        Parsed Discord data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded Discord export with {len(data.get('messages', []))} messages")
        return data
    except Exception as e:
        logger.error(f"Failed to load Discord export: {e}")
        return {}

def extract_messages_from_export(discord_data: dict, friend_name: str) -> list:
    """
    Extract messages from Discord export data.
    
    Args:
        discord_data: Parsed Discord export data
        friend_name: Name of friend to extract messages for
        
    Returns:
        List of message dictionaries
    """
    messages = []
    
    # Handle different Discord export formats
    if 'messages' in discord_data:
        # Standard export format
        for msg in discord_data['messages']:
            if msg.get('author', {}).get('username') == friend_name:
                messages.append({
                    'author': friend_name,
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp', ''),
                    'channel': msg.get('channel_id', '')
                })
    
    elif isinstance(discord_data, list):
        # Simple list format
        for msg in discord_data:
            if msg.get('author') == friend_name:
                messages.append(msg)
    
    logger.info(f"Extracted {len(messages)} messages from {friend_name}")
    return messages

def create_sample_data(friend_name: str = "YourFriend") -> list:
    """
    Create sample message data for testing.
    
    Args:
        friend_name: Name of the friend
        
    Returns:
        List of sample messages
    """
    sample_messages = [
        {"author": friend_name, "content": "Hey! What's up?", "timestamp": "2024-01-01T10:00:00"},
        {"author": friend_name, "content": "lol that's hilarious 😂", "timestamp": "2024-01-01T10:05:00"},
        {"author": friend_name, "content": "I totally agree with that", "timestamp": "2024-01-01T10:10:00"},
        {"author": friend_name, "content": "Hmm, interesting point", "timestamp": "2024-01-01T10:15:00"},
        {"author": friend_name, "content": "That reminds me of this one time...", "timestamp": "2024-01-01T10:20:00"},
        {"author": friend_name, "content": "Wait, really? That's crazy!", "timestamp": "2024-01-01T10:25:00"},
        {"author": friend_name, "content": "I love that idea!", "timestamp": "2024-01-01T10:30:00"},
        {"author": friend_name, "content": "Yeah, I've been thinking about that too", "timestamp": "2024-01-01T10:35:00"},
        {"author": friend_name, "content": "Oh wow, I didn't know that", "timestamp": "2024-01-01T10:40:00"},
        {"author": friend_name, "content": "That's so cool! 🎉", "timestamp": "2024-01-01T10:45:00"},
        {"author": "SomeoneElse", "content": "What do you think about this?", "timestamp": "2024-01-01T10:46:00"},
        {"author": friend_name, "content": "I think it's pretty awesome actually", "timestamp": "2024-01-01T10:47:00"},
        {"author": "SomeoneElse", "content": "Should we do this?", "timestamp": "2024-01-01T10:48:00"},
        {"author": friend_name, "content": "Yeah definitely! Let's do it", "timestamp": "2024-01-01T10:49:00"},
        {"author": friend_name, "content": "This is going to be fun 😊", "timestamp": "2024-01-01T10:50:00"},
    ]
    
    logger.info(f"Created {len(sample_messages)} sample messages")
    return sample_messages

def main():
    """Main data preparation function."""
    logger.info("Starting data preparation...")
    
    # Configuration
    friend_name = input("Enter your friend's Discord username: ").strip()
    if not friend_name:
        friend_name = "YourFriend"
        logger.info(f"Using default friend name: {friend_name}")
    
    # Check for Discord export file
    export_path = "data/messages.json"
    
    if os.path.exists(export_path):
        logger.info(f"Found Discord export at: {export_path}")
        discord_data = load_discord_export(export_path)
        raw_messages = extract_messages_from_export(discord_data, friend_name)
    else:
        logger.warning(f"No Discord export found at {export_path}")
        logger.info("Creating sample data for testing...")
        raw_messages = create_sample_data(friend_name)
        
        # Save sample data
        os.makedirs("data", exist_ok=True)
        with open("data/messages.json", 'w', encoding='utf-8') as f:
            json.dump(raw_messages, f, indent=2, ensure_ascii=False)
        logger.info("Sample data saved to data/messages.json")
    
    if not raw_messages:
        logger.error("No messages found! Please check your Discord export or friend name.")
        return
    
    # Process messages
    processor = MessageProcessor()
    
    logger.info("Cleaning and filtering messages...")
    clean_messages = processor.filter_messages(raw_messages)
    
    if not clean_messages:
        logger.error("No clean messages after filtering!")
        return
    
    logger.info("Preparing training data...")
    training_samples = processor.prepare_training_data(clean_messages, friend_name)
    
    if not training_samples:
        logger.error("No training samples created!")
        return
    
    # Extract personality traits
    logger.info("Analyzing personality traits...")
    personality = processor.extract_personality_traits(clean_messages)
    
    # Create output directory
    os.makedirs("data/processed", exist_ok=True)
    
    # Save processed data
    output_data = {
        "friend_name": friend_name,
        "message_count": len(clean_messages),
        "training_samples": training_samples,
        "personality_traits": personality,
        "messages": clean_messages
    }
    
    with open("data/processed/training_data.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Save just the training text
    with open("data/processed/training_text.txt", 'w', encoding='utf-8') as f:
        for sample in training_samples:
            f.write(sample + "\n\n---\n\n")
    
    logger.info("✅ Data preparation completed!")
    logger.info(f"📊 Statistics:")
    logger.info(f"   - Original messages: {len(raw_messages)}")
    logger.info(f"   - Clean messages: {len(clean_messages)}")
    logger.info(f"   - Training samples: {len(training_samples)}")
    logger.info(f"   - Average message length: {personality['avg_message_length']:.1f} chars")
    logger.info(f"   - Emoji usage: {personality['emoji_usage']:.2f} per message")
    
    logger.info(f"\n🎯 Personality traits for {friend_name}:")
    logger.info(f"   - Common words: {personality['common_words'][:10]}")
    logger.info(f"   - Exclamation usage: {personality['exclamation_usage']:.2f} per message")
    logger.info(f"   - Question usage: {personality['question_usage']:.2f} per message")
    
    logger.info(f"\n📁 Files created:")
    logger.info(f"   - data/processed/training_data.json")
    logger.info(f"   - data/processed/training_text.txt")
    
    logger.info(f"\n🚀 Next steps:")
    logger.info(f"   1. Review the training data in data/processed/")
    logger.info(f"   2. Run: python scripts/train_model.py")
    logger.info(f"   3. Start the bot: python bot.py")

if __name__ == "__main__":
    main()
