#!/usr/bin/env python3
"""
Message Processor for Friend AI Bot
Handles text processing, cleaning, and preparation for training and inference.
"""

import re
import json
import logging
from typing import List, Dict, Optional
import unicodedata
import string

logger = logging.getLogger(__name__)

class MessageProcessor:
    """
    Processes Discord messages for training and response generation.
    """
    
    def __init__(self):
        # Common Discord artifacts to remove
        self.discord_patterns = [
            r'<@!?\d+>',          # User mentions
            r'<#\d+>',            # Channel mentions  
            r'<:\w+:\d+>',        # Custom emojis
            r'<a:\w+:\d+>',       # Animated emojis
            r'https?://\S+',      # URLs
            r'www\.\S+',          # URLs without protocol
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern) for pattern in self.discord_patterns]
        
        # Common words to filter out for privacy
        self.sensitive_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',     # Phone numbers
            r'\b\w+@\w+\.\w+\b',          # Email addresses
            r'\b\d{1,5}\s+\w+\s+(street|st|avenue|ave|road|rd|lane|ln)\b',  # Addresses
        ]
        
        self.sensitive_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.sensitive_patterns]
    
    def clean_message(self, text: str) -> str:
        """
        Clean a Discord message for processing.
        
        Args:
            text: Raw Discord message text
            
        Returns:
            Cleaned text suitable for training/inference
        """
        if not text:
            return ""
        
        # Remove Discord-specific formatting
        cleaned = text
        
        # Remove Discord artifacts
        for pattern in self.compiled_patterns:
            cleaned = pattern.sub('', cleaned)
        
        # Remove sensitive information
        for pattern in self.sensitive_compiled:
            cleaned = pattern.sub('[REDACTED]', cleaned)
        
        # Normalize Unicode characters
        cleaned = unicodedata.normalize('NFKD', cleaned)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def clean_response(self, text: str) -> str:
        """
        Clean generated response text.
        
        Args:
            text: Generated response text
            
        Returns:
            Cleaned response suitable for Discord
        """
        if not text:
            return ""
        
        # Remove any unwanted characters
        cleaned = text.strip()
        
        # Remove incomplete sentences at the end
        if cleaned and not cleaned[-1] in '.!?':
            # Find last complete sentence
            last_punct = max(
                cleaned.rfind('.'),
                cleaned.rfind('!'),
                cleaned.rfind('?')
            )
            
            if last_punct > len(cleaned) * 0.5:  # Only if we don't lose too much
                cleaned = cleaned[:last_punct + 1]
        
        # Limit length for Discord
        if len(cleaned) > 2000:  # Discord message limit
            cleaned = cleaned[:1997] + "..."
        
        return cleaned
    
    def filter_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Filter messages for training quality.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Filtered list of high-quality messages
        """
        filtered = []
        
        for msg in messages:
            content = msg.get('content', '')
            
            # Skip empty messages
            if not content or len(content.strip()) < 3:
                continue
            
            # Skip very long messages (probably spam)
            if len(content) > 500:
                continue
            
            # Skip messages that are mostly non-alphabetic
            alpha_chars = sum(1 for c in content if c.isalpha())
            if alpha_chars < len(content) * 0.5:
                continue
            
            # Skip messages with too many special characters
            special_chars = sum(1 for c in content if c in string.punctuation)
            if special_chars > len(content) * 0.3:
                continue
            
            # Clean the message
            cleaned_content = self.clean_message(content)
            
            # Skip if cleaning removed too much
            if len(cleaned_content) < 10:
                continue
            
            # Add cleaned message to filtered list
            filtered_msg = msg.copy()
            filtered_msg['content'] = cleaned_content
            filtered.append(filtered_msg)
        
        logger.info(f"Filtered {len(messages)} messages down to {len(filtered)} quality messages")
        return filtered
    
    def prepare_training_data(self, messages: List[Dict], friend_name: str) -> List[str]:
        """
        Prepare messages for language model training.
        
        Args:
            messages: List of cleaned message dictionaries
            friend_name: Name of the friend to train on
            
        Returns:
            List of training text samples
        """
        training_samples = []
        
        # Group messages by conversation
        conversations = self._group_by_conversation(messages)
        
        for conversation in conversations:
            # Filter to only friend's messages in context
            friend_messages = [msg for msg in conversation if msg.get('author') == friend_name]
            
            if len(friend_messages) < 2:
                continue
            
            # Create training samples with context
            for i in range(1, len(conversation)):
                current_msg = conversation[i]
                
                # Only train on friend's messages
                if current_msg.get('author') != friend_name:
                    continue
                
                # Build context from previous messages
                context = []
                for j in range(max(0, i-5), i):  # Last 5 messages as context
                    prev_msg = conversation[j]
                    author = prev_msg.get('author', 'Unknown')
                    content = prev_msg.get('content', '')
                    context.append(f"{author}: {content}")
                
                # Create training sample
                context_text = "\n".join(context)
                response = current_msg.get('content', '')
                
                training_sample = f"{context_text}\n{friend_name}: {response}"
                training_samples.append(training_sample)
        
        logger.info(f"Created {len(training_samples)} training samples")
        return training_samples
    
    def _group_by_conversation(self, messages: List[Dict]) -> List[List[Dict]]:
        """
        Group messages into conversations based on time gaps.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List of conversation groups
        """
        if not messages:
            return []
        
        conversations = []
        current_conversation = [messages[0]]
        
        for i in range(1, len(messages)):
            current_msg = messages[i]
            prev_msg = messages[i-1]
            
            # Check time gap (assuming timestamp field exists)
            time_gap = self._calculate_time_gap(prev_msg, current_msg)
            
            # If gap is more than 30 minutes, start new conversation
            if time_gap > 30 * 60:  # 30 minutes in seconds
                conversations.append(current_conversation)
                current_conversation = [current_msg]
            else:
                current_conversation.append(current_msg)
        
        # Add the last conversation
        if current_conversation:
            conversations.append(current_conversation)
        
        # Filter out very short conversations
        conversations = [conv for conv in conversations if len(conv) >= 3]
        
        return conversations
    
    def _calculate_time_gap(self, msg1: Dict, msg2: Dict) -> int:
        """
        Calculate time gap between two messages in seconds.
        
        Args:
            msg1: First message
            msg2: Second message
            
        Returns:
            Time gap in seconds
        """
        try:
            # This is a placeholder - actual implementation depends on timestamp format
            # For now, assume messages are in chronological order and return default gap
            return 60  # 1 minute default gap
        except Exception:
            return 60
    
    def extract_personality_traits(self, messages: List[Dict]) -> Dict[str, any]:
        """
        Extract personality traits from messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary of personality traits
        """
        traits = {
            "message_count": len(messages),
            "avg_message_length": 0,
            "common_words": [],
            "emoji_usage": 0,
            "exclamation_usage": 0,
            "question_usage": 0,
            "sentiment": "neutral"
        }
        
        if not messages:
            return traits
        
        total_length = 0
        word_freq = {}
        emoji_count = 0
        exclamation_count = 0
        question_count = 0
        
        for msg in messages:
            content = msg.get('content', '')
            total_length += len(content)
            
            # Count emojis (basic detection)
            emoji_count += len(re.findall(r'[😀-🙏🌀-🗿]', content))
            
            # Count punctuation
            exclamation_count += content.count('!')
            question_count += content.count('?')
            
            # Count words
            words = re.findall(r'\b\w+\b', content.lower())
            for word in words:
                if len(word) > 2:  # Ignore very short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Calculate traits
        traits["avg_message_length"] = total_length / len(messages) if messages else 0
        traits["emoji_usage"] = emoji_count / len(messages) if messages else 0
        traits["exclamation_usage"] = exclamation_count / len(messages) if messages else 0
        traits["question_usage"] = question_count / len(messages) if messages else 0
        
        # Get most common words (excluding very common ones)
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        stop_words = {'the', 'and', 'is', 'to', 'a', 'of', 'it', 'in', 'you', 'that', 'for', 'on', 'with', 'as'}
        traits["common_words"] = [word for word, count in common_words[:20] if word not in stop_words]
        
        return traits
