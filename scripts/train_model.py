#!/usr/bin/env python3
"""
Model Training Script for Friend AI Bot
Fine-tunes a language model on friend's messages.
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required ML dependencies are available."""
    missing_deps = []
    
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
    except ImportError:
        missing_deps.append("torch")
    
    try:
        import transformers
        logger.info(f"Transformers version: {transformers.__version__}")
    except ImportError:
        missing_deps.append("transformers")
    
    try:
        import datasets
        logger.info(f"Datasets version: {datasets.__version__}")
    except ImportError:
        missing_deps.append("datasets")
    
    if missing_deps:
        logger.error(f"Missing dependencies: {missing_deps}")
        logger.info("Install with: pip install torch transformers datasets")
        return False
    
    return True

def load_training_data() -> Optional[Dict]:
    """Load processed training data."""
    data_path = "data/processed/training_data.json"
    
    if not os.path.exists(data_path):
        logger.error(f"Training data not found at {data_path}")
        logger.info("Please run: python scripts/prepare_data.py first")
        return None
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded training data for {data['friend_name']}")
        logger.info(f"Training samples: {len(data['training_samples'])}")
        return data
    except Exception as e:
        logger.error(f"Failed to load training data: {e}")
        return None

def create_simple_model():
    """Create a simple rule-based model for basic functionality."""
    logger.info("Creating simple rule-based model...")
    
    # Load training data for pattern analysis
    training_data = load_training_data()
    if not training_data:
        logger.error("Cannot create model without training data")
        return False
    
    # Extract patterns from training data
    messages = [sample.split("Response: ")[-1] for sample in training_data['training_samples'] 
                if "Response: " in sample]
    
    personality = training_data['personality_traits']
    
    # Create simple model data
    simple_model = {
        "friend_name": training_data['friend_name'],
        "model_type": "rule_based",
        "version": "1.0",
        "personality": personality,
        "common_responses": messages[:20],  # Top 20 responses
        "response_patterns": {
            "agreement": ["Yeah!", "Totally!", "I agree!", "Exactly!", "For sure!"],
            "excitement": ["That's awesome!", "So cool!", "Amazing!", "Wow!", "That's great!"],
            "questioning": ["Really?", "Wait, what?", "How so?", "Interesting...", "Tell me more!"],
            "casual": ["lol", "haha", "nice", "cool", "sweet"],
            "thinking": ["Hmm...", "I think...", "Maybe...", "Probably...", "Not sure..."]
        },
        "emoji_preferences": ["😂", "😊", "🎉", "👍", "❤️", "🤔", "😎", "🔥"],
        "fallback_responses": [
            "That's interesting!",
            "Tell me more about that",
            "I see what you mean",
            "That makes sense",
            "Hmm, interesting point"
        ]
    }
    
    # Save simple model
    os.makedirs("models", exist_ok=True)
    model_path = "models/friend_ai_simple.json"
    
    with open(model_path, 'w', encoding='utf-8') as f:
        json.dump(simple_model, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Simple model saved to {model_path}")
    return True

def train_transformer_model():
    """Train a transformer model if dependencies are available."""
    if not check_dependencies():
        logger.warning("ML dependencies not available, skipping transformer training")
        return False
    
    try:
        import torch
        from transformers import (
            AutoTokenizer, AutoModelForCausalLM, 
            TrainingArguments, Trainer, DataCollatorForLanguageModeling
        )
        from datasets import Dataset
        
        logger.info("Starting transformer model training...")
        
        # Load training data
        training_data = load_training_data()
        if not training_data:
            return False
        
        # Prepare training texts
        training_texts = training_data['training_samples']
        
        if len(training_texts) < 10:
            logger.warning(f"Only {len(training_texts)} training samples - this may not be enough for good results")
        
        # Use a small, fast model for quick training
        model_name = "microsoft/DialoGPT-small"
        logger.info(f"Loading model: {model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Tokenize training data
        def tokenize_function(examples):
            return tokenizer(
                examples['text'], 
                truncation=True, 
                padding=True, 
                max_length=512,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_dict({"text": training_texts})
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # We're doing causal LM, not masked LM
        )
        
        # Training arguments - very light training for quick results
        training_args = TrainingArguments(
            output_dir="./models/checkpoints",
            overwrite_output_dir=True,
            num_train_epochs=1,  # Just 1 epoch for quick training
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            warmup_steps=10,
            logging_steps=10,
            save_steps=50,
            eval_steps=50,
            logging_dir="./logs",
            save_total_limit=2,
            remove_unused_columns=False,
            dataloader_drop_last=True,
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_dataset,
        )
        
        # Train the model
        logger.info("Starting training...")
        trainer.train()
        
        # Save the fine-tuned model
        model_output_dir = "models/friend_ai_transformer"
        trainer.save_model(model_output_dir)
        tokenizer.save_pretrained(model_output_dir)
        
        # Save model info
        model_info = {
            "friend_name": training_data['friend_name'],
            "model_type": "transformer",
            "base_model": model_name,
            "training_samples": len(training_texts),
            "version": "1.0"
        }
        
        with open(f"{model_output_dir}/model_info.json", 'w') as f:
            json.dump(model_info, f, indent=2)
        
        logger.info(f"✅ Transformer model saved to {model_output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Transformer training failed: {e}")
        return False

def main():
    """Main training function."""
    logger.info("🚀 Starting Friend AI model training...")
    
    # Check if training data exists
    if not os.path.exists("data/processed/training_data.json"):
        logger.error("No training data found!")
        logger.info("Please run: python scripts/prepare_data.py first")
        return
    
    # Always create simple model (works without ML dependencies)
    logger.info("Creating simple rule-based model...")
    simple_success = create_simple_model()
    
    # Try to create transformer model if dependencies are available
    logger.info("Attempting to create transformer model...")
    transformer_success = train_transformer_model()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("🎯 Training Summary:")
    
    if simple_success:
        logger.info("✅ Simple rule-based model: SUCCESS")
        logger.info("   - Location: models/friend_ai_simple.json")
        logger.info("   - Features: Pattern matching, personality traits")
    else:
        logger.info("❌ Simple rule-based model: FAILED")
    
    if transformer_success:
        logger.info("✅ Transformer model: SUCCESS")
        logger.info("   - Location: models/friend_ai_transformer/")
        logger.info("   - Features: AI text generation")
    else:
        logger.info("⚠️  Transformer model: SKIPPED")
        logger.info("   - Reason: Missing ML dependencies or training failed")
        logger.info("   - Install with: pip install torch transformers datasets")
    
    logger.info("\n🚀 Next steps:")
    if simple_success or transformer_success:
        logger.info("   1. Test the bot: python bot.py")
        logger.info("   2. Set up Discord token in .env file")
        logger.info("   3. Invite bot to your Discord server")
    else:
        logger.info("   1. Fix any errors above")
        logger.info("   2. Re-run this script")
    
    logger.info("="*50)

if __name__ == "__main__":
    main()
