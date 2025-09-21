#!/usr/bin/env python3
"""
Test Runner for Agent Investment Platform

Comprehensive test suite runner that organizes and executes all tests
with proper reporting and configuration management.
"""

import sys
import asyncio
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_integration_tests():
    """Run integration tests for MCP servers."""
    print("🧪 Running Integration Tests...")
    return pytest.main([
        "tests/integration/", 
        "-v", 
        "--tb=short",
        "--durations=10"
    ])

def run_api_tests():
    """Run API tests (requires API keys)."""
    print("🌐 Running API Tests...")
    return pytest.main([
        "tests/api/", 
        "-v", 
        "--tb=short"
    ])

def run_unit_tests():
    """Run unit tests."""
    print("⚡ Running Unit Tests...")
    return pytest.main([
        "tests/", 
        "-v", 
        "--ignore=tests/integration",
        "--ignore=tests/api"
    ])

def run_all_tests():
    """Run all tests."""
    print("🎯 Running All Tests...")
    return pytest.main([
        "tests/", 
        "-v", 
        "--tb=short"
    ])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Investment Platform Test Runner")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.integration:
        sys.exit(run_integration_tests())
    elif args.api:
        sys.exit(run_api_tests())
    elif args.unit:
        sys.exit(run_unit_tests())
    elif args.all:
        sys.exit(run_all_tests())
    else:
        print("Please specify test type: --integration, --api, --unit, or --all")
        sys.exit(1)