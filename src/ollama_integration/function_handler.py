#!/usr/bin/env python3
"""
Function handler for Open WebUI to get real-time financial data
"""
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from src.ollama_integration.financial_functions import (
        get_stock_quote, get_market_overview, get_stock_news,
        compare_stocks, get_sector_performance
    )
    
    def handle_function_call(function_name, **kwargs):
        """Handle function calls from Open WebUI"""
        functions = {
            "get_stock_quote": get_stock_quote,
            "get_market_overview": get_market_overview,
            "get_stock_news": get_stock_news,
            "compare_stocks": compare_stocks,
            "get_sector_performance": get_sector_performance
        }
        
        if function_name in functions:
            try:
                result = functions[function_name](**kwargs)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}
    
    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("Usage: python function_handler.py <function_name> [args...]")
            sys.exit(1)
        
        function_name = sys.argv[1]
        
        # Parse additional arguments as JSON if provided
        kwargs = {}
        if len(sys.argv) > 2:
            try:
                kwargs = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                # Treat as simple string argument for symbol
                kwargs = {"symbol": sys.argv[2]}
        
        result = handle_function_call(function_name, **kwargs)
        print(json.dumps(result, indent=2))

except ImportError as e:
    print(json.dumps({"success": False, "error": f"Import error: {e}"}))
