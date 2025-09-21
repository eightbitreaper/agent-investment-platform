"""
Comprehensive Backtesting Example for the Agent Investment Platform.

This script demonstrates how to use the backtesting framework to validate
investment strategies with historical data and generate detailed performance reports.

Example Usage:
    python examples/backtest_example.py
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent / 'src')
sys.path.insert(0, src_path)

from backtesting import (
    BacktestEngine,
    BacktestConfig,
    DataManager,
    DataSource,
    create_sample_backtest_config,
    run_strategy_backtest,
    generate_backtest_dataset
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Run comprehensive backtesting example."""
    print("🚀 Agent Investment Platform - Backtesting Framework Demo")
    print("=" * 60)

    # Configuration
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    initial_capital = 100000.0

    print(f"📊 Backtesting Configuration:")
    print(f"   Symbols: {', '.join(symbols)}")
    print(f"   Period: {start_date} to {end_date}")
    print(f"   Initial Capital: ${initial_capital:,.2f}")
    print()

    try:
        # Step 1: Generate sample dataset
        print("📈 Step 1: Generating market data...")
        price_data, news_data = await generate_backtest_dataset(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            include_news=True
        )

        data_summary = []
        for symbol, df in price_data.items():
            data_summary.append(f"   {symbol}: {len(df)} trading days")
        print("✅ Data generated successfully:")
        print("\n".join(data_summary))
        print()

        # Step 2: Create backtesting configuration
        print("⚙️  Step 2: Setting up backtest configuration...")
        config = create_sample_backtest_config(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )

        print(f"✅ Configuration created:")
        print(f"   Max Positions: {config.max_positions}")
        print(f"   Position Sizing: {config.position_sizing_method}")
        print(f"   Rebalance Frequency: {config.rebalance_frequency}")
        print(f"   Commission per Trade: ${config.commission_per_trade}")
        print(f"   Stop Loss Enabled: {config.enable_stop_loss}")
        print()

        # Step 3: Run backtests for different strategies
        strategies_to_test = [
            'conservative_growth',
            'aggressive_growth',
            'value_investing',
            'momentum_trading'
        ]

        print("🔄 Step 3: Running backtests for multiple strategies...")
        backtest_results = {}

        for strategy_name in strategies_to_test:
            print(f"   Testing strategy: {strategy_name}")

            result = await run_strategy_backtest(
                strategy_name=strategy_name,
                symbols=symbols,
                price_data=price_data,
                config=config,
                news_data=news_data
            )

            backtest_results[strategy_name] = result

            # Print basic results
            if result.status.value == "completed" and result.risk_metrics:
                print(f"   ✅ {strategy_name}:")
                print(f"      Total Return: {result.risk_metrics.total_return:.2%}")
                print(f"      Sharpe Ratio: {result.risk_metrics.sharpe_ratio:.3f}")
                print(f"      Max Drawdown: {result.risk_metrics.max_drawdown:.2%}")
                print(f"      Win Rate: {result.risk_metrics.win_rate:.1%}")
                print(f"      Total Trades: {result.risk_metrics.total_trades}")
            else:
                print(f"   ❌ {strategy_name}: {result.status.value}")
                if result.error_message:
                    print(f"      Error: {result.error_message}")
            print()

        # Step 4: Analyze and compare results
        print("📊 Step 4: Strategy Performance Comparison")
        print("-" * 40)

        # Create comparison table
        comparison_data = []
        headers = ["Strategy", "Total Return", "Sharpe Ratio", "Max Drawdown", "Win Rate", "Trades"]

        for strategy_name, result in backtest_results.items():
            if result.status.value == "completed" and result.risk_metrics:
                rm = result.risk_metrics
                comparison_data.append([
                    strategy_name,
                    f"{rm.total_return:.2%}",
                    f"{rm.sharpe_ratio:.3f}",
                    f"{rm.max_drawdown:.2%}",
                    f"{rm.win_rate:.1%}",
                    str(rm.total_trades)
                ])
            else:
                comparison_data.append([
                    strategy_name,
                    "Failed",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A"
                ])

        # Print comparison table
        col_widths = [max(len(str(row[i])) for row in [headers] + comparison_data) + 2
                     for i in range(len(headers))]

        # Header
        header_row = "".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(header_row)
        print("-" * len(header_row))

        # Data rows
        for row in comparison_data:
            data_row = "".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
            print(data_row)

        print()

        # Step 5: Identify best performing strategy
        successful_results = {
            name: result for name, result in backtest_results.items()
            if result.status.value == "completed" and result.risk_metrics
        }

        if successful_results:
            best_strategy_name = max(
                successful_results.keys(),
                key=lambda name: successful_results[name].risk_metrics.sharpe_ratio
            )

            best_result = successful_results[best_strategy_name]
            best_metrics = best_result.risk_metrics

            print("🏆 Best Performing Strategy:")
            print(f"   Strategy: {best_strategy_name}")
            print(f"   Total Return: {best_metrics.total_return:.2%}")
            print(f"   Annualized Return: {best_metrics.annualized_return:.2%}")
            print(f"   Sharpe Ratio: {best_metrics.sharpe_ratio:.3f}")
            print(f"   Sortino Ratio: {best_metrics.sortino_ratio:.3f}")
            print(f"   Maximum Drawdown: {best_metrics.max_drawdown:.2%}")
            print(f"   Win Rate: {best_metrics.win_rate:.1%}")
            print(f"   Profit Factor: {best_metrics.profit_factor:.2f}")
            print(f"   Total Trades: {best_metrics.total_trades}")
            print(f"   Execution Rate: {best_result.execution_rate:.1%}")
            print()

            # Show top trades
            completed_trades = [t for t in best_result.trades if t.exit_date is not None and t.pnl]
            if completed_trades:
                # Sort by P&L percentage
                top_trades = sorted(completed_trades, key=lambda t: t.pnl_percent or 0, reverse=True)[:5]

                print("💰 Top 5 Trades:")
                for i, trade in enumerate(top_trades, 1):
                    print(f"   {i}. {trade.symbol}: {trade.pnl_percent:.2%} "
                          f"({trade.hold_days} days, ${trade.pnl:.2f})")
                print()

        # Step 6: Generate insights and recommendations
        print("💡 Key Insights and Recommendations:")
        print("-" * 40)

        if successful_results:
            # Calculate average metrics
            avg_return = sum(r.risk_metrics.total_return for r in successful_results.values()) / len(successful_results)
            avg_sharpe = sum(r.risk_metrics.sharpe_ratio for r in successful_results.values()) / len(successful_results)

            print(f"📈 Average Performance Across Strategies:")
            print(f"   Average Return: {avg_return:.2%}")
            print(f"   Average Sharpe Ratio: {avg_sharpe:.3f}")
            print()

            # Strategy-specific insights
            high_return_strategies = [
                name for name, result in successful_results.items()
                if result.risk_metrics.total_return > avg_return
            ]

            high_sharpe_strategies = [
                name for name, result in successful_results.items()
                if result.risk_metrics.sharpe_ratio > avg_sharpe
            ]

            print("🎯 Strategic Recommendations:")
            if high_return_strategies:
                print(f"   • High Return Strategies: {', '.join(high_return_strategies)}")
            if high_sharpe_strategies:
                print(f"   • High Risk-Adjusted Returns: {', '.join(high_sharpe_strategies)}")

            # Risk management insights
            low_drawdown_strategies = [
                name for name, result in successful_results.items()
                if result.risk_metrics.max_drawdown > -0.15  # Less than 15% drawdown
            ]

            if low_drawdown_strategies:
                print(f"   • Conservative Options: {', '.join(low_drawdown_strategies)}")

            print("   • Consider combining strategies for diversification")
            print("   • Monitor execution rates to optimize trade timing")
            print("   • Adjust position sizing based on risk tolerance")

        else:
            print("   ❌ No successful backtests completed")
            print("   • Review strategy implementation")
            print("   • Check data quality and availability")
            print("   • Verify backtesting configuration")

        print()
        print("✅ Backtesting analysis completed!")
        print("📝 Next steps:")
        print("   1. Review detailed strategy performance")
        print("   2. Consider out-of-sample testing")
        print("   3. Implement paper trading for validation")
        print("   4. Monitor live performance metrics")

    except Exception as e:
        print(f"❌ Error during backtesting: {e}")
        import traceback
        traceback.print_exc()


