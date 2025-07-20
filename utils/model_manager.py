#!/usr/bin/env python3
"""
Model Manager for Friend AI Bot
Handles loading, saving, and running the trained language model.
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GPT2LMHeadModel, 
    GPT2Tokenizer,
    pipeline
)
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages the AI language model for generating friend-like responses.
    """
    
    def __init__(self, model_name: str = "gpt2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.model_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"ModelManager initialized with device: {self.device}")
    
    def load_pretrained_model(self, model_name: str = None):
        """
        Load a pre-trained model from Hugging Face.
        
        Args:
            model_name: Name of the model to load (default: gpt2)
        """
        if model_name:
            self.model_name = model_name
        
        try:
            logger.info(f"Loading pre-trained model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Move model to device
            self.model.to(self.device)
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_full_text=False,
                do_sample=True,
                temperature=0.8,
                max_length=150,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.model_loaded = True
            logger.info(f"Successfully loaded model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load pre-trained model: {e}")
            self.model_loaded = False
    
    def load_model(self, model_path: str):
        """
        Load a fine-tuned model from local path.
        
        Args:
            model_path: Path to the saved model directory
        """
        try:
            if not os.path.exists(model_path):
                logger.warning(f"Model path not found: {model_path}")
                # Fall back to pre-trained model
                self.load_pretrained_model()
                return
            
            logger.info(f"Loading fine-tuned model from: {model_path}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Move model to device
            self.model.to(self.device)
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_full_text=False,
                do_sample=True,
                temperature=0.7,  # Lower temperature for more consistent responses
                max_length=100,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.model_loaded = True
            logger.info("Successfully loaded fine-tuned model")
            
        except Exception as e:
            logger.error(f"Failed to load fine-tuned model: {e}")
            # Fall back to pre-trained model
            logger.info("Falling back to pre-trained model")
            self.load_pretrained_model()
    
    def generate_response(self, prompt: str, max_length: int = 100) -> str:
        """
        Generate a response based on the input prompt.
        
        Args:
            prompt: Input text to generate response from
            max_length: Maximum length of generated response
            
        Returns:
            Generated response text
        """
        if not self.model_loaded or not self.generator:
            logger.warning("Model not loaded, cannot generate response")
            return ""
        
        try:
            # Clean and prepare prompt
            prompt = prompt.strip()
            if not prompt:
                return ""
            
            # Generate response
            outputs = self.generator(
                prompt,
                max_new_tokens=max_length,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            if outputs and len(outputs) > 0:
                response = outputs[0]['generated_text'].strip()
                
                # Clean up response
                response = self._clean_generated_text(response)
                
                return response
            
            return ""
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""
    
    def _clean_generated_text(self, text: str) -> str:
        """
        Clean and post-process generated text.
        
        Args:
            text: Raw generated text
            
        Returns:
            Cleaned text
        """
        # Remove any remaining prompt text
        lines = text.split('\n')
        
        # Find the first line that looks like a response
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.endswith(':'):
                # Take this line and potentially the next few
                response_lines = []
                for j in range(i, min(i + 3, len(lines))):
                    if lines[j].strip():
                        response_lines.append(lines[j].strip())
                    else:
                        break
                
                response = ' '.join(response_lines)
                
                # Limit length
                if len(response) > 200:
                    # Find last complete sentence
                    sentences = response.split('.')
                    if len(sentences) > 1:
                        response = '.'.join(sentences[:-1]) + '.'
                    else:
                        response = response[:200] + "..."
                
                return response
        
        # If no good response found, return truncated text
        if len(text) > 150:
            text = text[:150] + "..."
        
        return text
    
    def save_model(self, save_path: str):
        """
        Save the current model to disk.
        
        Args:
            save_path: Directory path to save model
        """
        if not self.model_loaded:
            logger.error("No model loaded to save")
            return False
        
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # Save model and tokenizer
            self.model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)
            
            logger.info(f"Model saved to: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def get_model_info(self) -> dict:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        info = {
            "model_name": self.model_name,
            "model_loaded": self.model_loaded,
            "device": self.device,
            "parameters": 0
        }
        
        if self.model:
            info["parameters"] = sum(p.numel() for p in self.model.parameters())
        
        return info
