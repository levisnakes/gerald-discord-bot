# Gerald Discord Bot

Gerald is an angry British Discord bot with AI-powered responses and a vocabulary learning system. He only uses words that have been said in conversations, creating a unique and authentic speaking style.

## Features

- 🤖 **AI-Powered Responses**: Uses Ollama AI (gemma2:2b model) for contextual responses
- 🎓 **Vocabulary Learning**: Only uses words learned from user conversations
- �🇧 **British Personality**: Angry British character with authentic slang
- 💬 **Context Awareness**: Maintains conversation history and responds appropriately
- �️ **Anti-Loop Protection**: Prevents self-responses and repetitive behavior
- 🎯 **Smart Response Logic**: Responds to mentions, questions, and trigger words
- � **Word Frequency Tracking**: Learns which words are used most often
- 🚀 **Easy Commands**: Built-in commands for testing and vocabulary management

## Quick Start

### 1. Setup Environment
```bash
# Run the setup script
python setup.py
```

### 2. Get Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Edit `.env` file and add your token:
```
DISCORD_TOKEN=your_bot_token_here
```

### 3. Prepare Training Data
```bash
# This will create sample data or use your Discord export
python scripts/prepare_data.py
```

### 4. Train the Model
```bash
# Creates both simple and AI models
python scripts/train_model.py
```

### 5. Start the Bot
```bash
python bot.py
```

## Project Structure

```
discord botv1/
├── bot.py                 # Main bot file
├── setup.py              # Setup and installation script
├── requirements.txt      # Dependencies
├── .env                  # Bot configuration (create this)
├── utils/
│   ├── __init__.py
│   ├── model_manager.py  # AI model handling
│   └── message_processor.py # Text processing
├── scripts/
│   ├── prepare_data.py   # Data preparation
│   └── train_model.py    # Model training
├── data/
│   ├── messages.json     # Raw message data
│   └── processed/        # Processed training data
└── models/               # Trained models
```

## How It Works

### 1. Data Collection
- Import Discord message history (JSON export)
- Or use sample data for testing
- Filter and clean messages

