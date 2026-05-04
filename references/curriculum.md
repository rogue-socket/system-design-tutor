# Curriculum

Topic tree for system design, mapped to **Designing Data-Intensive Applications (DDIA)** and **The System Design Primer**. Use this when planning a learning path, checking prerequisites, or deciding what to teach next.

## How to use this file

- Topics are listed in **rough learning order**. Skip what the user already knows; never teach a topic before its prerequisites unless the user explicitly opts in.
- Each topic has: prereqs, DDIA reference, Primer reference, key concepts, and "you understand this when..." criteria.
- When a user asks "what should I learn next?", check `progress.json` for completed topics, then suggest the earliest unmet topic with all prereqs satisfied.
- When a user asks for a topic out of order ("teach me quorum reads" before they've done replication), warn them: "This depends on async replication. Want to cover that first, or push through?"

---

## Tier 0: Foundations (assume known, but verify)

**Verify with one quick question per topic, don't lecture.**

- **Load balancers (L4 vs L7)** — Primer §Load Balancer
- **Forward vs reverse proxy** — Primer §Reverse Proxy
- **CDN basics** — Primer §CDN
- **DNS** — Primer §DNS
- **SQL vs NoSQL trade-offs** — DDIA Ch 2; Primer §SQL or NoSQL
- **HTTP, TCP/UDP basics** — Primer §Communication
- **Single-node caching (in-process, Redis/Memcached)** — Primer §Cache

---

## Tier 1: Storage & retrieval (single node)

### 1.1 Indexing fundamentals
- **Prereqs**: SQL basics
- **DDIA**: Ch 3 (Storage and Retrieval) — pp. 70-79 on hash indexes, SSTables, LSM-trees, B-trees
- **Concepts**: hash indexes, SSTables, LSM-trees, B-trees, write amplification, compaction
- **Understands when they can**: explain why LSM-trees write fast and read slow; explain bloom filters' role in LSM reads; reason about which to pick for a given workload.

### 1.2 OLTP vs OLAP, column stores
- **Prereqs**: 1.1
- **DDIA**: Ch 3 pp. 90-101
- **Concepts**: row-oriented vs column-oriented storage, data warehousing, star schema
- **Understands when they can**: explain why analytics queries on row stores are slow and how column stores fix that.

### 1.3 Data encoding & evolution
- **Prereqs**: SQL basics
- **DDIA**: Ch 4
- **Concepts**: JSON/XML/binary formats, Protocol Buffers, Avro, Thrift, schema evolution, backward/forward compatibility
- **Understands when they can**: explain what happens when an old service reads data written by a new service.

---

## Tier 2: Replication

### 2.1 Single-leader replication
- **Prereqs**: storage basics
- **DDIA**: Ch 5 pp. 151-162
- **Primer**: §Database — Replication
- **Concepts**: sync vs async, replication lag, read-your-own-writes, monotonic reads, follower failover, split brain
- **Understands when they can**: explain why async replication can violate read-your-own-writes; design a system that prevents it.

### 2.2 Multi-leader & leaderless replication
- **Prereqs**: 2.1
- **DDIA**: Ch 5 pp. 168-186
- **Concepts**: multi-datacenter writes, conflict resolution (LWW, CRDTs), Dynamo-style quorum (R + W > N), read repair, anti-entropy, sloppy quorum, hinted handoff
- **Understands when they can**: derive why R + W > N gives strong consistency; explain when it breaks.

---

## Tier 3: Partitioning (sharding)

### 3.1 Partitioning strategies
- **Prereqs**: 2.1
- **DDIA**: Ch 6 pp. 199-218
- **Primer**: §Database — Federation, Sharding
- **Concepts**: range-based, hash-based, consistent hashing, virtual nodes, hot keys, rebalancing strategies
- **Understands when they can**: walk through what happens when you add a node under each strategy; explain why consistent hashing exists.

### 3.2 Secondary indexes & request routing
- **Prereqs**: 3.1
- **DDIA**: Ch 6 pp. 218-225
- **Concepts**: local (document-partitioned) vs global (term-partitioned) secondary indexes, scatter/gather, ZooKeeper for routing
- **Understands when they can**: explain the read amplification of scatter/gather and when each index style wins.

---

## Tier 4: Transactions & consistency

### 4.1 Transactions
- **Prereqs**: SQL basics
- **DDIA**: Ch 7
- **Concepts**: ACID, isolation levels (read committed, snapshot isolation/MVCC, serializable), lost updates, write skew, phantoms
- **Understands when they can**: give a concrete example of write skew and explain why snapshot isolation doesn't prevent it.

### 4.2 Trouble with distributed systems
- **Prereqs**: 2.x, 3.x
- **DDIA**: Ch 8
- **Concepts**: partial failures, unreliable networks, unreliable clocks, GC pauses, fencing tokens, Byzantine vs non-Byzantine
- **Understands when they can**: explain why you can't trust timestamps for ordering, and what fencing tokens fix.

### 4.3 Consistency & consensus
- **Prereqs**: 4.1, 4.2
- **DDIA**: Ch 9
- **Concepts**: linearizability, ordering guarantees, total order broadcast, distributed transactions, 2PC, consensus (Paxos/Raft), CAP, PACELC
- **Understands when they can**: distinguish linearizability from serializability; explain what 2PC's coordinator failure mode is.

---

## Tier 5: Async, messaging, streaming

### 5.1 Message queues
- **Prereqs**: 2.1
- **Primer**: §Asynchronism
- **Concepts**: queue vs pub/sub, at-most-once / at-least-once / exactly-once, idempotency keys, dead-letter queues, ordering guarantees, when to use SQS vs Kafka vs RabbitMQ
- **Understands when they can**: explain why "exactly-once" is mostly a lie and how idempotency keys give the same effect.

### 5.2 Stream processing
- **Prereqs**: 5.1
- **DDIA**: Ch 11
- **Concepts**: log-based messaging (Kafka), stream-stream joins, stream-table joins, windowing, watermarks, backpressure
- **Understands when they can**: explain why Kafka uses a log instead of a queue and what that buys you.

### 5.3 Batch processing
- **Prereqs**: 5.2
- **DDIA**: Ch 10
- **Concepts**: MapReduce model, joins in MapReduce (sort-merge, broadcast hash, partitioned hash), output of batch jobs

---

## Tier 6: Reliability & operability

**Primary sources for Tier 6** (DDIA only goes so far on operability):
- *Site Reliability Engineering* (Beyer et al., Google) — sre.google/books
- *The Site Reliability Workbook* (Beyer et al., Google) — sre.google/books
- *Release It!* 2nd ed. (Nygard) — for resilience patterns
- *Production-Ready Microservices* (Fowler) — for the org/operational lens
- *Observability Engineering* (Majors, Fong-Jones, Miranda) — for the three pillars done well

Per-item references:

- **Circuit breakers** — exponential backoff with jitter. Nygard, *Release It!* Ch 5; Hystrix design docs.
- **Retries**: idempotency requirement, retry storms. AWS Architecture Blog "Exponential Backoff And Jitter"; *SRE Workbook* Ch 22 (Addressing Cascading Failures).
- **Timeouts** — every network call needs one. Nygard, *Release It!* Ch 4; Google SRE Book Ch 22.
- **Bulkheads** — isolation of failure domains. Nygard, *Release It!* Ch 5.
- **Rate limiting**: token bucket, leaky bucket, sliding window. Stripe Engineering "Scaling your API with rate limiters"; Cloudflare "How we built rate limiting capable of scaling to millions of domains".
- **Graceful degradation** — fallbacks, feature flags. Fowler, *Production-Ready Microservices* Ch 5; LaunchDarkly engineering blog.
- **SLA / SLO / SLI** — error budgets. *SRE Workbook* Ch 1-3; Google SRE Book Ch 4.
- **Chaos engineering** — failure injection. Netflix tech blog (Chaos Monkey); Rosenthal et al., *Chaos Engineering* (O'Reilly).
- **Observability**: metrics, logs, traces (the three pillars), correlation IDs. Majors, Fong-Jones, Miranda, *Observability Engineering*; OpenTelemetry docs.

Primer also relevant: §Performance vs scalability, §Availability vs consistency.

---

## Tier 7: Specialized systems & deep dives

### 7.1 Caching deep dive
- write-through, write-back, write-around
- cache stampede / dogpile (single-flight, jittered TTLs, probabilistic early expiration)
- cache invalidation strategies, the two hard problems
- materialized views

### 7.2 Search systems
- inverted indexes, tokenization, stemming, BM25
- Elasticsearch / Lucene basics
- when to use search vs SQL `LIKE`

### 7.3 Real-time delivery
- WebSockets vs SSE vs long-polling
- push vs pull
- fan-out on write vs read (Twitter timeline trade-offs)
- presence systems

### 7.4 Geo-distribution
- multi-region active-active vs active-passive
- GeoDNS, anycast
- latency budgets, edge compute
- global vs regional consistency

### 7.5 Storage specialties
- object storage (S3 model: eventually consistent listings, strong on get-after-put)
- time-series databases (InfluxDB, Prometheus)
- graph databases
- blob CDNs

---

## Tier 8: Classic system designs (practice problems)

These are not topics — they're integration tests for everything above. Pick one and run a mock interview. The exercise bank (`references/exercise-bank.md`) maps each to the topics it tests.

- URL shortener (sharding, caching, ID generation)
- Pastebin (object storage, CDN)
- Twitter feed (fan-out trade-offs, timeline gen)
- Instagram (photo storage, CDN, feed)
- WhatsApp / chat (real-time, message delivery, presence)
- Uber / Lyft dispatch (geospatial indexing, real-time matching)
- Dropbox / Google Drive (chunking, dedup, sync, versioning)
- YouTube (video pipeline, CDN, transcoding)
- Distributed cache from scratch (consistent hashing, replication)
- Rate limiter (token bucket, distributed coordination)
- Web crawler (politeness, dedup, distributed BFS)
- Search autocomplete (trie, ranking, real-time updates)
- Distributed counter (sharded counter, eventual aggregation)
- Ad click aggregator (stream processing, exactly-once-ish)
- Google Maps / nearby (geohashing, quad trees, S2)
- Tinder (matching, geospatial, pagination)
- Ticket booking (reservation, double-booking prevention, locking)
- Payment processing (idempotency, sagas, audit log)

---

## Path suggestions by goal

If the user states a goal, recommend a path:

- **"Interview prep, FAANG-level"**: Tier 0 verify → 2.x → 3.x → 4.3 (CAP + consensus, lighter on consensus internals) → 5.1 → 6 (reliability essentials) → 8 (heavy on classic designs)
- **"Build production systems"**: Tier 0 verify → 1.x → 2.x → 4.1 → 5.x → 6 → 7.1 (caching is high-value)
- **"Just learn it well"**: Linear, tier by tier. This is the DDIA path.
- **"I keep hitting concurrency bugs"**: Jump to 4.1 (transactions, isolation) and 4.2 (distributed trouble), then back-fill.

---

## The default ordered course path

When the skill is in Claude-driven mode and needs to pick "what's next" without explicit user direction, use this ordered list. **The skill walks this path top-to-bottom**, skipping items the user has already mastered (status: complete, confidence ≥ 4) and substituting equivalent topics if the user explicitly redirected.

Each step is one **unit of work** — roughly one session, sometimes two for heavy topics. The unit type is in brackets: `[T]` = theory, `[E]` = practical exercise, `[M]` = mock interview, `[R]` = review/integration session.

```
=== FOUNDATIONS (verify, don't lecture) ===
F1.  [T]  Foundations check — quick probe of LB, proxy, CDN, DNS, SQL/NoSQL trade-offs
F2.  [T]  HTTP/TCP basics + idempotency

=== STORAGE & RETRIEVAL (Tier 1) ===
S1.  [T]  Hash indexes, SSTables, LSM-trees vs B-trees (DDIA Ch 3)
S2.  [E]  Build a hash index over a log file (Pattern A)
S3.  [T]  OLTP vs OLAP, column stores
S4.  [T]  Data encoding & schema evolution (DDIA Ch 4)

=== REPLICATION (Tier 2) ===
R1.  [T]  Single-leader replication, sync vs async, replication lag (DDIA Ch 5)
R2.  [E]  Single-leader replication with async lag (Pattern B/C)
R3.  [T]  Read-your-own-writes, monotonic reads, follower failover, split brain
R4.  [T]  Multi-leader & leaderless replication, R+W>N
R5.  [E]  Quorum reads/writes (Dynamo-style) (Pattern B)
R6.  [R]  Replication review session

=== PARTITIONING (Tier 3) ===
P1.  [T]  Partitioning strategies — range, hash, consistent hashing (DDIA Ch 6)
P2.  [E]  Consistent hashing with virtual nodes (Pattern A)
P3.  [T]  Hot keys, secondary indexes, scatter/gather
P4.  [E]  Hot-key handling extension on the CH exercise
P5.  [M]  Mock interview: URL shortener (integrates S1, P1, P2 + caching basics)

=== TRANSACTIONS & CONSISTENCY (Tier 4) ===
C1.  [T]  Transactions, ACID, isolation levels (DDIA Ch 7)
C2.  [E]  Implement snapshot isolation
C3.  [T]  Trouble with distributed systems (DDIA Ch 8)
C4.  [T]  Linearizability, ordering, consensus, CAP, PACELC (DDIA Ch 9)
C5.  [E]  Two-phase commit with coordinator failure (Pattern B)
C6.  [E]  Tiny Raft (leader election only) (Pattern B) — heads-up: long
C7.  [R]  Consistency review session

=== ASYNC & MESSAGING (Tier 5) ===
A1.  [T]  Message queues, at-least-once vs at-most-once, idempotency
A2.  [E]  Build a queue + worker with idempotency keys (Pattern B)
A3.  [T]  Stream processing, Kafka log model (DDIA Ch 11)
A4.  [T]  Batch processing fundamentals

=== RELIABILITY (Tier 6) ===
RL1. [T]  Circuit breakers, retries with backoff + jitter, timeouts, bulkheads
RL2. [E]  Token bucket rate limiter (Pattern A)
RL3. [E]  Distributed rate limiter with Redis (Pattern D)
RL4. [T]  SLA / SLO / SLI, error budgets, observability

=== CACHING DEEP DIVE (Tier 7.1) ===
CA1. [T]  Caching strategies, stampede prevention
CA2. [E]  Cache stampede + single-flight (Pattern C)
CA3. [M]  Mock interview: distributed cache from scratch

=== REAL-TIME (Tier 7.3) ===
RT1. [T]  WebSockets, SSE, push vs pull
RT2. [E]  WebSocket fan-out (Pattern C)
RT3. [T]  Twitter timeline: fan-out on write vs read
RT4. [E]  Twitter fan-out simulation
RT5. [M]  Mock interview: WhatsApp / chat system

=== STORAGE SPECIALTIES (Tier 7.2, 7.5) ===
ST1. [T]  Search systems, inverted indexes
ST2. [T]  Object storage model (S3), CDN integration
ST3. [T]  Time-series DBs

=== GEO-DISTRIBUTION (Tier 7.4) ===
G1.  [T]  Multi-region active-active vs active-passive
G2.  [T]  Latency budgets, edge compute

=== INTEGRATION & PRACTICE (Tier 8) ===
I1.  [M]  Mock interview: Uber / Lyft dispatch
I2.  [M]  Mock interview: Dropbox / Google Drive
I3.  [M]  Mock interview: YouTube / video pipeline
I4.  [M]  Mock interview: Web crawler
I5.  [M]  Mock interview: Geospatial nearby search
I6.  [R]  Final synthesis session
```

### How to use this path

- **Track position in `progress.json`** under `course_position` (the step ID, e.g. "P3").
- **Walking the path**: when the current step is done, advance to the next step that isn't already mastered.
- **Adapting the path**: if the user redirects ("I want to focus on caching"), jump to that section but plan a return. Note the deviation in `session-state.md` so you can come back.
- **Spaced repetition is interleaved**: SR review sessions happen *before* the next path step, not as a separate track.
- **Review sessions [R]**: triggered automatically every 3-5 path steps, or when SR queue is heavy.

Don't walk the path mechanically. If diagnostic showed the user has solid replication knowledge but weak partitioning, skip R1-R3 to spot-check, then dive into P1.

---

## Practical Coverage Standard (must-hit)

Because practical work is the core of this course, enforce this minimum exercise coverage before calling the course "complete":

- Tier 1 (storage): at least 1 completed exercise
- Tier 2 (replication): at least 2 completed exercises
- Tier 3 (partitioning): at least 2 completed exercises
- Tier 4 (transactions/consistency): at least 2 completed exercises
- Tier 5 (async/messaging): at least 1 completed exercise
- Tier 6 (reliability): at least 2 completed exercises
- Tier 7 (specialized deep dives): at least 2 completed exercises
- Tier 8 (integration): at least 3 mock interviews or full builds

Required concept checkpoints (must have at least one hands-on artifact each):
- consistent hashing / partition movement
- replication lag or stale-read behavior
- idempotency under at-least-once delivery
- distributed rate limiting
- one failure-injection exercise (node kill, network fault, hot key, retry storm)

If the learner progresses through theory but misses these, propose practical sessions before advancing further.
