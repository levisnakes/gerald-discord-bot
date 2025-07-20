#!/usr/bin/env python3
"""
Setup Script for Friend AI Discord Bot
Installs dependencies and sets up the environment.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """
    Run a command and return success status.
    
    Args:
        command: Command to run
        description: Description for logging
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - FAILED")
        logger.error(f"Error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - FAILED")
        logger.error(f"Error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("Python 3.8+ is required!")
        return False
    
    logger.info("✅ Python version is compatible")
    return True

def install_basic_dependencies():
    """Install basic required dependencies."""
    logger.info("Installing basic dependencies...")
    
    basic_deps = [
        "discord.py>=2.3.2",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0"
    ]
    
    success = True
    for dep in basic_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            success = False
    
    return success

def install_ml_dependencies():
    """Install ML dependencies (optional)."""
    logger.info("Installing ML dependencies...")
    logger.info("This may take a while...")
    
    # Try CPU-only PyTorch first (smaller download)
    ml_deps = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "transformers>=4.21.0",
        "datasets>=2.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0"
    ]
    
    success = True
    for dep in ml_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split()[0]}"):
            success = False
            break
    
    return success

def create_env_file():
    """Create .env file template."""
    env_path = ".env"
    
    if os.path.exists(env_path):
        logger.info("✅ .env file already exists")
        return True
    
    env_content = """# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here

# Optional: OpenAI API (if you want to use GPT models)
# OPENAI_API_KEY=your_openai_key_here

# Bot Settings
BOT_PREFIX=!
DEBUG_MODE=false
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        logger.info("✅ Created .env file template")
        logger.info("   Please edit .env and add your Discord bot token!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "data/processed", 
        "models",
        "logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_imports():
    """Test if important modules can be imported."""
    logger.info("Testing imports...")
    
    # Test basic imports
    basic_modules = {
        "discord": "discord.py",
        "dotenv": "python-dotenv", 
        "aiohttp": "aiohttp"
    }
    
    basic_success = True
    for module, package in basic_modules.items():
        try:
            __import__(module)
            logger.info(f"✅ {package} imported successfully")
        except ImportError:
            logger.error(f"❌ {package} import failed")
            basic_success = False
    
    # Test ML imports (optional)
    ml_modules = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "datasets": "Datasets"
    }
    
    ml_success = True
    for module, package in ml_modules.items():
        try:
            __import__(module)
            logger.info(f"✅ {package} imported successfully")
        except ImportError:
            logger.warning(f"⚠️  {package} not available (optional for advanced AI)")
            ml_success = False
    
    return basic_success, ml_success

def main():
    """Main setup function."""
    logger.info("🚀 Starting Friend AI Discord Bot Setup...")
    logger.info("="*60)
    
    # Check Python version
    if not check_python_version():
        logger.error("Setup aborted - incompatible Python version")
        return
    
    # Create directories
    if not create_directories():
        logger.error("Setup aborted - failed to create directories")
        return
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    logger.info("\n📦 Installing Dependencies...")
    
    # Basic dependencies (required)
    basic_success = install_basic_dependencies()
    
    if not basic_success:
        logger.error("❌ Failed to install basic dependencies")
        logger.info("Try running manually: pip install discord.py python-dotenv aiohttp")
        return
    
    # ML dependencies (optional)
    logger.info("\n🤖 Installing ML Dependencies (Optional)...")
    logger.info("This is optional but enables advanced AI features")
    
    install_ml = input("Install ML dependencies? (y/n): ").lower().strip()
    
    if install_ml in ['y', 'yes']:
        ml_success = install_ml_dependencies()
        if not ml_success:
            logger.warning("⚠️  ML dependencies installation failed")
            logger.info("The bot will work with basic features only")
    else:
        logger.info("⚠️  Skipping ML dependencies - basic features only")
    
    # Test imports
    logger.info("\n🧪 Testing Installation...")
    basic_success, ml_success = test_imports()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("🎯 Setup Summary:")
    
    if basic_success:
        logger.info("✅ Basic Dependencies: SUCCESS")
        logger.info("   - Discord bot functionality available")
    else:
        logger.info("❌ Basic Dependencies: FAILED")
        logger.info("   - Bot will not work properly")
    
    if ml_success:
        logger.info("✅ ML Dependencies: SUCCESS") 
        logger.info("   - Advanced AI features available")
    else:
        logger.info("⚠️  ML Dependencies: NOT AVAILABLE")
        logger.info("   - Basic rule-based responses only")
    
    logger.info("\n🚀 Next Steps:")
    logger.info("1. Edit .env file and add your Discord bot token")
    logger.info("2. Prepare training data: python scripts/prepare_data.py")
    logger.info("3. Train the model: python scripts/train_model.py")
    logger.info("4. Start the bot: python bot.py")
    
    logger.info("\n📚 Additional Help:")
    logger.info("- Discord bot setup: https://discord.com/developers/applications")
    logger.info("- Bot permissions: Send Messages, Read Message History")
    logger.info("- Bot token: Copy from Bot section in Discord Developer Portal")
    
    logger.info("="*60)

if __name__ == "__main__":
    main()
