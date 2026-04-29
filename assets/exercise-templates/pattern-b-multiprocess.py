"""
{{EXERCISE_TITLE}}

Pattern B: multi-process. Use this when you need true OS-level concurrency
(leader election, distributed locks, consensus, etc.)

Run:
    python run_cluster.py

Each process logs with a prefix so you can read the interleaving.
"""

import multiprocessing as mp
import time
from queue import Empty


def node_worker(node_id, in_queue, out_queue, peers):
    """
    A single node in the cluster.

    Args:
        node_id: this node's identifier
        in_queue: messages to this node
        out_queue: messages this node sends out (the orchestrator routes them)
        peers: list of other node_ids
    """
    log = lambda msg: print(f"[{time.time():.3f}] [node-{node_id}] {msg}", flush=True)
    log("started")

    # TODO: node state goes here
    state = {}

    while True:
        try:
            msg = in_queue.get(timeout=0.1)
        except Empty:
            # TODO: heartbeat / timeout logic here
            continue

        if msg is None:
            log("shutting down")
            return

        # TODO: handle incoming message
        log(f"received {msg}")


def run_cluster(num_nodes=3):
    queues = {i: mp.Queue() for i in range(num_nodes)}
    processes = []

    for i in range(num_nodes):
        peers = [j for j in range(num_nodes) if j != i]
        # NOTE: simple version: each node has its own inqueue, no central router.
        # For node-to-node messages, processes write directly to peers' queues.
        # Pass the dict of all queues so nodes can send to each other.
        p = mp.Process(target=node_worker, args=(i, queues[i], queues, peers))
        p.start()
        processes.append(p)

    # TODO: orchestrator logic — inject events, kill nodes, observe
    time.sleep(5)

    # Shutdown
    for q in queues.values():
        q.put(None)
    for p in processes:
        p.join()


if __name__ == "__main__":
    run_cluster(num_nodes=3)
