"""
Command-line argument parser for the SEWA application.
Handles logging configuration and other runtime options.
"""

import argparse
import sys
import os

def parse_arguments():
    """
    Parse command-line arguments for the SEWA application
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="SEWA - SMS and WhatsApp Message Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  streamlit run app.py -- --log-level DEBUG
  streamlit run app.py -- --log-level INFO --log-file logs/sewa.log
  streamlit run app.py -- --log-level WARNING
        """
    )
    
    # Logging arguments
    logging_group = parser.add_argument_group('Logging Options')
    
    logging_group.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    logging_group.add_argument(
        '--log-file',
        type=str,
        default=None,
        help='Log file path (default: console only)'
    )
    
    logging_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress all console output (ERROR level only)'
    )
    
    # Application arguments
    app_group = parser.add_argument_group('Application Options')
    
    app_group.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Streamlit server port (default: 8501)'
    )
    
    app_group.add_argument(
        '--headless',
        action='store_true',
        help='Run Streamlit in headless mode'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle quiet mode
    if args.quiet:
        args.log_level = 'ERROR'
    
    # Set default log file if not specified
    if args.log_file is None:
        # Create logs directory and set default log file
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = os.path.join(logs_dir, f"sewa_{timestamp}.log")
    
    return args

def setup_logging_from_args(args):
    """
    Setup logging based on parsed arguments
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        logging.Logger: Configured logger instance
    """
    from modules.logger_config import setup_logging
    
    return setup_logging(
        log_level=args.log_level,
        log_file=args.log_file
    )

def print_startup_info(args):
    """Print application startup information"""
    print("=" * 60)
    print("🚀 SEWA - SMS and WhatsApp Message Management System")
    print("=" * 60)
    print(f"📊 Log Level: {args.log_level}")
    print(f"📁 Log File: {args.log_file}")
    print(f"🌐 Server Port: {args.port}")
    print(f"🖥️  Headless Mode: {'Yes' if args.headless else 'No'}")
    print("=" * 60)
    print()
