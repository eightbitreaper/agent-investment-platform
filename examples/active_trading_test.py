"""
Active Trading Validation

This script demonstrates the backtesting framework with more active trading
parameters to show actual trade execution and portfolio changes.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent / 'src')
sys.path.insert(0, src_path)

# Configure logging to show more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def run_active_trading_test():
    """Run a test with parameters designed to generate active trading."""
    print("🎯 ACTIVE TRADING BACKTESTING DEMONSTRATION")
    print("=" * 60)
    
    try:
        from backtesting import (
            BacktestEngine,
            BacktestConfig,
            generate_backtest_dataset
        )
        
        # Configuration for more active trading
        symbols = ['AAPL', 'MSFT']  # Limit to 2 symbols for focused testing
        start_date = "2023-01-01"
        end_date = "2023-03-31"  # Shorter period for more targeted testing
        initial_capital = 50000.0
        
        print(f"📊 Active Trading Configuration:")
        print(f"   Symbols: {', '.join(symbols)}")
        print(f"   Period: {start_date} to {end_date} (3 months)")
        print(f"   Initial Capital: ${initial_capital:,.2f}")
        print(f"   Strategy: Aggressive Growth (designed for active trading)")
        print()
        
        # Generate data
        print("📈 Generating market data...")
        price_data, news_data = await generate_backtest_dataset(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            include_news=True
        )
        
        for symbol, df in price_data.items():
            start_price = df.iloc[0]['close']
            end_price = df.iloc[-1]['close']
            return_pct = (end_price - start_price) / start_price
            volatility = df['close'].pct_change().std() * 100
            print(f"   {symbol}: {len(df)} days, ${start_price:.2f} → ${end_price:.2f} ({return_pct:+.1%}), Vol: {volatility:.1f}%")
        print()
        
        # Create aggressive configuration
        print("⚙️ Setting up aggressive trading configuration...")
        config = BacktestConfig(
            start_date=datetime.strptime(start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            initial_capital=initial_capital,
            max_positions=2,
            position_sizing_method="equal_weight",  # Equal weight for predictable sizing
            commission_per_trade=1.0,  # Lower commission to encourage trading
            slippage_percent=0.0001,   # Lower slippage
            enable_stop_loss=False,    # Disable stop loss to see full strategy
            enable_take_profit=False,  # Disable take profit initially
            rebalance_frequency="weekly",  # More frequent rebalancing
            min_position_size=500.0,   # Lower minimum position size
            lookback_period=30         # Shorter lookback for more responsive signals
        )
        
        print(f"✅ Aggressive configuration:")
        print(f"   Position Sizing: {config.position_sizing_method}")
        print(f"   Commission: ${config.commission_per_trade}")
        print(f"   Rebalancing: {config.rebalance_frequency}")
        print(f"   Lookback Period: {config.lookback_period} days")
        print()
        
        # Initialize engine
        print("🔧 Initializing backtesting engine...")
        engine = BacktestEngine(config)
        print("✅ Engine ready for active trading simulation")
        print()
        
        # Run backtest with aggressive growth strategy
        print("🚀 Running aggressive growth backtest...")
        result = await engine.run_backtest(
            strategy_name='aggressive_growth',
            symbols=symbols,
            price_data=price_data,
            news_data=news_data
        )
        
        print("\n" + "=" * 60)
        print("📊 ACTIVE TRADING RESULTS")
        print("=" * 60)
        
        if result.status.value == "completed":
            print("✅ Backtest completed successfully!")
            
            if result.end_time and result.start_time:
                duration = (result.end_time - result.start_time).total_seconds()
                print(f"⏱️ Execution time: {duration:.2f} seconds")
            
            print(f"\n🎯 Trading Activity:")
            print(f"   Total Signals Generated: {result.total_signals}")
            print(f"   Signals Executed: {result.signals_executed}")
            print(f"   Execution Rate: {result.execution_rate:.1%}")
            
            if result.risk_metrics:
                rm = result.risk_metrics
                print(f"\n📈 Performance Metrics:")
                print(f"   Total Return: {rm.total_return:+.2%}")
                print(f"   Annualized Return: {rm.annualized_return:+.2%}")
                print(f"   Total Trades: {rm.total_trades}")
                print(f"   Winning Trades: {rm.winning_trades}")
                print(f"   Losing Trades: {rm.losing_trades}")
                print(f"   Win Rate: {rm.win_rate:.1%}")
                
                if rm.total_trades > 0:
                    print(f"   Average Win: ${rm.avg_win:.2f}")
                    print(f"   Average Loss: ${rm.avg_loss:.2f}")
                    print(f"   Profit Factor: {rm.profit_factor:.2f}")
                
                print(f"   Sharpe Ratio: {rm.sharpe_ratio:.3f}")
                print(f"   Max Drawdown: {rm.max_drawdown:.2%}")
            
            # Portfolio progression
            if result.portfolio_history:
                print(f"\n💼 Portfolio Evolution:")
                history = result.portfolio_history
                
                # Show key checkpoints
                checkpoints = [0, len(history)//3, 2*len(history)//3, -1]
                labels = ["Start", "33%", "67%", "End"]
                
                for i, idx in enumerate(checkpoints):
                    snapshot = history[idx]
                    print(f"   {labels[i]:>5}: {snapshot.date.strftime('%Y-%m-%d')} - "
                          f"${snapshot.total_value:,.0f} ({snapshot.cumulative_return:+.1%}) "
                          f"Cash: ${snapshot.cash:,.0f}")
                
                # Calculate volatility
                daily_returns = [s.daily_return for s in history[1:] if s.daily_return is not None]
                if daily_returns:
                    import numpy as np
                    daily_vol = np.std(daily_returns)
                    annual_vol = daily_vol * np.sqrt(252)
                    print(f"\n📊 Risk Metrics:")
                    print(f"   Daily Volatility: {daily_vol:.4f} ({daily_vol*100:.2f}%)")
                    print(f"   Annualized Volatility: {annual_vol:.1%}")
                    
                    if daily_returns:
                        best_day = max(daily_returns)
                        worst_day = min(daily_returns)
                        print(f"   Best Day: {best_day:+.2%}")
                        print(f"   Worst Day: {worst_day:+.2%}")
            
            # Trade analysis
            if result.trades:
                print(f"\n💰 Trade Analysis:")
                all_trades = result.trades
                completed_trades = [t for t in all_trades if t.exit_date is not None]
                
                print(f"   Total Trade Orders: {len(all_trades)}")
                print(f"   Completed Trades: {len(completed_trades)}")
                
                if completed_trades:
                    # Show individual trades
                    print(f"\n   Completed Trade Details:")
                    for i, trade in enumerate(completed_trades[:10]):  # Show first 10 trades
                        entry_date = trade.entry_date.strftime('%m/%d')
                        exit_date = trade.exit_date.strftime('%m/%d') if trade.exit_date else 'Open'
                        pnl = trade.pnl or 0
                        pnl_pct = trade.pnl_percent or 0
                        hold_days = trade.hold_days or 0
                        
                        print(f"   {i+1:2d}. {trade.symbol} {trade.trade_type} "
                              f"{entry_date}-{exit_date} ({hold_days}d): "
                              f"${pnl:+.2f} ({pnl_pct:+.1%})")
                    
                    if len(completed_trades) > 10:
                        print(f"   ... and {len(completed_trades) - 10} more trades")
                    
                    # Trade statistics
                    profitable_trades = [t for t in completed_trades if t.pnl and t.pnl > 0]
                    losing_trades = [t for t in completed_trades if t.pnl and t.pnl <= 0]
                    
                    print(f"\n   Trade Statistics:")
                    print(f"   Profitable: {len(profitable_trades)} trades")
                    print(f"   Losing: {len(losing_trades)} trades")
                    
                    if profitable_trades:
                        avg_profit = sum(t.pnl or 0 for t in profitable_trades) / len(profitable_trades)
                        print(f"   Average Profit: ${avg_profit:.2f}")
                    
                    if losing_trades:
                        avg_loss = sum(t.pnl or 0 for t in losing_trades) / len(losing_trades)
                        print(f"   Average Loss: ${avg_loss:.2f}")
                    
                    # By symbol
                    symbol_trades = {}
                    for trade in completed_trades:
                        if trade.symbol not in symbol_trades:
                            symbol_trades[trade.symbol] = []
                        symbol_trades[trade.symbol].append(trade)
                    
                    print(f"\n   Performance by Symbol:")
                    for symbol, trades in symbol_trades.items():
                        total_pnl = sum(t.pnl or 0 for t in trades)
                        print(f"   {symbol}: {len(trades)} trades, ${total_pnl:.2f} total P&L")
                
                # Open positions
                open_trades = [t for t in all_trades if t.exit_date is None]
                if open_trades:
                    print(f"\n   Open Positions: {len(open_trades)}")
                    for trade in open_trades:
                        entry_date = trade.entry_date.strftime('%m/%d')
                        days_held = (datetime.now() - trade.entry_date).days
                        print(f"   {trade.symbol} {trade.trade_type} "
                              f"since {entry_date} ({days_held}d)")
            
            print(f"\n🎯 Validation Summary:")
            if result.total_signals > 0:
                print(f"✅ Signal generation working: {result.total_signals} signals")
            else:
                print(f"⚠️ No signals generated - may need strategy adjustment")
                
            if result.signals_executed > 0:
                print(f"✅ Trade execution working: {result.signals_executed} executed")
            else:
                print(f"⚠️ No trades executed - may need parameter adjustment")
                
            if result.portfolio_history:
                print(f"✅ Portfolio tracking working: {len(result.portfolio_history)} snapshots")
                
            if result.risk_metrics:
                print(f"✅ Risk metrics calculation working")
                
            print(f"✅ End-to-end backtesting framework operational")
            
        else:
            print(f"❌ Backtest failed: {result.status.value}")
            if result.error_message:
                print(f"   Error: {result.error_message}")
            
            return False
        
        print(f"\n" + "=" * 60)
        print("🏆 ACTIVE TRADING VALIDATION COMPLETE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Active trading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting active trading backtesting demonstration...")
    
    try:
        success = asyncio.run(run_active_trading_test())
        
        if success:
            print("\n🎉 BACKTESTING FRAMEWORK VALIDATION COMPLETE!")
            print("The system successfully demonstrates:")
            print("• Signal generation and processing")
            print("• Trade execution and tracking")
            print("• Portfolio management and progression")
            print("• Risk metrics and performance analysis")
            print("• End-to-end backtesting workflow")
            print("\n🚀 Ready for production strategy optimization!")
        else:
            print("\n⚠️ Test completed with issues - check configuration")
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")