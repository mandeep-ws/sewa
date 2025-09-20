#!/usr/bin/env python3
"""
SEWA Application Launcher
Handles command-line arguments and starts the Streamlit application
"""

import sys
import os
import subprocess
from modules.cli_args import parse_arguments, print_startup_info

def main():
    """Main entry point for the SEWA application"""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Print startup information
        print_startup_info(args)
        
        # Build Streamlit command
        streamlit_cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(args.port)
        ]
        
        if args.headless:
            streamlit_cmd.append("--server.headless")
            streamlit_cmd.append("true")
        
        # Add logging arguments to pass to the app
        streamlit_cmd.extend(["--", "--log-level", args.log_level])
        if args.log_file:
            streamlit_cmd.extend(["--log-file", args.log_file])
        
        print(f"🚀 Starting SEWA application...")
        print(f"📝 Command: {' '.join(streamlit_cmd)}")
        print()
        
        # Start Streamlit
        subprocess.run(streamlit_cmd)
        
    except KeyboardInterrupt:
        print("\n👋 SEWA application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting SEWA application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
