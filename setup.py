"""
Setup script for NLP Resume Analyzer
Handles installation and initial configuration.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("NLP Resume Analyzer Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version}")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install requirements. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("Warning: spaCy model download failed. The application will use a basic model.")
    
    # Create necessary directories
    dirs_to_create = [
        "uploads",
        "data/sample_resumes",
        "data/job_descriptions",
        "logs"
    ]
    
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    print("\n" + "=" * 40)
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Activate your virtual environment (if using one)")
    print("2. Navigate to the src/web_app directory")
    print("3. Run: python app.py")
    print("4. Open your browser to http://localhost:5000")
    print("\nFor development:")
    print("- Run tests with: python -m pytest tests/")
    print("- Check code quality with: flake8 src/")


if __name__ == "__main__":
    main()
