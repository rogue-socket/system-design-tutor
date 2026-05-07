# Builder-mode anchor projects

This file defines the three anchor projects used by Builder-mode traversal of the curriculum (see `SKILL.md` § Step 1.5 and the `in-project` mode in Step 2). Each project is a **system the user designs and partially builds** — not a free-form sandbox. The project provides the spine; foundations from `references/curriculum.md` get unlocked just-in-time as the design hits them.

Three projects together cover the full curriculum surface. After all three are done, the user is at Foundation-track graduation parity and runs Tier 8 mocks for breadth.

## How Builder mode uses this file

1. After the diagnostic, propose a project based on diagnostic strength and user goal.
2. Pick a difficulty tier (easy / medium / hard) — never gate, always adapt.
3. Walk milestones in order. At each milestone, identify the curriculum topics it requires; if any aren't in `progress.json.topics` with `status: complete`, route into Foundation lessons for those topics, then return to the project.
4. Every 2-3 milestones, inject a stress scenario from the project's stress list. Track delivered injections in `progress.json.current_project.stress_injections_done` to avoid repeats.
5. At project end, run a synthesis review and update `progress.json` with all topics touched. Append the project entry to `completed_projects`. Offer the next project.

## Difficulty philosophy

Each project has three pre-calibrated tiers (easy / medium / hard) that vary **scope** and **scale knobs**, not foundational rigor. A beginner doing the easy URL shortener still encounters real LSM-vs-B-tree and cache-invalidation reasoning — just at lower scale and without multi-region. Difficulty is "how many milestones" + "what scale numbers", not "skip the hard concepts."

If the user says "make this harder" mid-project, jump scale knobs (1k → 10k QPS) or pull in the next milestone early. If "make this easier", drop the next stress injection or shrink the scale. Update `current_project.difficulty` in `progress.json` only on explicit tier changes.

---

## Project 1: URL shortener at scale

**Premise**: Build a URL shortener that takes long URLs, returns short codes, and redirects on access. Survive going viral.

**Project ID**: `url-shortener`
**Coverage**: Tiers 0–4, 6, 7.1.
**Best fit when**: diagnostic shows mid-strength on storage/caching, or goal is `interview-prep`.
**Anti-fit**: skip if diagnostic shows the user already designs systems at this scale daily — propose Project 3 instead.

### Difficulty knobs

| Tier | Scale | Region | Stop after milestone |
|---|---|---|---|
| Easy | 1k QPS | Single | 4 |
| Medium | 10k QPS, with HA | Single | 6 |
| Hard | 100k QPS | Multi-region | 8 |

### Milestones

| # | Milestone | Curriculum topics unlocked |
|---|---|---|
| 1 | Single-instance MVP: encode → store → redirect | F1, F2; SQL/KV trade-off (Tier 0) |
| 2 | Scale reads with caching (Redis) | Tier 0 cache, 7.1 (CA1) |
| 3 | Scale writes with sharding + ID generation | S1, P1, P2, 3.1 |
| 4 | Hot-key & cache-stampede handling | P3, CA2 |
| 5 | Rate limiting (abuse prevention) | RL2, RL3 |
| 6 | Replication for durability/HA, follower failover | R1, R3 |
| 7 | Multi-region: geo-routing, cross-region replication | G1, R4 (multi-leader/leaderless) |
| 8 | Click analytics pipeline (async ingest, aggregation) | A1, A2, A3 |

### Stress injections

- **`hot-key`**: one URL goes viral; show what happens to the shard. Force them to reason about cache stampede + read replicas.
- **`cache-eviction-storm`**: Redis evicts 30% of entries — what's the recovery profile?
- **`replica-lag-failover`**: primary dies mid-write; what does the user see?
- **`cross-region-partition`** (hard tier only): regions can't talk for 2 minutes. Writes accepted in both — what happens at heal?

### "Done" criteria

User can: (a) defend their storage choice with numbers, (b) walk through a hot-key incident response, (c) explain why their replication strategy fits the consistency requirements, (d) at hard tier, articulate the multi-region trade-off.

---

## Project 2: Chat backend with presence + history

**Premise**: Build a chat system supporting 1:1 and group messaging, with online presence indicators and persistent message history.

**Project ID**: `chat-backend`
**Coverage**: Tiers 2–5, 6, 7.3.
**Best fit when**: diagnostic shows user reasons well about partitioning but is shaky on ordering/consistency, or goal is `concurrency-bugs`.
**Anti-fit**: skip if user has shipped chat infrastructure at scale.

### Difficulty knobs

| Tier | Concurrent users | Features | Stop after milestone |
|---|---|---|---|
| Easy | 100 | 1:1 only, basic history | 2 |
| Medium | 10k | Group chats, presence, ordering guarantees | 6 |
| Hard | 1M | Multi-region, exactly-once-style delivery | 8 |

### Milestones

| # | Milestone | Curriculum topics unlocked |
|---|---|---|
| 1 | 1:1 messaging MVP over WebSocket | RT1, F2 |
| 2 | Persistent message history; storage choice | S1, S3 (encoding) |
| 3 | Group chats: fan-out on write vs read | RT3, RT4 |
| 4 | Presence system (heartbeats, last-seen) | RT1, distributed state basics |
| 5 | Connection sharding (gateway by user_id) | P1, P3 |
| 6 | Message ordering & delivery guarantees | A1, A2, RL1 |
| 7 | Replication & follower reads for history | R1, R3 |
| 8 | Ephemeral lane: typing/receipts via stream | A3 |

