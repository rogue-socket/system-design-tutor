# Practical Mode

How to run **runnable code exercises** so the user actually builds and breaks systems instead of just reading about them. The default language is whatever the user set in `progress.json.user.preferred_language` during onboarding. Confirm at the start of each exercise; switching is fine but slows setup.

If the user asks for more practice ("another exercise", "more coding", "harder one", "easier one"), stay in practical mode by default for the next 1-3 sessions before returning to theory unless they explicitly ask to switch.

## Difficulty control loop (mandatory)

Before generating exercise code, run this loop:

1. **Pre-flight calibration (3 quick checks)**
   - Concept check: one short "why/when" question on the target concept.
   - Coding comfort check: ask if they can implement the core data structure/protocol without template hand-holding.
   - Tooling comfort check: verify comfort with `pytest`, `asyncio`/`multiprocessing`, or Docker if needed.
2. **Set planned difficulty**
   - `easy`: smaller scope, fewer moving parts, stronger scaffolding.
   - `medium`: standard exercise path.
   - `hard`: full constraints, less scaffolding, adversarial cases.
3. **Generate in three layers**
   - `core`: must-pass path (30-45 min).
   - `stretch`: deeper extension (+30-60 min).
   - `chaos`: failure injection / adversarial scenario (optional).
4. **Adapt during execution**
   - If stuck or repeated failures: downshift one level, keep topic fixed.
   - If fast success: offer stretch first, then chaos.
5. **Log observed difficulty**
   - Write `planned_difficulty`, `observed_difficulty`, `hints_used_max_level`, and attempt counters into `progress.json`.

## The core principle

Reading about consistent hashing is not knowing it. Writing a 30-line Python script that hashes keys, places them on a ring, and watches half your keys go to the wrong node when you bump the modulus — *that* is knowing it.

Every practical exercise must:

1. **Run.** Real Python (or Go / TS / etc.) the user actually executes.
2. **Fail meaningfully.** The user should see the failure mode the topic addresses, then fix it.
3. **Use real concurrency / network when relevant.** A "distributed cache" exercise that runs in one process is less educational than one that runs three processes communicating over loopback.
4. **Live in the workspace.** `exercises/<topic>/` with proper structure — not throwaway snippets.
5. **Be measurable.** Has tests, or a measurable outcome ("rebalance moves <5% of keys when adding a node"), or both.
6. **Expose one visible failure mode first.** Learner should see what breaks before the fix.

## Exercise structure on disk

Each exercise gets its own folder in `exercises/`:

```
exercises/
└── 2026-04-29-consistent-hashing/
    ├── README.md                  ← problem statement, goals, hints, common mistakes
    ├── starter.py                 ← scaffold with TODOs
    ├── solution.py                ← reference solution (kept hidden until they finish)
    ├── test_hashing.py            ← pytest tests
    ├── experiment.py              ← runs the experiment that demonstrates the lesson
    ├── notes.md                   ← user's notes, generated/updated as they go
    ├── production-readiness.md    ← metrics/alerts/runbook/capacity/cost/rollout (filled together at the end)
    └── Makefile                   ← `make run`, `make test`, `make experiment`
```

The `production-readiness.md` file is copied from `assets/exercise-templates/production-readiness-template.md` when the exercise folder is created. Leave the sections empty until the "When they finish" workflow — that's where it gets filled in Socratically.

Naming: `YYYY-MM-DD-<topic>` so the user has a chronological record.

### When to add complexity to the structure

- Multi-process exercises: add `docker-compose.yml` or a `run_cluster.sh`
- Network exercises: split into `client.py` / `server.py` / `proxy.py`
- Long-running exercises: add `monitor.py` to print stats
- Stateful exercises: include a `data/` folder for state files

## Workflow when starting an exercise

1. **Confirm topic and confirm language.** Read `progress.json.user.preferred_language` and ask: "Doing this in [lang], or want to switch?" If `preferred_language` is unset, ask the user to pick now and save it to `progress.json`.
2. **Confirm prereqs.** Check `progress.json`. If they haven't covered something the exercise needs, warn them.
   - Also read `progress.json.user.practice_preference` (`low|medium|high`) and size exercise scope accordingly.
