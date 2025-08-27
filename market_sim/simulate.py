import argparse
import os
import sys

# Ensure imports work regardless of cwd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def main():
    parser = argparse.ArgumentParser(description="Market Sim Scenarios")
    subparsers = parser.add_subparsers(dest="scenario", help="Scenario to run")

    # Streamlet scenario
    p_streamlet = subparsers.add_parser("streamlet", help="Run Streamlet consensus demo")
    p_streamlet.add_argument("--epochs", type=int, default=8, help="Number of epochs to simulate")
    p_streamlet.add_argument("--plot", action="store_true", default=True, help="Show Plotly visualization (default: on)")

    # Stock Market Consensus scenario
    p_stock_consensus = subparsers.add_parser("stock-consensus", help="Run stock market consensus demo")
    p_stock_consensus.add_argument("--epochs", type=int, default=12, help="Number of consensus epochs to run")
    p_stock_consensus.add_argument("--nodes", type=int, default=4, help="Number of consensus nodes")

    # Consensus Trading scenario
    p_consensus_trading = subparsers.add_parser("consensus-trading", help="Run consensus-based trading demo")
    p_consensus_trading.add_argument("--nodes", type=int, default=4, help="Number of consensus nodes")

    # Default to streamlet if no subcommand
    args, unknown = parser.parse_known_args()
    scenario = args.scenario or "streamlet"

    if scenario == "streamlet":
        from simulation.scenarios.streamlet_demo import run_demo
        # Re-parse for streamlet in case user omitted subcommand
        if args.scenario is None:
            dparser = argparse.ArgumentParser(add_help=False)
            dparser.add_argument("--epochs", type=int, default=8)
            dparser.add_argument("--plot", action="store_true", default=True)
            dargs = dparser.parse_args(unknown)
            run_demo(epochs=dargs.epochs, plot=dargs.plot)
        else:
            run_demo(epochs=args.epochs, plot=args.plot)
    elif scenario == "stock-consensus":
        from simulation.scenarios.stock_market_consensus_demo import run_stock_market_consensus_demo
        run_stock_market_consensus_demo(epochs=args.epochs, num_nodes=args.nodes)
    elif scenario == "consensus-trading":
        from simulation.scenarios.consensus_trading_demo import run_consensus_trading_demo
        run_consensus_trading_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 