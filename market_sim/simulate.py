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
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 