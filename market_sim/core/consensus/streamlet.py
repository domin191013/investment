from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from hashlib import sha256

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from core.consensus.crypto import Ed25519KeyPair, verify_signature, serialize_public_key


@dataclass(frozen=True)
class Block:
    parent_hash: str
    epoch: int
    proposer_id: str
    payload: bytes = b""

    def hash(self) -> str:
        m = sha256()
        m.update(self.parent_hash.encode("utf-8"))
        m.update(self.epoch.to_bytes(8, "big"))
        m.update(self.proposer_id.encode("utf-8"))
        m.update(self.payload)
        return m.hexdigest()


@dataclass
class Vote:
    block_hash: str
    epoch: int
    voter_id: str
    signature: bytes


@dataclass
class Notarization:
    block_hash: str
    epoch: int
    voters: Set[str] = field(default_factory=set)


@dataclass
class Node:
    node_id: str
    keys: Ed25519KeyPair
    public_keys: Dict[str, Ed25519PublicKey]
    f: int

    # local view
    blocks: Dict[str, Block] = field(default_factory=dict)
    parent_of: Dict[str, Optional[str]] = field(default_factory=dict)
    notarized_blocks: Set[str] = field(default_factory=set)
    votes_seen: Dict[Tuple[str, str], Vote] = field(default_factory=dict)  # (block_hash, voter_id) -> Vote
    notarizations: Dict[str, Notarization] = field(default_factory=dict)
    finalized: Set[str] = field(default_factory=set)

    def genesis_hash(self) -> str:
        return "GENESIS"

    def longest_notarized_chains(self) -> List[List[str]]:
        # Reconstruct chains ending at notarized tips and keep the longest
        chains: List[List[str]] = []
        max_len = 0
        for bh in self.notarized_blocks:
            chain = []
            cur = bh
            while cur and cur in self.blocks:
                chain.append(cur)
                cur = self.parent_of.get(cur)
            if cur == self.genesis_hash() or cur is None:
                length = len(chain)
                if length > max_len:
                    max_len = length
                    chains = [list(reversed(chain))]
                elif length == max_len:
                    chains.append(list(reversed(chain)))
        return chains if chains else []

    def get_quorum(self) -> int:
        return 2 * self.f + 1

    def leader_for_epoch(self, epoch: int, node_ids: List[str]) -> str:
        # deterministic round-robin
        return node_ids[epoch % len(node_ids)]

    def propose(self, epoch: int, node_ids: List[str], payload: bytes = b"") -> Optional[Block]:
        leader = self.leader_for_epoch(epoch, node_ids)
        if leader != self.node_id:
            return None
        # choose parent = tip of any longest notarized chain in local view (or genesis)
        chains = self.longest_notarized_chains()
        parent_hash = chains[-1][-1] if chains else self.genesis_hash()
        blk = Block(parent_hash=parent_hash, epoch=epoch, proposer_id=self.node_id, payload=payload)
        bh = blk.hash()
        self.blocks[bh] = blk
        self.parent_of[bh] = parent_hash if parent_hash != self.genesis_hash() else None
        return blk

    def sign_vote(self, block_hash: str, epoch: int) -> Vote:
        msg = f"{block_hash}:{epoch}:{self.node_id}".encode("utf-8")
        sig = self.keys.sign(msg)
        return Vote(block_hash=block_hash, epoch=epoch, voter_id=self.node_id, signature=sig)

    def can_vote_for(self, blk: Block) -> bool:
        # Vote for first proposal seen in epoch iff it extends one of the longest notarized chains seen
        # and we haven't already voted this epoch
        if any(k[1] == self.node_id and self.blocks[k[0]].epoch == blk.epoch for k in self.votes_seen.keys() if k[0] in self.blocks):
            return False
        if blk.epoch < 0:
            return False
        # check it extends a longest notarized chain tip
        chains = self.longest_notarized_chains()
        if not chains:
            # allow any first block extending genesis
            return blk.parent_hash == self.genesis_hash() or blk.parent_hash not in self.blocks
        longest_tips = {c[-1] for c in chains}
        return blk.parent_hash in longest_tips

    def observe_proposal(self, blk: Block) -> Optional[Vote]:
        bh = blk.hash()
        self.blocks[bh] = blk
        self.parent_of[bh] = blk.parent_hash if blk.parent_hash != self.genesis_hash() else None
        if self.can_vote_for(blk):
            vote = self.sign_vote(bh, blk.epoch)
            self.votes_seen[(bh, self.node_id)] = vote
            return vote
        return None

    def observe_vote(self, vote: Vote) -> Optional[Notarization]:
        # Verify signature
        pub = self.public_keys.get(vote.voter_id)
        if not pub:
            return None
        msg = f"{vote.block_hash}:{vote.epoch}:{vote.voter_id}".encode("utf-8")
        if not verify_signature(pub, msg, vote.signature):
            return None
        # Track vote
        key = (vote.block_hash, vote.voter_id)
        if key in self.votes_seen:
            return None
        self.votes_seen[key] = vote
        # Aggregate notarization
        notz = self.notarizations.get(vote.block_hash)
        if not notz:
            notz = Notarization(block_hash=vote.block_hash, epoch=vote.epoch, voters=set())
            self.notarizations[vote.block_hash] = notz
        notz.voters.add(vote.voter_id)
        if len(notz.voters) >= self.get_quorum():
            self.notarized_blocks.add(vote.block_hash)
            self._try_finalize(vote.block_hash)
            return notz
        return None

    def _try_finalize(self, tip_hash: str) -> None:
        # Finalize the middle of three consecutive notarized blocks in a notarized chain
        # Walk back from tip to gather three consecutive epochs
        chain: List[str] = []
        cur = tip_hash
        while cur in self.blocks and len(chain) < 3:
            if cur not in self.notarized_blocks:
                return
            chain.append(cur)
            cur = self.parent_of.get(cur)
        if len(chain) < 3:
            return
        b3, b2, b1 = chain  # b3 newest
        blk3, blk2, blk1 = self.blocks[b3], self.blocks[b2], self.blocks[b1]
        if blk3.epoch == blk2.epoch + 1 and blk2.epoch == blk1.epoch + 1:
            # finalize b2 and its ancestors
            cur = b2
            while cur is not None and cur in self.blocks and cur not in self.finalized:
                self.finalized.add(cur)
                cur = self.parent_of.get(cur)


