"""
Demo scenario for stock market consensus using Streamlet Protocol.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the market_sim directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from market.consensus.stock_market_network import create_aapl_consensus_network
from core.models.stock_price import PriceConsensus


def run_stock_market_consensus_demo(epochs: int = 12, num_nodes: int = 4):
    """Run the stock market consensus demo."""
    print("=" * 80)
    print("STOCK MARKET CONSENSUS DEMO")
    print("Streamlet Protocol for AAPL Price Consensus")
    print("=" * 80)
    
    # Create the consensus network
    print(f"Creating AAPL consensus network with {num_nodes} nodes...")
    network = create_aapl_consensus_network(num_nodes)
    
    # Print initial network status
    network.print_network_status()
    
    # Run the consensus simulation
    print(f"\nRunning consensus simulation for {epochs} epochs...")
    consensus_results = network.run_price_consensus_simulation(epochs)
    
    # Print final results
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    print(f"Total consensus prices generated: {len(consensus_results)}")
    print(f"Finalized consensus prices: {len(network.get_finalized_consensus_prices())}")
    
    if consensus_results:
        print(f"\nPrice Range: ${min(c.consensus_price for c in consensus_results):.2f} - ${max(c.consensus_price for c in consensus_results):.2f}")
        print(f"Average Price: ${sum(c.consensus_price for c in consensus_results) / len(consensus_results):.2f}")
        
        print(f"\nVolume Range: {min(c.total_volume for c in consensus_results):,.0f} - {max(c.total_volume for c in consensus_results):,.0f}")
        print(f"Average Volume: {sum(c.total_volume for c in consensus_results) / len(consensus_results):,.0f}")
    
    # Show detailed consensus history
    print(f"\nDetailed Consensus History:")
    print("-" * 60)
    for i, consensus in enumerate(consensus_results):
        print(f"Epoch {i}: ${consensus.consensus_price:.2f} (VWAP: ${consensus.volume_weighted_price:.2f}, Volume: {consensus.total_volume:,.0f})")
    
    # Show finalized consensus prices
    finalized_prices = network.get_finalized_consensus_prices()
    if finalized_prices:
        print(f"\nFinalized Consensus Prices (Immutable):")
        print("-" * 60)
        for i, consensus in enumerate(finalized_prices):
            print(f"Finalized {i+1}: ${consensus.consensus_price:.2f} (Block: {consensus.block_hash[:8]}...)")
    
    # Print final network status
    network.print_network_status()
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)
    
    return consensus_results


def main():
    """Main entry point for the demo."""
    parser = argparse.ArgumentParser(description="Stock Market Consensus Demo")
    parser.add_argument("--epochs", type=int, default=12, help="Number of consensus epochs to run")
    parser.add_argument("--nodes", type=int, default=4, help="Number of consensus nodes")
    
    args = parser.parse_args()
    
    try:
        run_stock_market_consensus_demo(args.epochs, args.nodes)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 