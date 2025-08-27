"""
Stock price models for consensus-based price discovery.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

@dataclass
class StockPrice:
    """Represents a stock price with metadata."""
    symbol: str
    price: Decimal
    volume: Decimal
    timestamp: datetime
    source: str  # e.g., "market_data", "consensus", "external_feed"
    
    @classmethod
    def create(cls, symbol: str, price: Decimal, volume: Decimal, source: str) -> 'StockPrice':
        return cls(
            symbol=symbol,
            price=price,
            volume=volume,
            timestamp=datetime.utcnow(),
            source=source
        )

@dataclass
class PriceConsensus:
    """Represents consensus price data for a stock."""
    symbol: str
    consensus_price: Decimal
    volume_weighted_price: Decimal
    total_volume: Decimal
    price_count: int
    timestamp: datetime
    block_hash: str
    
    @classmethod
    def create(cls, symbol: str, consensus_price: Decimal, vwap: Decimal, 
               total_volume: Decimal, price_count: int, block_hash: str) -> 'PriceConsensus':
        return cls(
            symbol=symbol,
            consensus_price=consensus_price,
            volume_weighted_price=vwap,
            total_volume=total_volume,
            price_count=price_count,
            timestamp=datetime.utcnow(),
            block_hash=block_hash
        )

@dataclass
class PriceValidation:
    """Validation rules for stock prices."""
    min_price: Decimal
    max_price: Decimal
    min_volume: Decimal
    max_price_deviation: Decimal  # percentage
    
    @classmethod
    def create_aapl_rules(cls) -> 'PriceValidation':
        """Create validation rules for AAPL stock."""
        return cls(
            min_price=Decimal('50.00'),  # AAPL minimum reasonable price
            max_price=Decimal('500.00'),  # AAPL maximum reasonable price
            min_volume=Decimal('100'),    # Minimum volume for price validity
            max_price_deviation=Decimal('0.10')  # 10% max deviation from previous consensus
        ) 