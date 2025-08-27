"""
Consensus-aware matching engine that uses Streamlet consensus prices.
"""

from typing import List, Optional, Tuple
from decimal import Decimal
from datetime import datetime

from core.models.base import Order, Trade, OrderBook, OrderSide, OrderStatus, OrderType
from core.models.stock_price import PriceConsensus
from market.exchange.matching_engine import MatchingEngine
from market.consensus.stock_market_network import StockMarketConsensusNetwork


class ConsensusMatchingEngine(MatchingEngine):
    """Matching engine that validates trades against consensus prices."""
    
    def __init__(self, symbol: str, consensus_network: StockMarketConsensusNetwork):
        super().__init__(symbol)
        self.symbol = symbol  # Store symbol for access
        self.consensus_network = consensus_network
        self.max_price_deviation = Decimal('0.05')  # 5% max deviation from consensus
        
    def get_latest_consensus_price(self) -> Optional[Decimal]:
        """Get the latest finalized consensus price."""
        finalized_prices = self.consensus_network.get_finalized_consensus_prices()
        if finalized_prices:
            return finalized_prices[-1].consensus_price
        return None
    
    def validate_trade_price(self, trade_price: Decimal) -> bool:
        """Validate trade price against consensus price."""
        consensus_price = self.get_latest_consensus_price()
        if not consensus_price:
            # If no consensus price available, allow the trade
            return True
            
        # Calculate deviation from consensus
        deviation = abs(trade_price - consensus_price) / consensus_price
        
        if deviation > self.max_price_deviation:
            print(f"Trade rejected: Price ${trade_price:.2f} deviates {deviation:.2%} from consensus ${consensus_price:.2f}")
            return False
            
        return True
    
    def _create_trade(self, order1: Order, order2: Order, quantity: Decimal, price: Decimal) -> Optional[Trade]:
        """Create a trade if price is valid against consensus."""
        if not self.validate_trade_price(price):
            return None
            
        return super()._create_trade(order1, order2, quantity, price)
    
    def process_order(self, order: Order) -> List[Trade]:
        """Process order with consensus validation."""
        # Get consensus price for logging
        consensus_price = self.get_latest_consensus_price()
        if consensus_price:
            print(f"Processing order at ${order.price:.2f} (consensus: ${consensus_price:.2f})")
        
        return super().process_order(order)
    
    def print_consensus_status(self):
        """Print current consensus status."""
        consensus_price = self.get_latest_consensus_price()
        if consensus_price:
            print(f"Current consensus price for {self.symbol}: ${consensus_price:.2f}")
        else:
            print(f"No consensus price available for {self.symbol}")
            
        finalized_count = len(self.consensus_network.get_finalized_consensus_prices())
        print(f"Finalized consensus prices: {finalized_count}")


def create_consensus_matching_engine(symbol: str = "AAPL", num_nodes: int = 4) -> ConsensusMatchingEngine:
    """Create a consensus-aware matching engine."""
    consensus_network = StockMarketConsensusNetwork(
        node_ids=[f"node_{i}" for i in range(num_nodes)],
        symbol=symbol,
        f=1
    )
    
    return ConsensusMatchingEngine(symbol, consensus_network) 