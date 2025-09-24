#!/usr/bin/env python3
"""
Simple command-line tool to get real-time financial data for Ollama chats
Usage: python financial_data_tool.py [command] [arguments]
"""

import sys
from pathlib import Path
import argparse

# Add the financial functions to the path
sys.path.append(str(Path(__file__).parent))

from financial_functions import (
    get_stock_quote, get_market_overview, get_stock_news,
    compare_stocks, get_sector_performance
)

def main():
    parser = argparse.ArgumentParser(
        description="Real-time Financial Data Tool for Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python financial_data_tool.py quote AAPL              # Get Apple stock quote
  python financial_data_tool.py market                  # Get market overview
  python financial_data_tool.py news TSLA               # Get Tesla news
  python financial_data_tool.py compare AAPL,GOOGL,MSFT # Compare stocks
  python financial_data_tool.py sectors                 # Get sector performance
        """
    )

    parser.add_argument("command", choices=["quote", "market", "news", "compare", "sectors"],
                       help="Command to execute")
    parser.add_argument("symbol", nargs="?", help="Stock symbol or comma-separated symbols")

    args = parser.parse_args()

    try:
        if args.command == "quote":
            if not args.symbol:
                print("Error: Stock symbol required for quote command")
                return
            result = get_stock_quote(args.symbol)

        elif args.command == "market":
            result = get_market_overview()

        elif args.command == "news":
            if not args.symbol:
                print("Error: Stock symbol required for news command")
                return
            result = get_stock_news(args.symbol)

        elif args.command == "compare":
            if not args.symbol:
                print("Error: Comma-separated symbols required for compare command")
                return
            result = compare_stocks(args.symbol)

        elif args.command == "sectors":
            result = get_sector_performance()

        print(result)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
