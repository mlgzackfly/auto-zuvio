#!/usr/bin/env python3
"""
Test runner script for Zuvio Auto Check-in System
"""

import sys
import os
import subprocess
import argparse


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run tests for Zuvio Auto Check-in System')
    parser.add_argument('--type', choices=['unit', 'integration', 'all'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--fast', action='store_true', 
                       help='Skip slow tests')
    
    args = parser.parse_args()
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("Consider activating your virtual environment first")
    
    success = True
    
    # Base pytest command
    pytest_cmd = "pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.coverage:
        pytest_cmd += " --cov=main --cov-report=html --cov-report=term"
    
    if args.fast:
        pytest_cmd += " -m 'not slow'"
    
    # Run tests based on type
    if args.type == 'unit':
        pytest_cmd += " -m unit"
    elif args.type == 'integration':
        pytest_cmd += " -m integration"
    
    # Run the tests
    if not run_command(pytest_cmd, f"Running {args.type} tests"):
        success = False
    
    # Run linting if all tests passed
    if success and args.type == 'all':
        lint_commands = [
            ("flake8 . --max-line-length=127 --exclude=.venv", "Code linting with flake8"),
            ("black --check .", "Code formatting check with black"),
            ("isort --check-only .", "Import sorting check with isort")
        ]
        
        for cmd, desc in lint_commands:
            if not run_command(cmd, desc):
                success = False
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All checks passed!")
        print("Your code is ready for commit.")
    else:
        print("❌ Some checks failed!")
        print("Please fix the issues before committing.")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
