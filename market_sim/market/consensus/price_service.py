"""
Price consensus service for stock market Streamlet implementation.
"""

import json
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from dataclasses import asdict

from core.models.stock_price import StockPrice, PriceConsensus, PriceValidation
from core.consensus.streamlet import Block


class AAPLPriceSimulator:
    """Simulates AAPL stock price data from multiple sources."""
    
    def __init__(self, base_price: Decimal = Decimal('150.00')):
        self.base_price = base_price
        self.current_price = base_price
        self.volatility = Decimal('0.02')  # 2% volatility
        self.trend = Decimal('0.001')  # Slight upward trend
        
    def generate_price_feed(self, source: str) -> StockPrice:
        """Generate a simulated price feed for AAPL."""
        # Add some randomness and trend
        change = (random.random() - 0.5) * 2 * float(self.volatility) * float(self.current_price)
        trend_change = float(self.trend) * float(self.current_price)
        
        new_price = self.current_price + Decimal(str(change)) + Decimal(str(trend_change))
        
        # Ensure price stays within reasonable bounds
        new_price = max(Decimal('50.00'), min(Decimal('500.00'), new_price))
        
        # Generate realistic volume (1000-10000 shares)
        volume = Decimal(str(random.randint(1000, 10000)))
        
        # Update current price
        self.current_price = new_price
        
        return StockPrice.create(
            symbol="AAPL",
            price=new_price,
            volume=volume,
            source=source
        )


class PriceConsensusService:
    """Service for aggregating and validating stock prices for consensus."""
    
    def __init__(self, symbol: str = "AAPL"):
        self.symbol = symbol
        self.validation_rules = PriceValidation.create_aapl_rules()
        self.price_simulator = AAPLPriceSimulator()
        self.last_consensus_price: Optional[Decimal] = None
        
    def generate_price_feeds(self, num_sources: int = 3) -> List[StockPrice]:
        """Generate multiple price feeds from different sources."""
        sources = ["market_data_1", "market_data_2", "external_feed"]
        feeds = []
        
        for i in range(min(num_sources, len(sources))):
            feed = self.price_simulator.generate_price_feed(sources[i])
            feeds.append(feed)
            
        return feeds
    
    def validate_prices(self, prices: List[StockPrice]) -> List[StockPrice]:
        """Validate prices against rules and previous consensus."""
        valid_prices = []
        
        for price in prices:
            # Check price bounds
            if price.price < self.validation_rules.min_price or \
               price.price > self.validation_rules.max_price:
                continue
                
            # Check volume threshold
            if price.volume < self.validation_rules.min_volume:
                continue
                
            # Check deviation from last consensus (if available)
            if self.last_consensus_price:
                deviation = abs(price.price - self.last_consensus_price) / self.last_consensus_price
                if deviation > self.validation_rules.max_price_deviation:
                    continue
                    
            valid_prices.append(price)
            
        return valid_prices
    
    def calculate_consensus_price(self, prices: List[StockPrice]) -> PriceConsensus:
        """Calculate consensus price using volume-weighted average."""
        if not prices:
            raise ValueError("No valid prices provided for consensus")
            
        # Calculate volume-weighted average price (VWAP)
        total_volume = sum(p.volume for p in prices)
        weighted_sum = sum(p.price * p.volume for p in prices)
        vwap = weighted_sum / total_volume
        
        # Simple average as consensus price (could be median or other method)
        consensus_price = sum(p.price for p in prices) / len(prices)
        
        return PriceConsensus.create(
            symbol=self.symbol,
            consensus_price=consensus_price,
            vwap=vwap,
            total_volume=total_volume,
            price_count=len(prices),
            block_hash=""  # Will be set when block is created
        )
    
    def create_price_block_payload(self, consensus: PriceConsensus) -> bytes:
        """Create payload for Streamlet block containing price consensus data."""
        payload_data = {
            "type": "price_consensus",
            "symbol": consensus.symbol,
            "consensus_price": str(consensus.consensus_price),
            "volume_weighted_price": str(consensus.volume_weighted_price),
            "total_volume": str(consensus.total_volume),
            "price_count": consensus.price_count,
            "timestamp": consensus.timestamp.isoformat()
        }
        
        return json.dumps(payload_data, sort_keys=True).encode('utf-8')
    
    def process_epoch_prices(self, epoch: int) -> tuple[bytes, PriceConsensus]:
        """Process prices for a consensus epoch and return block payload."""
        # Generate price feeds
        price_feeds = self.generate_price_feeds()
        
        # Validate prices
        valid_prices = self.validate_prices(price_feeds)
        
        # Calculate consensus
        consensus = self.calculate_consensus_price(valid_prices)
        
        # Update last consensus price
        self.last_consensus_price = consensus.consensus_price
        
        # Create block payload
        payload = self.create_price_block_payload(consensus)
        
        return payload, consensus


class StockMarketStreamletNode:
    """Extended Streamlet node for stock market consensus."""
    
    def __init__(self, node_id: str, price_service: PriceConsensusService):
        self.node_id = node_id
        self.price_service = price_service
        self.consensus_history: List[PriceConsensus] = []
        
    def propose_price_block(self, epoch: int, parent_hash: str) -> Optional[Block]:
        """Propose a new price consensus block."""
        try:
            payload, consensus = self.price_service.process_epoch_prices(epoch)
            
            # Create block
            block = Block(
                parent_hash=parent_hash,
                epoch=epoch,
                proposer_id=self.node_id,
                payload=payload
            )
            
            # Store consensus data
            consensus.block_hash = block.hash()
            self.consensus_history.append(consensus)
            
            return block
            
        except Exception as e:
            print(f"Error proposing price block: {e}")
            return None
    
    def get_latest_consensus_price(self) -> Optional[Decimal]:
        """Get the latest consensus price for the stock."""
        if self.consensus_history:
            return self.consensus_history[-1].consensus_price
        return None 