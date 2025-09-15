#!/usr/bin/env python3
"""
Main entry point for the Book Request Automation System
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit application"""
    print("🚀 Starting Book Request Automation System...")
    
    # Check if required files exist
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found!")
        sys.exit(1)
    
    # Run Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")

if __name__ == "__main__":
    main()
