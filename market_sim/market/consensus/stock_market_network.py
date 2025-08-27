"""
Stock Market Consensus Network using Streamlet Protocol.
"""

import json
from typing import Dict, List, Optional, Set
from decimal import Decimal

from core.consensus.streamlet import StreamletNetwork, Node, Block, Vote, Notarization
from market.consensus.price_service import PriceConsensusService, StockMarketStreamletNode
from core.models.stock_price import PriceConsensus


class StockMarketConsensusNetwork(StreamletNetwork):
    """Extended Streamlet network for stock market price consensus."""
    
    def __init__(self, node_ids: List[str], symbol: str = "AAPL", f: int = 1):
        super().__init__(node_ids, f)
        self.symbol = symbol
        
        # Initialize price services for each node
        self.price_services: Dict[str, PriceConsensusService] = {}
        self.stock_nodes: Dict[str, StockMarketStreamletNode] = {}
        
        for node_id in node_ids:
            price_service = PriceConsensusService(symbol)
            self.price_services[node_id] = price_service
            self.stock_nodes[node_id] = StockMarketStreamletNode(node_id, price_service)
    
    def step_price_epoch(self, epoch: int) -> Optional[PriceConsensus]:
        """Run a single epoch of price consensus."""
        leader = self.node_ids[epoch % len(self.node_ids)]
        
        # Get the leader's stock node
        leader_stock_node = self.stock_nodes[leader]
        
        # Get parent hash from longest notarized chain
        leader_node = self.nodes[leader]
        chains = leader_node.longest_notarized_chains()
        parent_hash = chains[-1][-1] if chains else leader_node.genesis_hash()
        
        # Propose price block
        block = leader_stock_node.propose_price_block(epoch, parent_hash)
        if not block:
            return None
            
        # Broadcast proposal and gather votes
        votes: List[Vote] = []
        for nid, node in self.nodes.items():
            vote = node.observe_proposal(block)
            if vote:
                votes.append(vote)
                
        # Broadcast votes
        for vote in votes:
            for node in self.nodes.values():
                node.observe_vote(vote)
                
        # Return the consensus data if block was created
        if leader_stock_node.consensus_history:
            return leader_stock_node.consensus_history[-1]
            
        return None
    
    def get_consensus_price_history(self) -> Dict[str, List[PriceConsensus]]:
        """Get consensus price history from all nodes."""
        history = {}
        for node_id, stock_node in self.stock_nodes.items():
            history[node_id] = stock_node.consensus_history.copy()
        return history
    
    def get_latest_consensus_prices(self) -> Dict[str, Optional[Decimal]]:
        """Get the latest consensus price from each node."""
        prices = {}
        for node_id, stock_node in self.stock_nodes.items():
            prices[node_id] = stock_node.get_latest_consensus_price()
        return prices
    
    def get_finalized_consensus_prices(self) -> List[PriceConsensus]:
        """Get all finalized consensus prices across all nodes."""
        finalized_blocks = self.finalized_by_all()
        consensus_prices = []
        
        for node_id, stock_node in self.stock_nodes.items():
            for consensus in stock_node.consensus_history:
                if consensus.block_hash in finalized_blocks:
                    consensus_prices.append(consensus)
                    
        # Sort by timestamp
        consensus_prices.sort(key=lambda x: x.timestamp)
        return consensus_prices
    
    def run_price_consensus_simulation(self, epochs: int = 10) -> List[PriceConsensus]:
        """Run a complete price consensus simulation."""
        print(f"Starting AAPL price consensus simulation for {epochs} epochs...")
        print(f"Network: {len(self.node_ids)} nodes, f={self.f}")
        print("-" * 60)
        
        consensus_results = []
        
        for epoch in range(epochs):
            print(f"Epoch {epoch}:")
            
            # Run consensus step
            consensus = self.step_price_epoch(epoch)
            
            if consensus:
                print(f"  Consensus Price: ${consensus.consensus_price:.2f}")
                print(f"  VWAP: ${consensus.volume_weighted_price:.2f}")
                print(f"  Volume: {consensus.total_volume:,}")
                print(f"  Sources: {consensus.price_count}")
                consensus_results.append(consensus)
            else:
                print("  No consensus reached")
                
            # Show finalized blocks
            finalized = self.get_finalized_consensus_prices()
            if finalized:
                print(f"  Finalized blocks: {len(finalized)}")
                
            print()
            
        print("Simulation completed!")
        print(f"Total consensus prices: {len(consensus_results)}")
        print(f"Finalized consensus prices: {len(self.get_finalized_consensus_prices())}")
        
        return consensus_results
    
    def print_network_status(self):
        """Print current network status."""
        print("\n" + "=" * 60)
        print("STOCK MARKET CONSENSUS NETWORK STATUS")
        print("=" * 60)
        
        print(f"Symbol: {self.symbol}")
        print(f"Nodes: {len(self.node_ids)}")
        print(f"Fault tolerance: f={self.f}")
        print(f"Quorum size: {2 * self.f + 1}")
        
        print("\nLatest Consensus Prices:")
        latest_prices = self.get_latest_consensus_prices()
        for node_id, price in latest_prices.items():
            if price:
                print(f"  {node_id}: ${price:.2f}")
            else:
                print(f"  {node_id}: No consensus")
                
        print(f"\nFinalized Consensus Prices: {len(self.get_finalized_consensus_prices())}")
        
        # Show consensus history for each node
        history = self.get_consensus_price_history()
        for node_id, consensus_list in history.items():
            print(f"\n{node_id} Consensus History ({len(consensus_list)} prices):")
            for i, consensus in enumerate(consensus_list[-3:]):  # Show last 3
                print(f"  {i+1}. ${consensus.consensus_price:.2f} (VWAP: ${consensus.volume_weighted_price:.2f})")


def create_aapl_consensus_network(num_nodes: int = 4) -> StockMarketConsensusNetwork:
    """Create a stock market consensus network for AAPL."""
    node_ids = [f"node_{i}" for i in range(num_nodes)]
    return StockMarketConsensusNetwork(node_ids, symbol="AAPL", f=1) 