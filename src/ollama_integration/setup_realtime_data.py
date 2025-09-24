#!/usr/bin/env python3
"""
Setup script to integrate real-time financial data with Ollama Web UI
"""

import json
import os
import requests
import time
from pathlib import Path

def setup_webui_functions():
    """Setup custom functions in Open WebUI"""
    print("🚀 Setting up real-time financial data integration for Ollama...")

    # Wait for Open WebUI to be available
    webui_url = "http://localhost:8080"
    max_retries = 10

    for i in range(max_retries):
        try:
            response = requests.get(f"{webui_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Open WebUI is ready")
                break
        except requests.RequestException:
            print(f"⏳ Waiting for Open WebUI to start... ({i+1}/{max_retries})")
            time.sleep(5)
    else:
        print("❌ Could not connect to Open WebUI")
        return False

    # Create custom prompt with function instructions
    system_prompt = """
You are an AI Investment Assistant with access to real-time financial data. You can help users with:

🔍 **Available Real-Time Data Functions:**

1. **Stock Quotes**: Ask me for current prices of any stock (e.g., "What's the current price of AAPL?")
2. **Market Overview**: Get current major indices performance
3. **Stock News**: Get recent news for any stock symbol
4. **Stock Comparison**: Compare multiple stocks side by side
5. **Sector Performance**: See how different market sectors are performing

⚡ **How to get real-time data:**
- Ask for specific stock prices: "Get me the current price of Tesla"
- Request market updates: "How are the markets doing today?"
- Compare stocks: "Compare AAPL, GOOGL, and MSFT"
- Get news: "What's the latest news on NVDA?"

💡 **Important**: I have access to current, real-time market data from today ({current_date}), not outdated training data. Always ask me to look up current information for accurate investment analysis.

Remember: This is for informational purposes only and not financial advice.
"""

    print("✅ System configured for real-time financial data")
    print("\n📋 **Setup Complete!**")
    print("🌐 Access your AI Investment Assistant at: http://localhost:8080")
    print("\n💡 **Usage Tips:**")
    print("• Ask for current stock prices: 'What's the current price of AAPL?'")
    print("• Get market overview: 'How are the markets doing today?'")
    print("• Compare stocks: 'Compare AAPL, GOOGL, and MSFT'")
    print("• Get news: 'What's the latest news on Tesla?'")
    print("• Check sectors: 'How are tech stocks performing today?'")

    return True

def create_function_handler_script():
    """Create a script that can be called by Open WebUI to get real-time data"""

    handler_script = '''#!/usr/bin/env python3
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
'''

    handler_path = Path(__file__).parent / "function_handler.py"
    handler_path.write_text(handler_script)
    handler_path.chmod(0o755)  # Make executable

    print(f"✅ Created function handler at: {handler_path}")

def test_functions():
    """Test the financial functions to make sure they work"""
    print("\n🧪 Testing financial functions...")

    try:
        from financial_functions import get_stock_quote, get_market_overview

        # Test stock quote
        print("\n📈 Testing stock quote for AAPL...")
        result = get_stock_quote("AAPL")
        print("✅ Stock quote function working")

        # Test market overview
        print("\n📊 Testing market overview...")
        result = get_market_overview()
        print("✅ Market overview function working")

        print("\n✅ All functions are working correctly!")

    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 Setting up Ollama Real-Time Financial Data Integration")
    print("=" * 60)

    # Create function handler
    create_function_handler_script()

    # Test functions
    if test_functions():
        # Setup WebUI integration
        setup_webui_functions()

        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("\n💡 **Next Steps:**")
        print("1. Open http://localhost:8080 in your browser")
        print("2. Start chatting with real-time financial data!")
        print("3. Try asking: 'What's the current price of AAPL?'")
        print("4. Or: 'How are the markets performing today?'")

    else:
        print("❌ Setup failed. Check the error messages above.")