3. **Set up the folder.** Create the structure above.
4. **Write the README.md first.** Problem statement, what they should observe, and hints for the parts you want them to figure out.
   - README must explicitly label `core`, `stretch`, and `chaos`.
5. **Write `starter.py`** with TODO markers where they need to fill in the interesting parts. Keep boilerplate (imports, main, plumbing) intact — make them write the *concept*, not the loop.
6. **Write tests** that capture the success criteria, but **don't show the user the tests yet** if the topic includes "figure out how to know it's correct." For pure implementation topics (consistent hashing math, token bucket math), show the tests upfront.
7. **Hand it over.** "Open `exercises/<folder>/README.md`. Start with `starter.py`. Run `make test` to check yourself. Yell when you're stuck or done."
   - Always append this line on handoff: "If this feels too easy or too hard, say 'make this easier' or 'make this harder' and I'll adjust the same exercise."

## Workflow during the exercise

The user codes; you stay available. Two failure modes to watch for:

### They're stuck for 5+ minutes
- Don't give the answer. Ask: "What have you tried? What did you expect vs what happened?"
- Narrow the problem. "Forget the multi-node case for now — does it work for one node?"
- Use the hint ladder (progressive disclosure):
  - Level 1: directional hint
  - Level 2: pseudocode outline
  - Level 3: near-code hint for one function
  - Level 4: patch-level correction
- Log the highest hint level used.

### They wrote something that "works" but is wrong
- Don't say "wrong." Run their code with an adversarial input. Let the output tell them.
- "Try with these inputs: [...]" → and let them see the failure.
- *Then* discuss why it failed.

## Workflow when they finish

1. **Run their code together.** Don't just look — execute. Note edge cases.
2. **Run the experiment.** The point of the exercise. "Now let's add a node and see what happens."
3. **Compare to reference solution.** Highlight 1-2 things the reference does differently and *why*. Their solution may be better — say so.
4. **Add a stress test.** Crank up the scale or inject a failure. Things often break.
5. **Write up `notes.md`** with: what they built, what tripped them up, what they learned, and what to revisit. This is what the SR system surfaces later.
6. **Fill the production-readiness checklist together.** Don't make them write `production-readiness.md` solo — use it as a Socratic prompt. "What metric would have caught this kind of skew before it caused an outage?" / "What does the rollback look like if this rate-limiter starts denying valid traffic?" Reference the exercise's `production_readiness_focus` (from `exercise-bank.md`) to know which sections to lean on hardest. The point is to internalise the checklist, not produce the document.
7. **Update `progress.json`**: mark the exercise complete, log the topic, add weak spots.
   - Append events to `event_log` for `exercise_started`, `exercise_checkpoint`, `exercise_completed` (append-only; never delete old events).
8. **Apply graduation gates before increasing difficulty**:
   - Tests or measurable success criteria passed
   - User can explain at least one key trade-off
   - User handles one adversarial/failure case
   - `production-readiness.md` has at least the "Metrics to emit" and "Alerts to configure" sections filled (other sections are encouraged but not gating)

## Common exercise patterns

### Pattern A: Single-process, observable
For algorithmic topics. Example: consistent hashing, bloom filter, LSM tree.
- One script, run it, observe the printed output / generated chart.

### Pattern B: Multi-process with `multiprocessing`
For coordination topics where you want true OS-level concurrency. Example: leader election, distributed lock, simple Raft.
- Use `multiprocessing.Process` + `Queue` for IPC.
- Print with timestamps so the user can see the ordering.

### Pattern C: Network with `asyncio` or sockets
For protocol topics. Example: heartbeat protocol, gossip, simple consensus.
- `asyncio` for elegant network code, or raw `socket` if the point is "see the bytes."
- Keep it on `localhost` with multiple ports.

