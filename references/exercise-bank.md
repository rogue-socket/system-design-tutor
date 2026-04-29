# Exercise Bank

Catalog of practical exercises by topic. Each entry has prerequisites, what to build, success criteria, common mistakes, and pattern (from `practical-mode.md`).

When the user wants an exercise on topic X, find it here and follow the playbook in `practical-mode.md`. If a topic isn't here, design one using the principles in `practical-mode.md` and consider adding it.

---

## Storage & retrieval

### Build a hash index over a log file
- **Topic**: 1.1 indexing fundamentals
- **Pattern**: A (single-process)
- **Build**: A key-value store that appends writes to a log and keeps an in-memory hash map of `key → byte offset`. Reads do a seek+read.
- **Success**: 100k writes + 10k random reads, all return correct values. Throughput numbers reported.
- **Then break it**: Restart the process — show that the index is gone. Then add startup recovery (replay the log).
- **Then extend**: Add log compaction — merge old segments to drop overwritten keys.
- **Common mistakes**: Using line numbers instead of byte offsets; forgetting to handle deletes (use a tombstone).

### Build a tiny LSM tree
- **Topic**: 1.1 indexing fundamentals
- **Pattern**: A
- **Build**: A memtable (sorted dict), flush-to-SSTable on threshold, read merges memtable + SSTables newest-first.
- **Success**: Reads return the most recent value across all storage levels. Bloom filter (optional extension) reduces disk reads on missing keys.
- **Common mistakes**: Not handling the memtable/SSTable read order; treating SSTables as unsorted.

### Implement a B-tree node split
- **Topic**: 1.1
- **Pattern**: A
- **Build**: B-tree of order N. Insert keys, observe splits at the leaf and propagation up.
- **Success**: After inserting random keys, `print_tree()` shows a balanced tree.
- **Common mistakes**: Off-by-one on the split point; not propagating splits to root.

---

## Replication

### Single-leader replication with async lag
- **Topic**: 2.1
- **Pattern**: B (multiprocessing) or C (asyncio)
- **Build**: One leader process, two follower processes. Writes go to leader, leader async-replicates to followers. Reads can hit any node.
- **Success**: Read-after-write from a follower sometimes returns stale data. Quantify lag.
- **Then break it**: Make the user implement read-your-own-writes — route reads to leader for a window after a write.
- **Common mistakes**: Trying to make replication synchronous before testing the async failure mode (you want them to *feel* the bug first).

### Quorum reads/writes (Dynamo-style)
- **Topic**: 2.2
- **Pattern**: B
- **Build**: 5 nodes, configurable R and W. Writes go to W nodes, reads read from R nodes and pick the latest version.
- **Success**: With R+W>N (e.g., R=3,W=3,N=5) every read sees the latest write. With R+W≤N, demonstrate the stale read.
- **Versioning**: Use vector clocks or timestamps with conflict resolution.
- **Common mistakes**: Naive last-write-wins on equal timestamps drops writes silently.

### Multi-leader conflict resolution
- **Topic**: 2.2
- **Pattern**: B
- **Build**: Two leaders accept concurrent writes to the same key, then sync. User implements LWW, then a CRDT (e.g., G-Counter).
- **Success**: Show concrete cases where LWW loses data and the CRDT preserves it.

---

## Partitioning

### Consistent hashing with virtual nodes
- **Topic**: 3.1
- **Pattern**: A
- **Build**: A `NaiveSharding` class (`hash % N`) and a `ConsistentHashing` class with virtual nodes.
- **Success**: With 100k keys and 10 nodes, naive sharding moves ~50% of keys when adding a node. CH+vnodes moves ~10%.
- **Visualize**: Generate a histogram of keys-per-node — virtual nodes should give much flatter distribution.
- **Common mistakes**: Using Python's `hash()` (randomized per run); forgetting wraparound; too few virtual nodes.

### Hot-key handling
- **Topic**: 3.1 (extension)
- **Pattern**: A
- **Build**: On top of the consistent hashing exercise, simulate a celebrity hot key (one key gets 30% of traffic). Show the imbalance. Then implement key-splitting (replicate the hot key across multiple nodes, randomize on read).
- **Success**: Tail latency on the hot node drops back to baseline.

### Range-partitioned counter with rebalancing
- **Topic**: 3.1
- **Pattern**: B
- **Build**: A counter sharded by user_id range. Add a node — implement rebalancing that splits a range and migrates the data without losing increments in flight.
- **Common mistakes**: Lost writes during migration; double-counting after migration.

---

## Transactions & consistency

### Implement snapshot isolation
- **Topic**: 4.1
- **Pattern**: A
- **Build**: A simple in-memory store with multi-versioned values. Each transaction sees a snapshot from its start time.
- **Success**: Demonstrate a write-skew scenario — show that snapshot isolation allows it. Then bolt on a check that catches it (SSI).

