"""
Main entry point for the PumpAndDump application.
Delegates to Analyse/main.py for cryptocurrency analysis.
"""
import sys
import os
import argparse

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PumpAndDump application')
    parser.add_argument('cmd', choices=['analyze', 'report'], help='Command to execute')
    parser.add_argument('symbols', nargs='*', help='Cryptocurrency symbol(s) to analyze')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # Get the absolute path to Analyse/main.py
    main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Analyse/main.py")
    # Execute Analyse/main.py with the correct arguments
    # Build argument list
    cmd_list = ["python3", main_path, args.cmd] + args.symbols
    if args.verbose:
        cmd_list.append('--verbose')
    os.execvp("python3", cmd_list)
