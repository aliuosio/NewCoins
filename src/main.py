"""
Main entry point for the PumpAndDump application.
Delegates to Analyse/main.py for cryptocurrency analysis.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # Get the absolute path to Analyse/main.py
    main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Analyse/main.py")
    # Execute Analyse/main.py with the same arguments using python3
    os.execvp("python3", ["python3", main_path] + sys.argv[1:])
