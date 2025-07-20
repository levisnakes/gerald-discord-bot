# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a Discord bot project with a custom language model trained on friend's messages. Key components:

## Project Focus
- Discord bot using discord.py
- Custom language model training with Hugging Face Transformers
- Message data processing and fine-tuning
- Free AI/ML solutions (no paid APIs)

## Technologies Used
- **Discord.py** - Discord bot framework
- **Hugging Face Transformers** - Pre-trained language models
- **PyTorch** - Deep learning framework
- **Datasets** - Data processing library
- **Tokenizers** - Text tokenization

## Code Guidelines
- Use async/await for Discord bot commands
- Implement proper error handling for API calls
- Create modular code structure (bot, training, data processing)
- Use environment variables for sensitive data (Discord tokens)
- Implement message filtering and preprocessing
- Add logging for training progress and bot operations

## Free AI Approach
- Use pre-trained models from Hugging Face Hub
- Fine-tune smaller models (GPT-2, DistilBERT) that can run locally
- Implement efficient training with gradient accumulation
- Use free GPU resources (Colab, Kaggle) for training if needed
- Cache model outputs to reduce computation

## Data Privacy
- Implement consent mechanisms for message collection
- Anonymize personal information in training data
- Provide data deletion capabilities
- Follow Discord ToS for message usage
