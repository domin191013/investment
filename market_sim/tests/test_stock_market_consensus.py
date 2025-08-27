"""
Tests for stock market consensus using Streamlet Protocol.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch

from core.models.stock_price import StockPrice, PriceConsensus, PriceValidation
from market.consensus.price_service import AAPLPriceSimulator, PriceConsensusService
from market.consensus.stock_market_network import create_aapl_consensus_network


class TestAAPLPriceSimulator:
    """Test AAPL price simulator."""
    
    def test_generate_price_feed(self):
        """Test price feed generation."""
        simulator = AAPLPriceSimulator(base_price=Decimal('150.00'))
        
        feed = simulator.generate_price_feed("test_source")
        
        assert feed.symbol == "AAPL"
        assert feed.source == "test_source"
        assert feed.price > Decimal('0')
        assert feed.volume > Decimal('0')
        assert feed.timestamp is not None
        
    def test_price_bounds(self):
        """Test that prices stay within reasonable bounds."""
        simulator = AAPLPriceSimulator(base_price=Decimal('150.00'))
        
        for _ in range(100):
            feed = simulator.generate_price_feed("test_source")
            assert Decimal('50.00') <= feed.price <= Decimal('500.00')


class TestPriceConsensusService:
    """Test price consensus service."""
    
    def test_validation_rules(self):
        """Test price validation rules."""
        service = PriceConsensusService("AAPL")
        
        # Test valid price
        valid_price = StockPrice.create("AAPL", Decimal('150.00'), Decimal('1000'), "test")
        valid_prices = service.validate_prices([valid_price])
        assert len(valid_prices) == 1
        
        # Test invalid price (too low)
        invalid_price = StockPrice.create("AAPL", Decimal('10.00'), Decimal('1000'), "test")
        valid_prices = service.validate_prices([invalid_price])
        assert len(valid_prices) == 0
        
        # Test invalid volume (too low)
        invalid_volume = StockPrice.create("AAPL", Decimal('150.00'), Decimal('50'), "test")
        valid_prices = service.validate_prices([invalid_volume])
        assert len(valid_prices) == 0
    
    def test_consensus_calculation(self):
        """Test consensus price calculation."""
        service = PriceConsensusService("AAPL")
        
        prices = [
            StockPrice.create("AAPL", Decimal('150.00'), Decimal('1000'), "source1"),
            StockPrice.create("AAPL", Decimal('152.00'), Decimal('2000'), "source2"),
            StockPrice.create("AAPL", Decimal('148.00'), Decimal('1500'), "source3"),
        ]
        
        consensus = service.calculate_consensus_price(prices)
        
        assert consensus.symbol == "AAPL"
        assert consensus.consensus_price > Decimal('0')
        assert consensus.volume_weighted_price > Decimal('0')
        assert consensus.total_volume == Decimal('4500')
        assert consensus.price_count == 3
    
    @patch('market.consensus.price_service.AAPLPriceSimulator.generate_price_feed')
    def test_process_epoch_prices(self, mock_generate_feed):
        """Test processing epoch prices."""
        service = PriceConsensusService("AAPL")
        
        # Mock price feeds
        mock_generate_feed.side_effect = [
            StockPrice.create("AAPL", Decimal('150.00'), Decimal('1000'), "source1"),
            StockPrice.create("AAPL", Decimal('152.00'), Decimal('2000'), "source2"),
            StockPrice.create("AAPL", Decimal('148.00'), Decimal('1500'), "source3"),
        ]
        
        payload, consensus = service.process_epoch_prices(0)
        
        assert payload is not None
        assert consensus is not None
        assert consensus.symbol == "AAPL"


class TestStockMarketConsensusNetwork:
    """Test stock market consensus network."""
    
    def test_network_creation(self):
        """Test network creation."""
        network = create_aapl_consensus_network(4)
        
        assert len(network.node_ids) == 4
        assert network.symbol == "AAPL"
        assert network.f == 1
        assert len(network.price_services) == 4
        assert len(network.stock_nodes) == 4
    
    def test_network_initialization(self):
        """Test network initialization."""
        network = create_aapl_consensus_network(4)
        
        # Check that all nodes have price services
        for node_id in network.node_ids:
            assert node_id in network.price_services
            assert node_id in network.stock_nodes
            
        # Check that price services are properly initialized
        for service in network.price_services.values():
            assert service.symbol == "AAPL"
            assert service.validation_rules is not None


if __name__ == "__main__":
    pytest.main([__file__]) 