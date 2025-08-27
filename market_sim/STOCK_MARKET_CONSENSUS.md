# Stock Market Consensus using Streamlet Protocol

This implementation extends the Streamlet blockchain consensus protocol to achieve consensus on stock prices, specifically for AAPL (Apple Inc.) stock. The system demonstrates how blockchain consensus can be applied to financial markets for reliable price discovery.

## Overview

The stock market consensus system consists of several key components:

1. **Price Consensus Service**: Generates and validates simulated AAPL price data
2. **Stock Market Consensus Network**: Extends Streamlet protocol for price consensus
3. **Consensus-Aware Matching Engine**: Uses finalized consensus prices for trade validation
4. **Demo Scenarios**: Showcase the complete system in action

## Architecture

```
Stock Market Consensus Architecture
├── Price Data Layer
│   ├── AAPLPriceSimulator - Generates realistic price feeds
│   ├── PriceConsensusService - Aggregates and validates prices
│   └── PriceValidation - Defines validation rules
├── Consensus Layer
│   ├── StockMarketConsensusNetwork - Streamlet network for prices
│   ├── StockMarketStreamletNode - Extended nodes for price consensus
│   └── Block Payload - JSON-encoded price consensus data
└── Trading Layer
    ├── ConsensusMatchingEngine - Validates trades against consensus
    └── Order Processing - Uses consensus prices for validation
```

## Key Features

### 1. Simulated Price Generation
- **Realistic AAPL Price Simulation**: Generates price feeds with volatility and trend
- **Multiple Data Sources**: Simulates 3 different price sources (market_data_1, market_data_2, external_feed)
- **Volume-Weighted Pricing**: Calculates VWAP (Volume-Weighted Average Price)
- **Price Bounds**: Ensures prices stay within reasonable AAPL ranges ($50-$500)

### 2. Consensus Validation Rules
- **Price Bounds**: Minimum $50, maximum $500
- **Volume Threshold**: Minimum 100 shares for price validity
- **Deviation Limits**: Maximum 10% deviation from previous consensus
- **Multi-Source Validation**: Requires multiple valid price sources

### 3. Streamlet Protocol Integration
- **Block Structure**: Each block contains consensus price data as JSON payload
- **Finalization**: Uses Streamlet's 3-block finalization rule
- **Fault Tolerance**: Supports f=1 Byzantine faults (4 nodes, quorum of 3)
- **Deterministic Leaders**: Round-robin leadership for price proposals

### 4. Trading Integration
- **Consensus-Based Validation**: Rejects trades that deviate >5% from consensus
- **Real-time Price Updates**: Uses latest finalized consensus prices
- **Order Book Integration**: Maintains traditional order book with consensus validation

## Usage

### Running the Demos

1. **Stock Market Consensus Demo**:
```bash
cd market_sim
python simulate.py stock-consensus --epochs 12 --nodes 4
```

2. **Consensus-Based Trading Demo**:
```bash
cd market_sim
python simulate.py consensus-trading --nodes 4
```

3. **Original Streamlet Demo**:
```bash
cd market_sim
python simulate.py streamlet --epochs 8
```

### Running Tests

```bash
cd market_sim
pytest tests/test_stock_market_consensus.py -v
```

## Implementation Details

### Price Consensus Data Structure

```python
@dataclass
class PriceConsensus:
    symbol: str                    # "AAPL"
    consensus_price: Decimal       # Simple average of valid prices
    volume_weighted_price: Decimal # VWAP calculation
    total_volume: Decimal          # Total volume across all sources
    price_count: int              # Number of valid price sources
    timestamp: datetime           # When consensus was reached
    block_hash: str               # Streamlet block hash
```

### Block Payload Format

Each Streamlet block contains a JSON payload with consensus data:

```json
{
    "type": "price_consensus",
    "symbol": "AAPL",
    "consensus_price": "152.45",
    "volume_weighted_price": "152.67",
    "total_volume": "4500",
    "price_count": 3,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Consensus Process

1. **Price Generation**: Each epoch, the leader generates 3 simulated price feeds
2. **Validation**: Prices are validated against bounds, volume, and deviation rules
3. **Aggregation**: Valid prices are aggregated into consensus price and VWAP
4. **Block Creation**: Consensus data is encoded into Streamlet block payload
5. **Voting**: Network votes on the proposed price block
6. **Notarization**: Block is notarized when quorum (2f+1) votes are received
7. **Finalization**: Block is finalized after 3 consecutive notarized blocks

### Trading Validation

The consensus-aware matching engine:

1. **Gets Latest Consensus**: Retrieves most recent finalized consensus price
2. **Validates Trade Price**: Checks if trade price deviates >5% from consensus
3. **Rejects Invalid Trades**: Blocks trades that exceed deviation threshold
4. **Logs Validation**: Provides detailed logging of consensus vs trade prices

## Example Output

### Stock Market Consensus Demo
```
================================================================================
STOCK MARKET CONSENSUS DEMO
Streamlet Protocol for AAPL Price Consensus
================================================================================

Creating AAPL consensus network with 4 nodes...

Running consensus simulation for 12 epochs...

Epoch 0:
  Consensus Price: $152.45
  VWAP: $152.67
  Volume: 4,500
  Sources: 3

Epoch 1:
  Consensus Price: $153.12
  VWAP: $153.34
  Volume: 5,200
  Sources: 3

...

Finalized Consensus Prices (Immutable):
  Finalized 1: $152.45 (Block: a1b2c3d4...)
  Finalized 2: $153.12 (Block: e5f6g7h8...)
```

### Consensus Trading Demo
```
================================================================================
CONSENSUS-BASED TRADING DEMO
Streamlet Protocol + Trading Integration
================================================================================

Current consensus price: $152.45

Creating orders:
Buy order: 100 shares at $149.40
Sell order: 100 shares at $155.50

Processing buy order...
Processing order at $149.40 (consensus: $152.45)
Buy order trades: 0

Processing sell order...
Processing order at $155.50 (consensus: $152.45)
Sell order trades: 0

Testing price deviation validation...
Attempting trade at $182.94 (20% above consensus)...
Trade rejected: Price $182.94 deviates 20.00% from consensus $152.45
Extreme price trades: 0 (should be 0 due to validation)
```

## Benefits

### 1. **Reliable Price Discovery**
- Byzantine fault tolerance ensures consensus even with malicious nodes
- Finalization guarantees price immutability
- Multi-source validation prevents single point of failure

### 2. **Market Integrity**
- Consensus validation prevents extreme price manipulation
- Volume-weighted pricing reflects true market conditions
- Deviation limits maintain price stability

### 3. **Decentralized Architecture**
- No single authority controls price discovery
- Distributed consensus across multiple nodes
- Transparent and auditable price formation

### 4. **Trading Safety**
- Automatic rejection of outlier trades
- Consensus-based price validation
- Protection against market manipulation

## Future Enhancements

1. **Multi-Asset Support**: Extend to multiple stocks and assets
2. **Real Market Data**: Integrate with actual market data feeds
3. **Smart Contracts**: Deploy consensus prices as blockchain oracles
4. **Advanced Validation**: Machine learning-based price validation
5. **Performance Optimization**: High-frequency consensus updates

## Technical Requirements

- Python 3.8+
- cryptography library for Ed25519 signatures
- decimal for precise financial calculations
- pytest for testing

## License

This implementation is part of the market simulation framework and is licensed under the MIT License. 