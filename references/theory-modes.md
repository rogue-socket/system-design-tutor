# Theory Modes

How to teach theory using the four modalities: **flowcharts, mindmaps, flashcards, Socratic dialogue**. Each has a distinct shape and a distinct failure mode. Pick the right one for the concept; don't default to walls of text.

## Choosing the right modality

| Concept type | Best modality | Why |
|---|---|---|
| A protocol / sequence with branches (replication, 2PC, Raft leader election) | **Flowchart** | Branching is what flowcharts are *for* |
| A taxonomy / topic with siblings & relationships (replication strategies, consistency models) | **Mindmap** | Reveals the shape of the space |
| Definitions, trade-off pairs, things-to-memorize | **Flashcards** | SR-friendly atoms |
| "Why does this work?" / "What happens if...?" | **Socratic** | Builds reasoning, not recall |

You will often combine: e.g., teach quorum reads with a mindmap of consistency strategies → flowchart of the read-repair protocol → Socratic question on why R+W>N → flashcards on the math.

---

## Mode 1: Interactive HTML flowcharts

Default for protocols, decision trees, and request flows. Saved to `notes/diagrams/<topic>.html` so the user has a permanent reference.

### Required properties

1. **Show the failure path.** Every distributed protocol has a happy path and at least one failure path. Both should be visible. Color the failure path red, happy path green.
2. **Make it clickable.** Each node should expand on click to show "what happens here" detail. The user can collapse to see the shape, expand to read.
3. **Include a "what if" panel.** A sidebar showing the common failure modes for this protocol with a button to highlight that path through the diagram.
4. **Self-contained HTML file.** No external dependencies — inline CSS and JS. Works opened directly in any browser.

### Template structure