### Pattern D: Multi-container with Docker Compose
For "real distributed system" topics. Example: leader-follower replication with chaos injection.
- 3+ containers, a `docker-compose.yml`, ports exposed for inspection.
- Use `docker pause` / `docker network disconnect` to inject failures.
- Heavy setup — only use when the topic genuinely needs it.
- **Inline-only**: no scaffold lives in `assets/exercise-templates/`. Generate the `docker-compose.yml` and service stubs directly in the exercise's own folder when needed.

### Pattern E: Failure injection
Layered on any of the above. Example: kill a node mid-write, slow a network link, drop messages.
- Use `signal` to kill processes, `tc` for network manipulation, or a wrapper proxy that injects faults.

## Picking the right pattern

If the user says "I want to actually feel this distributed thing":

- Don't reach for Docker Compose immediately. Pattern B (multiprocessing) often delivers 80% of the lesson with 20% of the setup.
- Pattern D is for when the user has time and *wants* the operator experience. Don't impose it.
- Pattern E (failure injection) should be the *second half* of any distributed exercise, not the whole thing.

## Common pitfalls in exercise design

- ❌ **Too much scaffolding** — if you've written 90% of it, they're filling in blanks, not building.
- ❌ **Too little scaffolding** — if they spend 20 minutes on `argparse` setup, the lesson is lost.
- ❌ **No measurable outcome** — "implement consistent hashing" is fuzzy. "Show that adding 1 of 10 nodes moves <15% of keys" is concrete.
- ❌ **Solving without breaking** — if they don't see *why* the naive approach fails, they won't appreciate the fix.
- ❌ **Toy data** — 10 keys is a toy. 100,000 keys with a histogram makes load imbalance visible.
- ❌ **No layering** — one monolithic exercise with no core/stretch/chaos split.
- ❌ **Difficulty whiplash** — jumping from easy to hard without gates.

## Generation guardrails (to avoid too basic / too hard)

- Require at least one visible failure mode before the final fix.
- Require at least one measurable metric (e.g., keys moved %, stale-read rate, p95 latency).
- For sharding/caching/load distribution exercises, avoid tiny datasets; use scale where imbalance is visible.
- Keep `core` solvable in one focused sitting; push complexity into `stretch` and `chaos`.

## What "good" looks like — full example walkthrough

Topic: **consistent hashing**

`README.md`:
```
# Consistent Hashing

## What you'll build
A hash ring that maps keys to nodes, and an experiment that shows
how few keys move when you add or remove a node.

## What you'll observe
With naive `hash(key) % N` sharding, adding a node moves ~50% of keys.
With consistent hashing + virtual nodes, adding a node should move
roughly 1/N of keys.

## Steps
1. Implement `NaiveSharding` (TODO in starter.py).
2. Run `make experiment-naive`. Note how many keys move.
3. Implement `ConsistentHashing` with virtual nodes.
4. Run `make experiment-ch`. Compare.

## Hints (only peek when stuck)
- For the ring, use a sorted list of (hash, node_id) tuples.
- For lookups, use `bisect` to find the next position on the ring.
- Virtual nodes: each physical node gets 100-200 positions.

## Common mistakes
- Forgetting to handle wraparound (key hashes past the highest position go to the lowest).
- Using `hash()` directly — Python randomizes it across runs. Use `hashlib.md5(key).hexdigest()` and convert.
```

`starter.py` has the class skeletons with TODOs in the interesting methods.

`experiment.py` runs both implementations on 100,000 keys, prints a comparison table, and generates `keys-moved.png` showing distribution.

`test_hashing.py` has unit tests for the math.

When the user runs `make experiment`, they *see* the difference. That's the whole lesson.

## When the exercise is done

- Always update `progress.json`.
- Offer to generate flashcards based on what came up. ("You got the wraparound case wrong twice — want me to make a card for that?")
- Suggest the next exercise or topic based on the curriculum.

## Cross-references

- For exercise ideas by topic, see `references/exercise-bank.md`.
- For starter scaffolds, see `assets/exercise-templates/`.
- For the production-readiness checklist, copy `assets/exercise-templates/production-readiness-template.md` into the exercise folder as `production-readiness.md`.
