#!/usr/bin/env python3
"""
Agent Investment Platform - Quick Demo Script
Shows how to use the platform's core functionality
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_header():
    """Print demo header"""
    print("=" * 60)
    print("🚀 AGENT INVESTMENT PLATFORM - LIVE DEMO")
    print("=" * 60)
    print()

def demo_health_check():
    """Demo the health check system"""
    print("📊 1. PLATFORM HEALTH CHECK")
    print("-" * 30)

    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "scripts/health-check.py"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Platform health check: PASSED")
            # Extract health score from output
            for line in result.stdout.split('\n'):
                if 'Health Score:' in line:
                    print(f"   {line.strip()}")
                elif 'Overall Status:' in line:
                    print(f"   {line.strip()}")
        else:
            print("⚠️  Platform health check: ISSUES DETECTED")
            print(f"   Error: {result.stderr[:100]}")

    except Exception as e:
        print(f"❌ Health check failed: {e}")

    print()

def demo_configuration():
    """Demo configuration system"""
    print("⚙️ 2. CONFIGURATION OVERVIEW")
    print("-" * 30)

    config_files = [
        ("Environment", ".env"),
        ("Strategies", "config/strategies.yaml"),
        ("Data Sources", "config/data-sources.yaml"),
        ("LLM Config", "config/llm-config.yaml")
    ]

    for name, path in config_files:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (missing)")

    print()

def demo_analysis_components():
    """Demo analysis components"""
    print("🧠 3. ANALYSIS COMPONENTS")
    print("-" * 30)

    components = [
        ("Chart Analyzer", "src/analysis/chart_analyzer.py"),
        ("Sentiment Analyzer", "src/analysis/sentiment_analyzer.py"),
        ("Recommendation Engine", "src/analysis/recommendation_engine.py")
    ]

    for name, path in components:
        if os.path.exists(path):
            print(f"✅ {name}: Available")

            # Try to import and show basic info
            try:
                if "chart" in path.lower():
                    from src.analysis.chart_analyzer import ChartAnalyzer
                    analyzer = ChartAnalyzer()
                    print(f"   📈 Chart analysis patterns available")

                elif "sentiment" in path.lower():
                    from src.analysis.sentiment_analyzer import SentimentAnalyzer
                    analyzer = SentimentAnalyzer()
                    print(f"   😊 Sentiment analysis ready")

                elif "recommendation" in path.lower():
                    from src.analysis.recommendation_engine import RecommendationEngine
                    engine = RecommendationEngine()
                    print(f"   🎯 Recommendation engine loaded")

            except Exception as e:
                print(f"   ⚠️  Component needs configuration: {str(e)[:50]}...")
        else:
            print(f"❌ {name}: Not found")

    print()

def demo_reports():
    """Demo generated reports"""
    print("📝 4. GENERATED REPORTS")
    print("-" * 30)

    reports_dir = Path("reports")
    if reports_dir.exists():
        reports = list(reports_dir.glob("*.md"))
        if reports:
            print(f"✅ Found {len(reports)} reports:")

            for report in sorted(reports)[-3:]:  # Show last 3
                stat = report.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime)
                print(f"   📄 {report.name}")
                print(f"      Size: {size:,} bytes, Modified: {mtime.strftime('%Y-%m-%d %H:%M')}")

                # Show first few lines
                try:
                    with open(report, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:3]
                        for line in lines:
                            if line.strip():
                                print(f"      > {line.strip()[:60]}...")
                                break
                except:
                    pass
                print()
        else:
            print("📁 Reports directory exists but no reports found")
    else:
        print("❌ Reports directory not found")

    print()

def demo_docker_status():
    """Demo Docker service status"""
    print("🐳 5. DOCKER SERVICES STATUS")
    print("-" * 30)

    try:
        import subprocess
        result = subprocess.run([
            "docker-compose", "ps"
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                print("✅ Docker services:")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            status = "running" if "Up" in line else "stopped"
                            print(f"   🔧 {name}: {status}")
            else:
                print("📝 No Docker services running")
        else:
            print("❌ Could not check Docker status")

    except Exception as e:
        print(f"⚠️  Docker check failed: {e}")

    print()

def demo_next_steps():
    """Show next steps"""
    print("🎯 6. NEXT STEPS")
    print("-" * 30)

    steps = [
        "1. Configure API keys in .env file",
        "2. Run: .venv\\Scripts\\python.exe orchestrator.py --test-mode",
        "3. Customize strategies in config/strategies.yaml",
        "4. Generate live analysis with --live flag",
        "5. Access web interface at http://localhost:8000",
        "6. Monitor with Grafana at http://localhost:3000"
    ]

    for step in steps:
        print(f"   {step}")

    print()

def main():
    """Run the demo"""
    demo_header()

    try:
        demo_health_check()
        demo_configuration()
        demo_analysis_components()
        demo_reports()
        demo_docker_status()
        demo_next_steps()

        print("🎉 DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("The Agent Investment Platform is ready to use!")
        print()
        print("🚀 **Next Steps:**")
        print("1. Start Ollama: docker-compose up ollama ollama-webui -d")
        print("2. Access AI chat: http://localhost:8080")
        print("3. Get real-time data: python src\\ollama_integration\\financial_data_tool.py quote AAPL")
        print("4. Paste data into chat for current analysis")
        print("5. Generate reports: .venv\\Scripts\\python.exe orchestrator.py --test-mode")
        print()

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()