### Stress injections

- **`reconnect-storm`**: gateway restarts; 10k clients reconnect simultaneously.
- **`hot-group`**: a 100k-member group sends messages 10/sec — what's the fan-out cost?
- **`presence-flap`**: poor mobile network causes presence to flicker — does your system handle it without thundering broadcasts?
- **`out-of-order-delivery`** (medium+): network reorders two messages in the same conversation. What does the user see?

### "Done" criteria

User can: (a) defend their fan-out choice with a math justification, (b) walk through an ordering-violation scenario and how their design prevents it, (c) explain presence trade-offs (push vs pull), (d) at hard tier, reason about cross-region message routing.

---

## Project 3: Metrics pipeline at scale

**Premise**: Build a telemetry ingestion service: clients send metrics, the system ingests, stores, and serves queries against time-windowed aggregates.

**Project ID**: `metrics-pipeline`
**Coverage**: Tiers 1.2, 5–8.
**Best fit when**: diagnostic shows user reasons about queues + storage but hasn't dealt with stream processing or backpressure, or goal is `production`.
**Anti-fit**: skip if the user's day job is observability infra.

### Difficulty knobs

| Tier | Throughput | Tenants | Stop after milestone |
|---|---|---|---|
| Easy | 1k events/sec | Single | 3 |
| Medium | 10k events/sec | Multi-tenant | 6 |
| Hard | 1M events/sec | Multi-tenant + SLAs | 8 |

### Milestones

| # | Milestone | Curriculum topics unlocked |
|---|---|---|
| 1 | Single-tenant ingest endpoint + naive store | F2, S1 |
| 2 | Time-series storage (LSM-friendly) | ST3, S1, 7.5 |
| 3 | Async ingest with queue (durability boundary) | A1, A2 (idempotency keys) |
| 4 | Stream aggregation: windowing, watermarks, downsampling | A3 (stream processing) |
| 5 | Multi-tenant isolation: rate limits, quotas, bulkheads | RL3, Tier 6 bulkheads |
| 6 | Backpressure & retention policies | A3, A4 (batch), 7.5 |
| 7 | Hot-tier vs cold-tier query path | 1.2 (column stores), 7.5 |
| 8 | Observability of the pipeline itself (USE/RED) | RL4 |

### Stress injections

- **`ingest-burst`**: traffic spikes for 5 minutes — does buffering hold or does the queue fill?
- **`slow-storage`**: writes start taking 500ms. What does the ingest path do?
- **`hot-tenant`**: one tenant sends 50% of total traffic — does your isolation hold?
- **`late-events`** (medium+): events arrive 30 minutes late. How do windowed aggregates handle them?

### "Done" criteria

User can: (a) reason about queue depth and backpressure with concrete numbers, (b) explain why their windowing strategy handles late events correctly, (c) defend tenant-isolation choices, (d) at hard tier, walk through an ingest-spike incident from detection to mitigation.

---

## Cross-project rules

### Foundation unlock protocol

When a milestone requires a topic the user hasn't completed (`topics[topic].status != "complete"`):

1. Pause the project. Tell the user explicitly: *"You're at [milestone N: title]. To do this well, you need [topic X]. Quick foundation lesson, then back to building."*
2. Run a compressed lesson on the topic — same teaching modes (Explain → Visualize → Socratic → Build) but **time-boxed**: aim for ~1/3 the depth of a Foundation-track lesson, since the user has immediate context to anchor it.
3. Mark the topic complete in `progress.json` if it lands. If shaky, mark `confidence: 2` and queue an SR card.
4. Resume the project at the same milestone.

### Difficulty drift detection

Reuse the difficulty-adaptation rule from `references/spaced-repetition.md` § "Difficulty adaptation policy" but apply it to milestones rather than exercises:

- If the user is hint-flooding (`hints_used_max_level >= 3`) on three consecutive milestones, drop one tier.
- If they're cruising (no hints, all stress injections handled cleanly), bump a tier or accelerate to the next milestone.

Surface the change in one sentence ("Last few felt tight — easing the next milestone").

### Switching projects

Allowed mid-course. Update `progress.json.current_project` to the new project's id; the underlying `topics` map preserves what's been learned, so foundations don't reset. Don't penalize abandonment — sometimes the wrong project is the wrong project. Append the abandoned project to `completed_projects` only if at least milestone 1 was finished.

### When all three are done

Suggest a Tier 8 mock interview from `references/curriculum.md` that the projects didn't cover (e.g., Dropbox/sync, geospatial dispatch, video pipeline). At that point the user has earned Foundation-track equivalent coverage and can be treated as "complete" for the curriculum.

## Project recommendation by goal

When proposing the first project after the diagnostic, lean toward:

| Goal | Recommended first project |
|---|---|
| `interview-prep` | URL shortener (classic interview question, broadest coverage) |
| `production` | Metrics pipeline (closest to real-world infra work) |
| `concurrency-bugs` | Chat backend (forces ordering and consistency reasoning) |
| `deep-learning` | URL shortener, but plan to do all three |

These are recommendations, not gates. The user can pick anything. Update `progress.json.current_project.id` to whatever they choose.