class StreamletNetwork:
    def __init__(self, node_ids: List[str], f: int = 1):
        self.node_ids = node_ids
        self.f = f
        self.nodes: Dict[str, Node] = {}
        # key distribution
        keypairs: Dict[str, Ed25519KeyPair] = {nid: Ed25519KeyPair.generate() for nid in node_ids}
        pubs = {nid: kp.public_key for nid, kp in keypairs.items()}
        for nid in node_ids:
            self.nodes[nid] = Node(node_id=nid, keys=keypairs[nid], public_keys=pubs, f=f)

    def step_epoch(self, epoch: int, payload: bytes = b"") -> None:
        leader = self.node_ids[epoch % len(self.node_ids)]
        proposal = self.nodes[leader].propose(epoch, self.node_ids, payload)
        if not proposal:
            return
        # broadcast proposal and gather votes
        votes: List[Vote] = []
        for nid, node in self.nodes.items():
            vote = node.observe_proposal(proposal)
            if vote:
                votes.append(vote)
        # broadcast votes
        for vote in votes:
            for node in self.nodes.values():
                node.observe_vote(vote)

    def finalized_by_all(self) -> Set[str]:
        common = None
        for node in self.nodes.values():
            fs = node.finalized
            common = fs if common is None else common.intersection(fs)
        return common or set() 