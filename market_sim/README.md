# Market Dynamics and Trading Simulation Framework

Implements a framework for simulating, analyzing, and learning about financial markets, trading strategies, and blockchain integration.

Currently v0.

## Project Structure

```
market_sim/
├── core/                      # Core functionality and base classes
│   ├── data/                 # Data management and storage
│   ├── models/              # Core market models and entities
│   └── utils/               # Utility functions and helpers
│
├── market/                   # Market simulation components
│   ├── exchange/            # Exchange mechanisms and matching engines
│   ├── agents/              # Trading agents and strategies
│   ├── mechanisms/          # Trading mechanisms (options, warrants, etc.)
│   └── dynamics/            # Market dynamics and price formation
│
├── strategies/               # Trading strategies implementation
│   ├── traditional/         # Classical trading strategies
│   ├── hft/                 # High-frequency trading strategies
│   └── ml/                  # Machine learning based strategies
│
├── simulation/              # Simulation framework
│   ├── engine/             # Simulation engine and time management
│   ├── scenarios/          # Pre-defined simulation scenarios
│   └── results/            # Results analysis and visualization
│
├── blockchain/              # Blockchain integration
│   ├── ethereum/           # Ethereum specific implementations
│   ├── consensus/          # Consensus mechanisms
│   └── contracts/          # Smart contracts
│
├── analysis/                # Analysis tools and utilities
│   ├── metrics/            # Performance and risk metrics
│   ├── visualization/      # Data visualization tools
│   └── reports/            # Report generation
│
├── api/                     # API interfaces
│   ├── rest/               # REST API
│   └── websocket/          # WebSocket API
│
├── ui/                      # User interfaces
│   ├── web/                # Web interface
│   ├── cli/                # Command-line interface
│   └── desktop/            # Desktop application
│
└── tests/                   # Test suite
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── performance/        # Performance tests
```

## Features

### Market Simulation
- Real-time market simulation with configurable parameters
- Multiple asset types and trading mechanisms
- Price formation and order book management
- Trading agent framework with customizable strategies

### Trading Mechanisms
- Stock trading with various order types
- Options and warrants simulation
- Short selling and margin trading
- Custom mechanism creation framework

### High-Frequency Trading
- Ultra-low latency framework
- Order execution optimization
- Market making strategies
- Statistical arbitrage

### Blockchain Integration
- Ethereum smart contract integration
- Consensus mechanism simulation
- Cross-chain trading strategies
- DeFi protocol integration

### Learning Environment
- Interactive tutorials and scenarios
- Strategy backtesting framework
- Performance analytics
- Risk management tools

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with coverage
pytest --cov=market_sim

# Run specific test file
pytest tests/integration/test_market_making.py
```

## Streamlet (Textbook Blockchain Protocol)

A minimal implementation of Streamlet (from “Foundations of Distributed Consensus and Blockchains”, Ch. 7) is included for educational use.

- Location: `core/consensus/streamlet.py`
- Crypto: Ed25519 signatures using `cryptography`
- Defaults: `n=4`, `f=1` (quorum `2f+1 = 3`), deterministic round‑robin leaders, synchronous delivery
- Finalization rule: finalize the middle block of any three consecutive notarized blocks (by epoch)

### How to run Streamlet unit tests
```bash
# From market_sim/ directory
export PYTHONPATH=.
pytest -q tests/test_streamlet.py
```

### Minimal demo scenario
A simple demo produces a small chain, prints notarizations and finalized blocks, and opens a Plotly timeline in your browser by default.

Run:
```bash
# From market_sim/ directory
python simulate.py

# Optional: change epochs
python simulate.py --epochs 12

# Advanced (module form)
python -m simulation.scenarios.streamlet_demo --epochs 8 --plot
```

Flags:
- `--epochs N`: number of epochs to simulate (default: 8)
- Plot opens by default. If you need a non-GUI environment, we can add a headless flag on request.

Output highlights:
- Proposed blocks per epoch, notarized tips, and finalized set shared by all nodes

## License

This project is licensed under the MIT License - see the LICENSE file for details.