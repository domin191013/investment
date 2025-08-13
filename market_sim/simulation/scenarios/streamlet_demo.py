import argparse
from typing import List, Dict

from core.consensus.streamlet import StreamletNetwork

try:
    import plotly.graph_objects as go
    import plotly.io as pio
    pio.renderers.default = "browser"
except Exception:
    go = None

import webbrowser
import tempfile
from pathlib import Path


def run_demo(epochs: int = 8, plot: bool = False) -> None:
    node_ids = ["n1", "n2", "n3", "n4"]
    net = StreamletNetwork(node_ids=node_ids, f=1)

    print("Running Streamlet demo")
    print(f"nodes={node_ids}, f=1, quorum=3, epochs={epochs}")

    epoch_to_block_hash = []
    for e in range(epochs):
        net.step_epoch(e, f"tx{e}".encode())
        # capture the block proposed by leader (if any)
        leader = node_ids[e % len(node_ids)]
        # get any node's view of the proposed block hash at epoch e
        node = net.nodes[leader]
        # find blocks with epoch e
        bh = None
        for h, b in node.blocks.items():
            if b.epoch == e and b.proposer_id == leader:
                bh = h
                break
        epoch_to_block_hash.append(bh)

        # print status
        tips = {nid: max((net.nodes[nid].notarized_blocks or {None}), key=lambda x: (0 if x is None else len(net.nodes[nid].notarizations.get(x, {"voters": set()}).voters))) for nid in node_ids}
        finalized_all = net.finalized_by_all()
        print(f"epoch {e}: leader={leader}, proposed_hash={(bh[:8] if bh else None)}, finalized_common={len(finalized_all)} blocks")

    if plot and go is not None:
        # Build a simple timeline: epochs vs. whether block got notarized/finalized
        epochs_list = list(range(epochs))
        notarized = []
        finalized = []
        any_node = next(iter(net.nodes.values()))
        for e, bh in enumerate(epoch_to_block_hash):
            if bh is None:
                notarized.append(0)
                finalized.append(0)
                continue
            notarized.append(1 if bh in any_node.notarized_blocks else 0)
            finalized.append(1 if bh in net.finalized_by_all() else 0)

        fig = go.Figure()
        fig.add_trace(go.Bar(name="notarized", x=epochs_list, y=notarized))
        fig.add_trace(go.Bar(name="finalized\n(committed)", x=epochs_list, y=finalized))
        fig.update_layout(barmode="group", title="Streamlet: Notarized vs Finalized by Epoch", xaxis_title="Epoch", yaxis_title="Indicator")
        # Write inline HTML and open in browser (non-blocking, no CDN)
        html = pio.to_html(fig, include_plotlyjs="inline", full_html=True)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        with open(tmp.name, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open(Path(tmp.name).as_uri())
    elif plot and go is None:
        print("Plotly not available. Install plotly to enable plotting.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Streamlet demo")
    parser.add_argument("--epochs", type=int, default=8, help="Number of epochs to simulate")
    parser.add_argument("--plot", action="store_true", help="Show simple Plotly visualization")
    args = parser.parse_args()

    run_demo(epochs=args.epochs, plot=args.plot) 