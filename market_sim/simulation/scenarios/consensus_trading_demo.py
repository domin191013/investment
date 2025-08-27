"""
Demo showing consensus-based trading with Streamlet Protocol.
"""

import sys
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Add the market_sim directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models.base import Order, OrderSide, OrderType
from market.exchange.consensus_matching_engine import create_consensus_matching_engine
from market.consensus.stock_market_network import create_aapl_consensus_network


def run_consensus_trading_demo():
    """Run a demo showing consensus-based trading."""
    print("=" * 80)
    print("CONSENSUS-BASED TRADING DEMO")
    print("Streamlet Protocol + Trading Integration")
    print("=" * 80)
    
    # Create consensus network and matching engine
    print("Setting up consensus network and matching engine...")
    consensus_network = create_aapl_consensus_network(4)
    matching_engine = create_consensus_matching_engine("AAPL", 4)
    
    # Run some consensus epochs first
    print("\nRunning consensus epochs to establish price...")
    for epoch in range(10):  # Run more epochs to get finalized prices
        consensus = consensus_network.step_price_epoch(epoch)
        if consensus:
            print(f"Epoch {epoch}: Consensus price ${consensus.consensus_price:.2f}")
    
    # Show consensus status
    print("\nConsensus Status:")
    matching_engine.print_consensus_status()
    
    # Create some test orders
    print("\n" + "=" * 80)
    print("TRADING WITH CONSENSUS VALIDATION")
    print("=" * 80)
    
    # Get current consensus price
    consensus_price = matching_engine.get_latest_consensus_price()
    if not consensus_price:
        print("No consensus price available. Running more epochs...")
        for epoch in range(10, 15):
            consensus_network.step_price_epoch(epoch)
        consensus_price = matching_engine.get_latest_consensus_price()
    
    if consensus_price:
        print(f"Current consensus price: ${consensus_price:.2f}")
        
        # Create orders around consensus price
        buy_price = consensus_price * Decimal('0.98')  # 2% below consensus
        sell_price = consensus_price * Decimal('1.02')  # 2% above consensus
        
        print(f"\nCreating orders:")
        print(f"Buy order: 100 shares at ${buy_price:.2f}")
        print(f"Sell order: 100 shares at ${sell_price:.2f}")
        
        # Create and process orders
        buy_order = Order.create_limit_order("AAPL", OrderSide.BUY, Decimal('100'), buy_price, "trader_1")
        sell_order = Order.create_limit_order("AAPL", OrderSide.SELL, Decimal('100'), sell_price, "trader_2")
        
        # Process buy order first
        print(f"\nProcessing buy order...")
        buy_trades = matching_engine.process_order(buy_order)
        print(f"Buy order trades: {len(buy_trades)}")
        
        # Process sell order
        print(f"\nProcessing sell order...")
        sell_trades = matching_engine.process_order(sell_order)
        print(f"Sell order trades: {len(sell_trades)}")
        
        # Try a trade with extreme price deviation
        print(f"\nTesting price deviation validation...")
        extreme_price = consensus_price * Decimal('1.20')  # 20% above consensus
        extreme_order = Order.create_limit_order("AAPL", OrderSide.SELL, Decimal('50'), extreme_price, "trader_3")
        
        print(f"Attempting trade at ${extreme_price:.2f} (20% above consensus)...")
        extreme_trades = matching_engine.process_order(extreme_order)
        print(f"Extreme price trades: {len(extreme_trades)} (should be 0 due to validation)")
        
        # Show final order book state
        print(f"\nFinal order book state:")
        print(f"Bids: {len(matching_engine.order_book.bids)} price levels")
        print(f"Asks: {len(matching_engine.order_book.asks)} price levels")
        
        if matching_engine.order_book.bids:
            best_bid = max(matching_engine.order_book.bids.keys())
            print(f"Best bid: ${best_bid:.2f}")
            
        if matching_engine.order_book.asks:
            best_ask = min(matching_engine.order_book.asks.keys())
            print(f"Best ask: ${best_ask:.2f}")
    
    # Show final consensus status
    print(f"\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    matching_engine.print_consensus_status()
    
    finalized_prices = consensus_network.get_finalized_consensus_prices()
    print(f"\nFinalized consensus prices: {len(finalized_prices)}")
    for i, consensus in enumerate(finalized_prices[-3:]):  # Show last 3
        print(f"  {i+1}. ${consensus.consensus_price:.2f} (VWAP: ${consensus.volume_weighted_price:.2f})")
    
    print(f"\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_consensus_trading_demo() 