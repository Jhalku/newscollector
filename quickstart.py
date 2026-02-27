#!/usr/bin/env python3
"""
Quick Start Script for News Auto Collector
Sets up environment and runs the application
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step_num, text):
    print(f"[Step {step_num}] {text}")

def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        print(f"   Your version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description} found: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT found: {filepath}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print_step(2, "Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def setup_env_file():
    """Setup .env file"""
    print_step(3, "Setting up environment variables...")
    
    if Path(".env").exists():
        print("✓ .env file already exists")
        return True
    
    if not Path(".env.example").exists():
        print("✗ .env.example not found")
        return False
    
    # Copy .env.example to .env
    with open(".env.example", "r") as src:
        with open(".env", "w") as dst:
            dst.write(src.read())
    
    print("✓ .env file created from .env.example")
    print("  → Please update .env with your Google Sheets IDs")
    return True

def check_credentials():
    """Check for Google credentials"""
    print_step(4, "Checking Google API credentials...")
    
    if Path("credentials.json").exists():
        print("✓ credentials.json found")
        return True
    
    print("⚠ credentials.json not found")
    print("  → Download from Google Cloud Console")
    print("  → Save as 'credentials.json' in project root")
    print("  → On first run, browser will open for authentication")
    return True  # Not required before first run

def main():
    """Main setup routine"""
    print_header("Bilingual News Monitoring Automation - Quick Setup")
    
    # Check Python version
    print_step(1, "Checking Python version...")
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup .env
    setup_env_file()
    
    # Check credentials
    check_credentials()
    
    # Final setup message
    print_header("Setup Complete!")
    
    print("Next steps:")
    print("1. Update .env with your Google Sheets IDs:")
    print("   - KEYWORDS_SHEET_ID")
    print("   - WEBSITES_SHEET_ID")
    print()
    print("2. Download credentials.json from Google Cloud Console:")
    print("   → Go to https://console.cloud.google.com/")
    print("   → Create OAuth 2.0 Desktop credentials")
    print("   → Save as 'credentials.json' in project root")
    print()
    print("3. Start the web application:")
    print("   python app.py")
    print()
    print("4. Open in browser:")
    print("   http://localhost:5000")
    print()
    print("For detailed setup instructions, see SETUP_GUIDE.md")
    print()

if __name__ == "__main__":
    try:
        # Change to script directory
        os.chdir(Path(__file__).parent)
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)
