#!/usr/bin/env python3
"""
MCP Server Test Framework for the Agent Investment Platform.

This script provides comprehensive testing capabilities for all MCP servers
including functionality, performance, and integration testing.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.mcp_servers.stock_data_server import StockDataServer
from src.mcp_servers.analysis_engine_server import AnalysisEngineServer
from src.mcp_servers.report_generator_server import ReportGeneratorServer


class MCPServerTester:
    """Comprehensive testing framework for MCP servers."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def test_all_servers(self):
        """Test all MCP servers."""
        self.logger.info("Starting comprehensive MCP server testing...")

        # Test individual servers
        await self.test_stock_data_server()
        await self.test_analysis_engine_server()
        await self.test_report_generator_server()

        # Generate test report
        self.generate_test_report()

        return self.results

    async def test_stock_data_server(self):
        """Test Stock Data Server functionality."""
        self.logger.info("Testing Stock Data Server...")

        server = StockDataServer()
        test_results = {
            "server": "Stock Data Server",
            "tests": []
        }

        # Test health check
        try:
            health = await server.health_check()
            test_results["tests"].append({
                "test": "Health Check",
                "status": "PASS" if health.get("status") == "healthy" else "FAIL",
                "details": health
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Health Check",
                "status": "FAIL",
                "error": str(e)
            })

        # Test tool registration
        try:
            tools_count = len(server.tools)
            test_results["tests"].append({
                "test": "Tool Registration",
                "status": "PASS" if tools_count > 0 else "FAIL",
                "details": f"Registered {tools_count} tools"
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Tool Registration",
                "status": "FAIL",
                "error": str(e)
            })

        # Test mock stock quote (without API key)
        try:
            # This would fail without API key, but tests the validation
            params = {"symbol": "AAPL"}
            result = await server._handle_get_stock_quote(params)
            test_results["tests"].append({
                "test": "Stock Quote Handler",
                "status": "UNEXPECTED_PASS",
                "details": "Should fail without API key"
            })
        except Exception as e:
            if "API key not configured" in str(e):
                test_results["tests"].append({
                    "test": "Stock Quote Handler",
                    "status": "PASS",
                    "details": "Correctly validates API key requirement"
                })
            else:
                test_results["tests"].append({
                    "test": "Stock Quote Handler",
                    "status": "FAIL",
                    "error": str(e)
                })

        self.results.append(test_results)

    async def test_analysis_engine_server(self):
        """Test Analysis Engine Server functionality."""
        self.logger.info("Testing Analysis Engine Server...")

        server = AnalysisEngineServer()
        test_results = {
            "server": "Analysis Engine Server",
            "tests": []
        }

        # Test health check
        try:
            health = await server.health_check()
            test_results["tests"].append({
                "test": "Health Check",
                "status": "PASS" if health.get("status") == "healthy" else "FAIL",
                "details": health
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Health Check",
                "status": "FAIL",
                "error": str(e)
            })

        # Test database initialization
        try:
            db_exists = server.db_path.exists()
            test_results["tests"].append({
                "test": "Database Initialization",
                "status": "PASS" if db_exists else "FAIL",
                "details": f"Database path: {server.db_path}"
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Database Initialization",
                "status": "FAIL",
                "error": str(e)
            })

        # Test technical analysis with mock data
        try:
            params = {
                "symbol": "TEST",
                "prices": [100, 101, 102, 101, 103, 104, 103, 105, 106, 105,
                          107, 108, 107, 109, 110, 109, 111, 112, 111, 113],
                "indicators": ["sma", "rsi"]
            }
            result = await server._handle_technical_analysis(params)
            test_results["tests"].append({
                "test": "Technical Analysis",
                "status": "PASS" if result.get("success") else "FAIL",
                "details": f"Analyzed {len(params['prices'])} price points"
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Technical Analysis",
                "status": "FAIL",
                "error": str(e)
            })

        # Test risk assessment with mock data
        try:
            params = {
                "symbol": "TEST",
                "returns": [0.01, -0.02, 0.015, -0.01, 0.02, -0.015, 0.01, 0.005,
                           -0.01, 0.02, -0.005, 0.01, -0.02, 0.015, -0.01] * 3,
                "risk_free_rate": 0.02
            }
            result = await server._handle_risk_assessment(params)
            test_results["tests"].append({
                "test": "Risk Assessment",
                "status": "PASS" if result.get("success") else "FAIL",
                "details": f"Analyzed {len(params['returns'])} return observations"
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Risk Assessment",
                "status": "FAIL",
                "error": str(e)
            })

        self.results.append(test_results)

    async def test_report_generator_server(self):
        """Test Report Generator Server functionality."""
        self.logger.info("Testing Report Generator Server...")

        server = ReportGeneratorServer()
        test_results = {
            "server": "Report Generator Server",
            "tests": []
        }

        # Test health check
        try:
            health = await server.health_check()
            test_results["tests"].append({
                "test": "Health Check",
                "status": "PASS" if health.get("status") == "healthy" else "FAIL",
                "details": health
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Health Check",
                "status": "FAIL",
                "error": str(e)
            })

        # Test template listing
        try:
            result = await server._handle_list_templates({})
            templates_count = len(result.get("data", {}).get("templates", []))
            test_results["tests"].append({
                "test": "Template Listing",
                "status": "PASS" if templates_count > 0 else "FAIL",
                "details": f"Found {templates_count} templates"
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Template Listing",
                "status": "FAIL",
                "error": str(e)
            })

        # Test report generation with mock data
        try:
            params = {
                "template_name": "stock_analysis",
                "title": "Test Stock Analysis Report",
                "data": {
                    "symbol": "TEST",
                    "analysis_date": "2024-01-01",
                    "recommendation": "buy",
                    "target_price": 150.00,
                    "current_price": 145.00,
                    "investment_thesis": "Strong fundamentals and technical indicators",
                    "risks": ["Market volatility", "Sector rotation"],
                    "conclusion": "Attractive investment opportunity"
                },
                "save_to_file": False
            }
            result = await server._handle_generate_report(params)
            test_results["tests"].append({
                "test": "Report Generation",
                "status": "PASS" if result.get("success") else "FAIL",
                "details": "Generated test report successfully"
            })
        except Exception as e:
            test_results["tests"].append({
                "test": "Report Generation",
                "status": "FAIL",
                "error": str(e)
            })

        self.results.append(test_results)

    def generate_test_report(self):
        """Generate comprehensive test report."""
        self.logger.info("Generating test report...")

        total_tests = sum(len(server["tests"]) for server in self.results)
        passed_tests = sum(
            1 for server in self.results
            for test in server["tests"]
            if test["status"] == "PASS"
        )
        failed_tests = sum(
            1 for server in self.results
            for test in server["tests"]
            if test["status"] == "FAIL"
        )

        report = f"""
# MCP Server Test Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {failed_tests}
- **Success Rate**: {(passed_tests/total_tests*100):.1f}%

## Detailed Results

"""

        for server_result in self.results:
            server_name = server_result["server"]
            tests = server_result["tests"]

            report += f"### {server_name}\n"

            for test in tests:
                status_icon = "✅" if test["status"] == "PASS" else "❌"
                report += f"- {status_icon} **{test['test']}**: {test['status']}\n"

                if "details" in test:
                    report += f"  - Details: {test['details']}\n"
                if "error" in test:
                    report += f"  - Error: {test['error']}\n"

            report += "\n"

        # Save report to file
        report_path = Path("reports/mcp-server-test-report.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        self.logger.info(f"Test report saved to: {report_path}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"MCP SERVER TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"{'='*60}\n")


async def main():
    """Main entry point for MCP server testing."""
    tester = MCPServerTester()
    await tester.test_all_servers()


if __name__ == "__main__":
    asyncio.run(main())
