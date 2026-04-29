# Practical Mode

How to run **runnable code exercises** so the user actually builds and breaks systems instead of just reading about them. Default language is Python, but ask before each exercise — the user said "anything should work."

## The core principle

Reading about consistent hashing is not knowing it. Writing a 30-line Python script that hashes keys, places them on a ring, and watches half your keys go to the wrong node when you bump the modulus — *that* is knowing it.

Every practical exercise must:

1. **Run.** Real Python (or Go / TS / etc.) the user actually executes.
2. **Fail meaningfully.** The user should see the failure mode the topic addresses, then fix it.
3. **Use real concurrency / network when relevant.** A "distributed cache" exercise that runs in one process is less educational than one that runs three processes communicating over loopback.
4. **Live in the workspace.** `exercises/<topic>/` with proper structure — not throwaway snippets.
5. **Be measurable.** Has tests, or a measurable outcome ("rebalance moves <5% of keys when adding a node"), or both.

## Exercise structure on disk

Each exercise gets its own folder in `exercises/`:

```
exercises/
└── 2026-04-29-consistent-hashing/
    ├── README.md           ← problem statement, goals, hints, common mistakes
    ├── starter.py          ← scaffold with TODOs
    ├── solution.py         ← reference solution (kept hidden until they finish)
    ├── test_hashing.py     ← pytest tests
    ├── experiment.py       ← runs the experiment that demonstrates the lesson
    ├── notes.md            ← user's notes, generated/updated as they go
    └── Makefile            ← `make run`, `make test`, `make experiment`
```

Naming: `YYYY-MM-DD-<topic>` so the user has a chronological record.

### When to add complexity to the structure

- Multi-process exercises: add `docker-compose.yml` or a `run_cluster.sh`
- Network exercises: split into `client.py` / `server.py` / `proxy.py`
- Long-running exercises: add `monitor.py` to print stats
- Stateful exercises: include a `data/` folder for state files

## Workflow when starting an exercise

1. **Confirm topic + language.** "Consistent hashing exercise — Python OK or want to try this in Go?"
2. **Confirm prereqs.** Check `progress.json`. If they haven't covered something the exercise needs, warn them.
3. **Set up the folder.** Create the structure above.
4. **Write the README.md first.** Problem statement, what they should observe, and hints for the parts you want them to figure out.
5. **Write `starter.py`** with TODO markers where they need to fill in the interesting parts. Keep boilerplate (imports, main, plumbing) intact — make them write the *concept*, not the loop.
6. **Write tests** that capture the success criteria, but **don't show the user the tests yet** if the topic includes "figure out how to know it's correct." For pure implementation topics (consistent hashing math, token bucket math), show the tests upfront.
7. **Hand it over.** "Open `exercises/<folder>/README.md`. Start with `starter.py`. Run `make test` to check yourself. Yell when you're stuck or done."

## Workflow during the exercise

The user codes; you stay available. Two failure modes to watch for:

### They're stuck for 5+ minutes
- Don't give the answer. Ask: "What have you tried? What did you expect vs what happened?"
- Narrow the problem. "Forget the multi-node case for now — does it work for one node?"
- Drop a hint, not the solution. "Think about what happens when you take the modulus of the hash."

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
6. **Update `progress.json`**: mark the exercise complete, log the topic, add weak spots.

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