Use this skeleton for new diagrams:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{TOPIC}}</title>
  <style>
    body { font-family: -apple-system, system-ui, sans-serif; margin: 0; display: flex; }
    #diagram { flex: 2; padding: 20px; }
    #sidebar { flex: 1; padding: 20px; background: #f7f7f7; border-left: 1px solid #ddd; }
    .node { fill: #fff; stroke: #333; cursor: pointer; }
    .node.happy { stroke: #22c55e; stroke-width: 2; }
    .node.failure { stroke: #ef4444; stroke-width: 2; }
    .node.active { fill: #fef3c7; }
    .edge { stroke: #999; stroke-width: 1.5; fill: none; }
    .edge.happy { stroke: #22c55e; }
    .edge.failure { stroke: #ef4444; stroke-dasharray: 5,3; }
    .detail { display: none; padding: 10px; background: #fffbeb; margin: 10px 0; border-radius: 6px; }
    .detail.visible { display: block; }
    button { margin: 4px; padding: 6px 10px; cursor: pointer; }
  </style>
</head>
<body>
  <div id="diagram">
    <h2>{{TOPIC}}</h2>
    <svg viewBox="0 0 800 600" width="100%">
      <!-- nodes and edges here -->
    </svg>
    <div id="details"></div>
  </div>
  <div id="sidebar">
    <h3>What if...?</h3>
    <button onclick="highlight('failure-1')">Network partition</button>
    <button onclick="highlight('failure-2')">Leader crashes mid-write</button>
    <!-- one button per common failure mode -->
    <button onclick="reset()">Reset</button>
  </div>
  <script>
    // toggle node details on click; highlight() colors a path; reset() clears
  </script>
</body>
</html>
```

When generating one for the user, fill in the actual topic content, save it to `notes/diagrams/<topic-slug>.html`, and tell them: "Open `notes/diagrams/<topic-slug>.html` in your browser. Click any node for details, click the 'What if' buttons to see failure paths."

### Examples of good flowchart topics

- Single-leader replication (sync vs async write paths)
- Two-phase commit (with coordinator failure path)
- Raft leader election
- Read repair in Dynamo-style systems
- Cache stampede prevention strategies
- Circuit breaker state machine

### Anti-patterns

- ❌ Flat boxes-and-arrows with no branches — that's not a flowchart, that's a list
- ❌ Showing only the happy path
- ❌ External JS libraries (breaks when the user opens it without internet)
- ❌ Cramming too much into one diagram — split into multiple if needed

---

## Mode 2: Interactive HTML mindmaps

Default for taxonomies and "the shape of a topic." Saved to `notes/diagrams/<topic>-mindmap.html`.

### Required properties

1. **Center node = the question, not the topic.** "How do we replicate data?" not "Replication." This forces siblings to be actual answers.
2. **Each leaf has a one-line trade-off summary.** Not just "consistent hashing" — "consistent hashing: minimal reshuffling on resize, complex to implement."
3. **Collapsible branches.** The user can fold a branch they know to focus on what's new.
4. **Cross-links allowed.** If two leaves relate (e.g., "LSM trees" and "Cassandra"), draw a dotted line.

### When to use

- "What are all the ways to do X?" — use a mindmap
- Comparison of competing approaches — use a mindmap, with trade-offs on each leaf
- Mapping a chapter of DDIA — use a mindmap so the user has the chapter's shape

### Template

Use a simple recursive `<details>`/`<summary>` HTML structure for the data, then JS that lays it out radially. Or use a static SVG with collapse-expand. Keep it self-contained.

---

## Mode 3: Flashcards

Stored as JSON in `flashcards/<topic>.json`. The spaced-repetition system reads these.

### Schema for a single card

```json
{
  "id": "consistent-hashing-001",
  "topic": "consistent-hashing",
  "front": "Why does consistent hashing use virtual nodes?",
  "back": "To smooth out the load distribution. With N physical nodes, hash positions are uneven; virtual nodes (each physical node owns many positions) give a more uniform distribution and make rebalancing cheaper when adding/removing nodes.",
  "type": "why",
  "difficulty": "medium",
  "created": "2026-04-29",
  "ease": 2.5,
  "interval_days": 0,
  "next_review": "2026-04-29",
  "review_history": []
}
```

### Card types — make a mix

Don't make all "what is X" cards. Mix these types:

- **what** — definitions. Use sparingly. ("What is a bloom filter?")
- **why** — motivation. The most valuable type. ("Why do LSM trees beat B-trees on writes?")
- **when** — applicability. ("When would you pick eventual over strong consistency?")
- **trade-off** — pairs. ("Trade-off: synchronous vs asynchronous replication?")
- **gotcha** — common misconceptions. ("True or false: Kafka guarantees exactly-once delivery.")
- **calculation** — back-of-envelope. ("Estimate storage for Twitter timelines, 300M users, 200 tweets each, 2KB per tweet.")
- **scenario** — applied. ("Your DB writes succeed but reads return stale data sometimes. What's likely happening?")

### Quality bar

- A card should be answerable in under 30 seconds.
- If the answer is more than 3 sentences, split into multiple cards.
- Every concept should have at least one **why** card. "What" without "why" is trivia.

### When to make new cards

- After a lesson on topic X, offer to generate 5-10 cards. Mix the types above.
- When the user gets something wrong in a Socratic dialogue — make a card for it.
- When they say "I always forget..." — make a card.

Always show the user the cards before saving. Let them edit or reject.

---

## Mode 4: Socratic dialogue

The most underused mode. Use it whenever the answer to "do they get it?" matters.

### The pattern

1. **Predict.** Ask a question whose answer you haven't given.
2. **Wait.** Let them try. Don't supply the answer.
3. **Reveal.** Confirm or correct, with the *reasoning* — not just "right" or "wrong."
4. **Push one level deeper.** "OK, now what if X were also true?"

### Good Socratic questions

- "What happens if [component] fails right now?"
- "Why doesn't [simpler approach] work?"
- "What are you trading away by picking [choice]?"
- "How would this change if scale were 100x?"
- "Predict the result of this experiment, then we'll run it."

### Bad Socratic questions

- "Do you understand?" — they'll always say yes
- "Any questions?" — same
- Yes/no questions — too easy to bluff through
- Questions whose answers you've just given — pointless

### When the user is stuck

- First, narrow the question. ("Forget the network for a second — just on one node, what would happen?")
- Then, give a hint, not the answer. ("Think about what the leader does when it doesn't hear back.")
- Then, give the answer with reasoning, and ask them to restate it in their own words.

### Logging

When the user struggles or gets something wrong:
- Note it in `progress.json` under weak spots.
- Optionally make a flashcard.
- Don't shame them — struggle is the point.

---

## Mode 5: Auto-quiz (mid-lesson checkpoints)

The other four modes are *deliberate* — you choose to use them. Auto-quiz is *automatic* — it fires on triggers without you thinking about it. The point: the user shouldn't be able to stay in passive-listener mode for more than a few minutes without their understanding being checked.

### Triggers — fire a quiz when

1. **You've delivered ~150 words of explanation in a row.** Stop and ask one question before continuing.
2. **You're about to give a non-obvious result or formula.** ("R + W > N gives strong consistency" — quiz first: "If you have 5 nodes and want to tolerate one failure on writes while still guaranteeing fresh reads, what's the smallest R you need?")
3. **You finished a sub-topic and are about to start the next.** Quick recall before transitioning.
4. **30+ minutes into a session.** Drop a callback to something from earlier: "Quick check — 20 minutes ago we said why async replication can drop writes. What was the reason?"
5. **The user said something that suggests they're losing the thread.** ("OK", "got it", "makes sense" with no engagement — they may be drifting. Test it.)

### Quiz shapes (vary them — same shape every time gets gamed)

- **Predict-the-output**: "What does this code/system print?" with a tiny snippet
- **Spot-the-bug**: "What's wrong with this design/code?" with something subtly broken
- **Justify-the-choice**: "We picked X. Why not Y?"
- **Estimate**: "Roughly how much storage for 10M users at 1KB each per day, 1 year retention?"
- **Reverse**: "If I told you the answer is 'eventual consistency', what's a plausible question?"
- **Apply**: "How would you use what we just covered to fix [a related earlier problem]?"
- **Callback**: "Earlier we discussed X. How does today's topic relate?"

### Rules for auto-quiz questions

- **One question, not three.** A quiz is a checkpoint, not an interrogation.
- **Answerable in under 60 seconds.** If it takes longer, it's a Build, not a quiz.
- **Don't pre-announce.** "Quick check —" is fine. "I'm now going to quiz you on..." is not. The point is for it to feel like natural conversation.
- **No multiple choice unless the discrimination is sharp.** MC lets people guess. Open-ended is better.
- **If they get it wrong, don't move on.** Reteach the specific bit they missed. *Then* continue.

### What to do with the answer

- **Right, confidently**: nod, continue, slightly increase pace.
- **Right, hesitantly**: confirm and add the *why* — they had it but want reassurance.
- **Wrong, close**: walk through their reasoning, identify the missing piece, mini-reteach.
- **Wrong, way off**: stop. Back up. Probably skipped a prereq. Check `curriculum.md` for what's missing.
- **In all cases**: log to `progress.json`. Wrong answers feed weak spots and SR queue.

### Don't overdo it

If you've quizzed three times in 10 minutes and the user is getting them right, *back off*. They're not wasting time being explained at — they're learning. Pestering them with questions makes you feel rigorous; it makes them feel patronized.

The check: are quizzes producing new information about what they know? If yes, keep going. If they're 5-for-5 and the questions feel rote, switch to harder material instead of more questions.

---

## Combining modalities — example lesson plan

User: "Teach me consistent hashing."

1. **Hook with an incident** (from `incidents.md`): "Quick story to motivate this — Discord migrated their entire database from Cassandra to ScyllaDB in 2022 partly because hot partitions were killing them. The thing we're about to study is how to avoid that class of problem."
2. **Probe** (1 question, this is also an auto-quiz checkpoint): "When you've used hash-based sharding, what happens to reads when you add a node?"
3. **Explain — short**: "Right — most reads now go to the wrong shard. That's the problem CH solves." (Stop here, don't keep going. Visualize next.)
4. **Mindmap**: Generate `notes/diagrams/sharding-strategies-mindmap.html` showing modulo hashing, range-based, consistent hashing, with trade-offs on each.
5. **Flowchart**: Generate `notes/diagrams/consistent-hashing.html` showing the ring, nodes placed by hash, key lookup, and what happens when a node is added (only adjacent keys move).
6. **Auto-quiz checkpoint** (before giving the math): "If we have 100 nodes and add 1, roughly what fraction of keys move? Why?"
7. **Socratic**: "Now — what could still go wrong, even with consistent hashing? Imagine one of your keys is `user:beyonce`."
8. **Connect to incident**: "That hot-key problem you just identified is exactly what Twitter dealt with for years. Search 'Twitter Manhattan hot key' if you want the deep dive."
9. **Build**: Send them to `references/practical-mode.md` for the consistent-hashing exercise.
10. **Flashcards**: Offer to generate 6 cards. Mix of why/trade-off/calculation. Save to `flashcards/consistent-hashing.json`.
11. **Notes offer**: If `notes/consistent-hashing.md` doesn't exist, offer: "Want me to write up reference notes for consistent hashing?" Generate per the Notes Generation Mode in `SKILL.md`.
12. **Update progress**: Mark `consistent-hashing` in progress (status depends on how they did), seed SR queue.