async def run_single_strategy_example():
    """Example of running a single strategy backtest with detailed analysis."""
    print("\n" + "="*60)
    print("🔍 DETAILED SINGLE STRATEGY ANALYSIS")
    print("="*60)

    # Simple configuration for focused analysis
    symbols = ['AAPL', 'MSFT']
    config = create_sample_backtest_config(
        start_date="2023-06-01",
        end_date="2023-12-31",
        initial_capital=50000.0
    )

    # Generate data
    price_data, news_data = await generate_backtest_dataset(
        symbols=symbols,
        start_date="2023-06-01",
        end_date="2023-12-31"
    )

    # Run single strategy
    result = await run_strategy_backtest(
        strategy_name='conservative_growth',
        symbols=symbols,
        price_data=price_data,
        config=config,
        news_data=news_data
    )

    if result.status.value == "completed":
        print(f"📊 Strategy: {result.strategy_name}")
        print(f"⏱️  Duration: {result.end_time - result.start_time}")
        print()

        # Portfolio progression
        if result.portfolio_history:
            initial_value = result.portfolio_history[0].total_value
            final_value = result.portfolio_history[-1].total_value

            print("💼 Portfolio Progression:")
            print(f"   Initial Value: ${initial_value:,.2f}")
            print(f"   Final Value: ${final_value:,.2f}")
            print(f"   Net Gain/Loss: ${final_value - initial_value:,.2f}")
            print()

            # Show periodic snapshots
            print("📈 Portfolio Snapshots (Monthly):")
            monthly_snapshots = result.portfolio_history[::22]  # Roughly monthly
            for snapshot in monthly_snapshots[:6]:  # Show first 6 months
                print(f"   {snapshot.date.strftime('%Y-%m-%d')}: "
                      f"${snapshot.total_value:,.2f} "
                      f"({snapshot.cumulative_return:+.2%})")

        # Trade analysis
        if result.trades:
            completed_trades = [t for t in result.trades if t.exit_date is not None]
            print(f"\n🔄 Trade Analysis:")
            print(f"   Total Signals: {result.total_signals}")
            print(f"   Executed Trades: {result.signals_executed}")
            print(f"   Execution Rate: {result.execution_rate:.1%}")
            print(f"   Completed Trades: {len(completed_trades)}")

            if completed_trades:
                avg_hold_days = sum(t.hold_days or 0 for t in completed_trades) / len(completed_trades)
                print(f"   Average Hold Period: {avg_hold_days:.1f} days")

                # Trade distribution by symbol
                trade_counts = {}
                for trade in completed_trades:
                    trade_counts[trade.symbol] = trade_counts.get(trade.symbol, 0) + 1

                print("   Trades by Symbol:")
                for symbol, count in sorted(trade_counts.items()):
                    print(f"      {symbol}: {count} trades")

    else:
        print(f"❌ Backtest failed: {result.error_message}")


if __name__ == "__main__":
    print("Starting comprehensive backtesting example...")

    try:
        # Run main example
        asyncio.run(main())

        # Run detailed single strategy example
        asyncio.run(run_single_strategy_example())

    except KeyboardInterrupt:
        print("\n⏹️  Backtesting interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
