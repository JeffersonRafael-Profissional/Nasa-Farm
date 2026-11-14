"""
Smart Rotation Engine - Main Application Entrypoint.
NASA Space Apps Challenge 2026: Field Shift - Adapting Farms with NASA Data.
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Smart Rotation Engine - NASA Space Apps 2026")
    parser.add_argument("--cli", action="store_true", help="Run terminal CLI analysis and exit")
    parser.add_argument("--port", type=int, default=8000, help="Web dashboard server port (default: 8000)")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    args = parser.parse_args()

    if args.test:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    if args.cli:
        from scripts.run_analysis_cli import run_cli
        run_cli()
    else:
        from src.web.server import start_server
        start_server(port=args.port)

if __name__ == "__main__":
    main()
