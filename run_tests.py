#!/usr/bin/env python3
"""
Test runner script for the TodoList Flask API.
"""

import sys
import subprocess
import os


def run_tests():
    """Run the test suite."""
    print("Running TodoList API tests...")

    # Set environment variables for testing
    os.environ.setdefault("FLASK_ENV", "testing")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")

    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("pip install -r requirements.txt")
        return False


def run_specific_test(test_name):
    """Run a specific test."""
    print(f"Running specific test: {test_name}")

    os.environ.setdefault("FLASK_ENV", "testing")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")

    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/test_todos.py::{test_name}",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        success = run_tests()

    sys.exit(0 if success else 1)
