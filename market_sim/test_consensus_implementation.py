#!/usr/bin/env python3
"""
Simple test script to verify stock market consensus implementation.
"""

import sys
import os
from pathlib import Path

# Add the market_sim directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from market.consensus.stock_market_network import create_aapl_consensus_network
from market.exchange.consensus_matching_engine import create_consensus_matching_engine
from core.models.base import Order, OrderSide, OrderType
from decimal import Decimal


def test_basic_consensus():
    """Test basic consensus functionality."""
    print("Testing basic consensus functionality...")
    
    # Create network
    network = create_aapl_consensus_network(4)
    
    # Run a few epochs
    for epoch in range(8):
        consensus = network.step_price_epoch(epoch)
        if consensus:
            print(f"Epoch {epoch}: ${consensus.consensus_price:.2f}")
    
    # Check finalized prices
    finalized = network.get_finalized_consensus_prices()
    print(f"Finalized prices: {len(finalized)}")
    
    return len(finalized) > 0


def test_trading_integration():
    """Test trading integration with consensus."""
    print("\nTesting trading integration...")
    
    # Create matching engine
    matching_engine = create_consensus_matching_engine("AAPL", 4)
    
    # Run consensus to get prices
    for epoch in range(10):
        matching_engine.consensus_network.step_price_epoch(epoch)
    
    # Get consensus price
    consensus_price = matching_engine.get_latest_consensus_price()
    if consensus_price:
        print(f"Consensus price: ${consensus_price:.2f}")
        
        # Create test orders
        buy_order = Order.create_limit_order("AAPL", OrderSide.BUY, Decimal('100'), 
                                           consensus_price * Decimal('0.95'), "test_trader")
        
        # Process order
        trades = matching_engine.process_order(buy_order)
        print(f"Trades generated: {len(trades)}")
        
        return True
    else:
        print("No consensus price available")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("STOCK MARKET CONSENSUS IMPLEMENTATION TEST")
    print("=" * 60)
    
    # Test basic consensus
    consensus_ok = test_basic_consensus()
    
    # Test trading integration
    trading_ok = test_trading_integration()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Basic Consensus: {'✓ PASS' if consensus_ok else '✗ FAIL'}")
    print(f"Trading Integration: {'✓ PASS' if trading_ok else '✗ FAIL'}")
    
    if consensus_ok and trading_ok:
        print("\n🎉 All tests passed! Stock market consensus implementation is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 