### 2. Text Processing
- Remove Discord artifacts (@mentions, #channels)
- Clean and normalize text
- Extract conversation patterns

### 3. Model Training
- **Simple Mode**: Rule-based responses using patterns
- **AI Mode**: Fine-tune language model on messages
- Extract personality traits and speaking style

### 4. Response Generation
- Analyze incoming messages for context
- Generate responses matching friend's style
- Include appropriate emojis and reactions

## Requirements

### Basic Requirements (Required)
- Python 3.8+
- discord.py
- python-dotenv
- aiohttp

### ML Requirements (Optional - for advanced AI)
- PyTorch
- Transformers (Hugging Face)
- Datasets
- NumPy, Pandas

## Installation Options

### Option 1: Automatic Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Installation
```bash
# Install basic dependencies
pip install discord.py python-dotenv aiohttp

# Install ML dependencies (optional)
pip install torch transformers datasets numpy pandas

# Or install everything
pip install -r requirements.txt
```

## Usage

### Bot Commands
- Bot responds automatically to messages
- No special commands needed
- Natural conversation flow

### Training with Real Data
1. Export Discord messages:
   - Use Discord data export tools
   - Save as `data/messages.json`
   - Format: List of message objects with author, content, timestamp

2. Run data preparation:
   ```bash
   python scripts/prepare_data.py
   ```

3. Train model:
   ```bash
   python scripts/train_model.py
   ```

### Example Message Format
```json
[
  {
    "author": "YourFriend",
    "content": "Hey! What's up?",
    "timestamp": "2024-01-01T10:00:00"
  }
]
```

## Configuration

### Environment Variables (.env)
```bash
# Required
DISCORD_TOKEN=your_bot_token_here

# Optional
BOT_PREFIX=!
DEBUG_MODE=false
```

### Model Settings
- Models are saved in `models/` directory
- Simple model: `friend_ai_simple.json`
- AI model: `friend_ai_transformer/`

## Features in Detail

### Simple Rule-Based Model
- Works without ML dependencies
- Uses pattern matching and templates
- Personality trait analysis
- Common response phrases
- Emoji preferences

### Advanced AI Model
- Fine-tuned transformer model
- Context-aware responses
- Natural language generation
- Better conversation flow

### Privacy & Security
- All data processing is local
- No external API calls required
- Messages are processed anonymously
- Sensitive data is filtered out

## Troubleshooting

### Common Issues

1. **Bot Token Issues**
   - Make sure token is correct in `.env`
   - Check bot permissions in Discord
   - Ensure bot is invited to server

2. **Import Errors**
   - Run `python setup.py` to install dependencies
   - Check Python version (3.8+ required)

3. **Training Data Issues**
   - Ensure message format is correct
   - Check for sufficient message count
   - Verify friend name matches exactly

4. **ML Dependencies**
   - PyTorch installation can be slow
   - Use CPU version for faster setup
   - Simple model works without ML libs

### Getting Help
- Check the logs in `logs/` directory
- Run with DEBUG_MODE=true for verbose output
- Ensure all requirements are installed

## Development

### Adding Features
1. Modify `bot.py` for new bot commands
2. Update `utils/model_manager.py` for AI improvements
3. Extend `utils/message_processor.py` for text processing

### Testing
- Use sample data for testing
- Test with different friend personalities
- Try various conversation patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. Respect Discord's Terms of Service and your friends' privacy.

## Disclaimer

- Only use with permission from friends
- Respect privacy and consent
- Don't use for harassment or spam
- Follow Discord community guidelines

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs
3. Test with sample data first
4. Ensure all dependencies are installed

---

**Happy chatting with your AI friend! 🤖💬**

# Or use free GPU on Google Colab
# Upload the colab notebook provided
```

### 5. Run the Bot
```bash
python bot.py
```

## Project Structure

```
discord-friend-ai-bot/
├── bot.py                 # Main Discord bot
├── scripts/
│   ├── prepare_data.py    # Message data preprocessing
│   ├── train_model.py     # Model training script
│   └── export_messages.py # Discord message export helper
├── models/
│   └── friend_model/      # Trained model files
├── data/
│   ├── messages.json      # Raw message data
│   └── processed/         # Processed training data
├── utils/
│   ├── message_processor.py # Text processing utilities
│   └── model_manager.py   # Model loading/saving
└── requirements.txt
```

## Training Your Model

### Option 1: Local Training (Free, Slower)
- Uses your computer's CPU/GPU
- Good for smaller datasets
- Takes longer but completely free

### Option 2: Free Cloud Training
- **Google Colab** - Free GPU for 12 hours
- **Kaggle Notebooks** - Free GPU for 30 hours/week
- **Hugging Face Spaces** - Free community GPU access

## Commands

Once the bot is running:

- `/chat <message>` - Chat with your friend's AI
- `/retrain` - Retrain model with new data
- `/personality` - Show learned personality traits
- `/help` - Show all commands

## Privacy & Ethics

⚠️ **Important Guidelines:**
- Only train on messages with explicit consent
- Don't use for impersonation or deception
- Respect Discord's Terms of Service
- Consider anonymizing personal information

## Troubleshooting

### Common Issues:
1. **Bot not responding** - Check token and permissions
2. **Training fails** - Reduce batch size or use smaller model
3. **Memory errors** - Use gradient accumulation or cloud training

### Free Resources:
- [Hugging Face Free Models](https://huggingface.co/models)
- [Google Colab](https://colab.research.google.com/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)

## Advanced Features

🎯 **Context Awareness**
- Remembers conversation history
- Responds based on channel/user context
- Learns from ongoing conversations

🎨 **Personality Customization**
- Adjust response randomness
- Filter inappropriate content
- Fine-tune personality traits

📊 **Analytics**
- Track model performance
- Monitor response quality
- Conversation statistics

---

**Made with ❤️ and free AI tools!**