### Two-phase commit with coordinator failure
- **Topic**: 4.3
- **Pattern**: B
- **Build**: A coordinator + 2 participants. Implement the prepare and commit phases.
- **Success**: When the coordinator crashes between phases, participants are stuck holding locks. *That's the lesson.* Then add timeout-based recovery and discuss why it's still imperfect.

### Tiny Raft (educational)
- **Topic**: 4.3
- **Pattern**: B
- **Build**: 3-node Raft with leader election + log replication. Skip the snapshot/membership-change stuff.
- **Success**: Kill the leader — a new one is elected within the timeout window. Logs converge.
- **Heads-up**: This is hard. Set aside 4-6 hours. Ask if they want to scope down to *just* leader election first.

---

## Async / messaging

### Build a queue + worker
- **Topic**: 5.1
- **Pattern**: B
- **Build**: An in-memory queue, a producer, and N workers. At-least-once delivery: workers ack on completion; unacked messages get redelivered after timeout.
- **Success**: Kill a worker mid-job — its message gets picked up by another worker.
- **Then break it**: Show the duplicate-processing problem. Make the user implement idempotency keys.

### Token bucket rate limiter
- **Topic**: 6 reliability
- **Pattern**: A or C
- **Build**: A `RateLimiter` class with `allow(client_id) -> bool`. Refills tokens at a fixed rate.
- **Success**: 1000 requests/sec from one client gets throttled to the configured rate; other clients are unaffected.
- **Then extend**: Make it distributed (Redis-backed) and discuss the race conditions.

### Distributed rate limiter with Redis
- **Topic**: 6 reliability + distributed coordination
- **Pattern**: D (with Redis container) or C with a real Redis
- **Build**: Multiple worker processes share a Redis-backed token bucket using Lua scripts for atomicity.
- **Success**: Total throughput across all workers stays at the configured rate.
- **Common mistakes**: Naive `GET`/`DECR` race; not using Redis transactions or Lua.

---

## Caching deep dives

### Cache stampede (the dogpile problem)
- **Topic**: 7.1
- **Pattern**: C
- **Build**: A cache in front of a slow backend. 1000 concurrent clients all miss simultaneously when the cache expires.
- **Success**: Show that all 1000 hit the backend. Then implement single-flight (only one request goes through, others wait). Then jittered TTLs. Then probabilistic early refresh.
- **Common mistakes**: Implementing single-flight with a global lock that serializes everything.

### Write-through vs write-back vs write-around
- **Topic**: 7.1
- **Pattern**: A
- **Build**: All three caching strategies in front of a "slow disk" simulation.
- **Success**: Measure read latency, write latency, durability under crash.
- **Then break it**: Crash mid-write in write-back mode — data lost. Discuss the trade-off.

---

## Real-time delivery

### WebSocket fan-out
- **Topic**: 7.3
- **Pattern**: C
- **Build**: A simple chat room. N clients connect via WebSocket; messages broadcast to all.
- **Success**: Works for 100 clients on one server.
- **Then extend**: Two server processes. How do messages from clients on server A reach clients on server B? (Pub/sub between servers — Redis or in-memory.)

### Twitter timeline: fan-out on write vs read
- **Topic**: 7.3
- **Pattern**: A
- **Build**: Simulate users with followers (skewed distribution — most users have <100, a few have millions). Implement both:
  - Fan-out on write: post → push to every follower's timeline
  - Fan-out on read: post → store; on timeline read, fetch from all followed users and merge
- **Success**: Measure write latency and read latency under both. Identify the celebrity problem in fan-out-on-write.
- **Then synthesize**: Hybrid (fan-out on write for normal users, fan-out on read for celebrities).

---

## Classic system designs (full builds)

These are weekend-scale projects. Each integrates many topics. Use them when the user has time and wants integration practice.

### URL shortener
- **Tests**: ID generation (counter? base62? hash?), sharding, caching, analytics counter
- **Build**: HTTP server + DB + cache. Generate short URLs, redirect, count clicks.
- **Stretch**: Replace single-process counter with a distributed one.

### Distributed cache from scratch
- **Tests**: Consistent hashing, replication, eviction, client-side routing
- **Build**: Multi-process cache cluster with a smart client.

### Geospatial nearby search
- **Tests**: Geohashing or quad-tree, indexing, query patterns
- **Build**: "Find restaurants within 1km" using a geohash index.

### Web crawler
- **Tests**: BFS at scale, dedup, politeness (per-host rate limiting), distributed coordination
- **Build**: Multi-worker crawler with a shared frontier, robots.txt respect, dedup on URL hash.

### Search autocomplete
- **Tests**: Trie, ranking, real-time updates
- **Build**: Index a million terms, autocomplete with prefix + frequency ranking, sub-50ms latency.

---

## How to suggest exercises

When the user asks "give me an exercise" or "let me practice X":

1. Check `progress.json` for completed exercises and weak spots.
2. Pick something matching their current topic, prerequisites met, that they haven't done.
3. State the time estimate honestly: "This is ~2 hours including the experiment."
4. Confirm scope: "We can do the basic version (1 hour) or include failure injection (3 hours). Which?"
5. Set it up using `practical-mode.md`.
