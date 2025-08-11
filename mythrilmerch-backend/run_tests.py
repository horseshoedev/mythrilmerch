#!/usr/bin/env python3
"""
Test runner for MythrilMerch API
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"\n⏱️  Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print(f"\n📤 STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print(f"\n⚠️  STDERR:")
        print(result.stderr)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
        return True
    else:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False

def main():
    """Main test runner"""
    print("🚀 MythrilMerch API Test Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the mythrilmerch-backend directory.")
        sys.exit(1)
    
    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    install_result = run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    )
    
    if not install_result:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Run linting (if available)
    try:
        import flake8
        run_command(
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Running linting checks"
        )
    except ImportError:
        print("⚠️  flake8 not installed, skipping linting")
    
    # Run unit tests
    unit_success = run_command(
        "python -m pytest tests/test_auth.py -v --cov=auth --cov-report=term-missing",
        "Running authentication unit tests"
    )
    
    # Run integration tests
    integration_success = run_command(
        "python -m pytest tests/test_integration.py -v --cov=app --cov-report=term-missing",
        "Running integration tests"
    )
    
    # Run all tests with coverage
    coverage_success = run_command(
        "python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=70",
        "Running all tests with coverage"
    )
    
    # Generate coverage report
    if coverage_success:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
        print(f"📊 Open the file in your browser to view detailed coverage")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Summary")
    print(f"{'='*60}")
    
    results = [
        ("Dependencies", install_result),
        ("Unit Tests", unit_success),
        ("Integration Tests", integration_success),
        ("Coverage", coverage_success)
    ]
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not result:
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests passed!")
        print("🚀 Your API is ready for production!")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 