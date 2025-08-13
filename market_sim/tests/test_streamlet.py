import pytest

from core.consensus.streamlet import StreamletNetwork


@pytest.mark.unit
def test_notarization_threshold():
    net = StreamletNetwork(node_ids=["n1", "n2", "n3", "n4"], f=1)
    # epoch 0 leader n1
    net.step_epoch(0, b"tx0")
    # All honest nodes vote; notarization should exist in each node for the proposed block
    for node in net.nodes.values():
        assert len(node.notarized_blocks) >= 1


@pytest.mark.unit
def test_finalization_three_consecutive_epochs():
    net = StreamletNetwork(node_ids=["n1", "n2", "n3", "n4"], f=1)
    # Create three consecutive notarized blocks (epochs 0,1,2)
    for e in range(3):
        net.step_epoch(e, f"tx{e}".encode())
    # After epoch 2, the middle block (epoch 1) should be finalized in all nodes
    finalized_common = net.finalized_by_all()
    assert len(finalized_common) >= 1
    # Check at least one block with epoch 1 is finalized by all
    epochs = {net.nodes[next(iter(net.nodes))].blocks[h].epoch for h in finalized_common}
    assert 1 in epochs


@pytest.mark.unit
def test_consistency_of_finalized_prefix():
    net = StreamletNetwork(node_ids=["n1", "n2", "n3", "n4"], f=1)
    for e in range(6):
        net.step_epoch(e, f"tx{e}".encode())
    # All nodes should share a common finalized prefix (non-empty)
    common = net.finalized_by_all()
    assert len(common) > 0
    # And no two nodes finalize conflicting blocks at the same height
    by_height_per_node = []
    for node in net.nodes.values():
        pairs = {}
        for h in node.finalized:
            blk = node.blocks[h]
            pairs[blk.epoch] = h
        by_height_per_node.append(pairs)
    # For each epoch present in any finalized set, all nodes agree on the hash
    all_epochs = set().union(*[set(p.keys()) for p in by_height_per_node])
    for ep in all_epochs:
        vals = {p.get(ep) for p in by_height_per_node if ep in p}
        assert len(vals) <= 1 