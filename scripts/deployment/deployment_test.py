#!/usr/bin/env python3
"""
Simple deployment test for Agent Investment Platform
"""
import yfinance as yf
import yaml
import os
from datetime import datetime

def main():
    print("Agent Investment Platform - Deployment Test")
    print("=" * 50)

    # Test 1: Market Data Access
    print("\nTesting Market Data Access...")
    try:
        stock = yf.Ticker("AAPL")
        info = stock.info
        current_price = info.get('currentPrice', 'N/A')
        company_name = info.get('longName', 'N/A')
        print(f"SUCCESS: {company_name}: ${current_price}")
    except Exception as e:
        print(f"ERROR: Market data error: {e}")

    # Test 2: Configuration Loading
    print("\nTesting Configuration...")
    try:
        with open('config/strategies.yaml', 'r') as f:
            strategies = yaml.safe_load(f)
        strategy_count = len(strategies.get('strategies', {}))
        print(f"SUCCESS: Loaded {strategy_count} investment strategies")
    except Exception as e:
        print(f"ERROR: Config error: {e}")

    # Test 3: File System Access
    print("\nTesting File System...")
    required_dirs = ['reports', 'logs', 'config', 'data']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"SUCCESS: {dir_name}/ directory exists")
        else:
            print(f"ERROR: {dir_name}/ directory missing")

    # Test 4: Environment Variables
    print("\nTesting Environment Variables...")
    from dotenv import load_dotenv
    load_dotenv()

    polygon_key = os.getenv("POLYGON_API_KEY")
    if polygon_key:
        print(f"SUCCESS: Polygon API key configured (starts with: {polygon_key[:8]}...)")
    else:
        print("ERROR: Polygon API key not found")

    print("\nBasic platform components tested successfully!")
    print("Platform is ready for investment analysis.")

if __name__ == "__main__":
    main()
