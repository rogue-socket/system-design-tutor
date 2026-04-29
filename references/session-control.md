# Session Control

How to drive sessions, checkpoint state, manage Opus 4.7's context window, and resume cleanly across breaks. **This is the most important reference file for the experience to feel cohesive across days/weeks.**

## The model

The skill owns the course. The user shows up; Claude runs the lesson plan. The user can interject ("can we detour to X?", "skip this", "I'm stuck"), but the *default behavior is forward motion*. This is the opposite of a chatbot — Claude proposes, the user steers when they want to.

This requires three things to work cleanly:

1. **Persistent state on disk** — rich enough that any new session can reconstruct context.
2. **Session checkpoints** — written *during* a session, not just at the end, because conversations crash, get cleared, hit context limits.
3. **Explicit pause/resume protocol** — both Claude-initiated (context-aware) and user-initiated.

## The two state files

### `progress.json` (long-term state)

Schema is in `spaced-repetition.md`. This is the *what* — what topics are done, what's weak, what's due. Survives across all sessions forever.

### `session-state.md` (session-bridging state)

This is the *where* — where we left off mid-flow. Updated *during* every session. Re-read at the start of every session. This is the file that makes "pick up where we left off" actually work.

Schema:

```markdown
# Session State

**Last updated**: 2026-04-30 14:23
**Current course position**: Tier 3.1 Partitioning Strategies → consistent hashing
**Current mode**: Theory (mid-lesson) | Practical (mid-exercise) | Review | Mock interview | Idle

## Where we left off
[2-4 sentences. What was just happening when the session paused.
"User had just finished implementing the consistent hash ring with virtual
nodes. We ran the experiment showing 12% of keys move when adding a node.
About to discuss why virtual node count matters and start the hot-key extension."]

## Open threads
- [Any unresolved questions or topics queued up. Bullet list.]
- User asked about jump consistent hashing — promised to come back to it
- Need to revisit quorum reads (struggled in last session)

## Next planned step
[One sentence. The next thing Claude will propose when the session resumes.]
"Hot-key extension on the consistent hashing exercise — celebrity simulation."

## Active artifacts
- `exercises/2026-04-30-consistent-hashing/` (in progress)
- `notes/diagrams/consistent-hashing.html` (saved, can re-share)

## Recent confusion / weak spots
[Things from this session that need flagging in progress.json before clearing context.]
- User confused about virtual node count vs replica count — clarified, but check on next review.
```

This file is human-readable and re-readable in 30 seconds. That's the design — when you load it at session start, you don't have to puzzle over JSON.

## Session start protocol

Every session, **before doing anything else**:

1. **Read `progress.json`.** Note: SR queue, weak spots, last session date.
2. **Read `session-state.md`** if it exists. This tells you *exactly* where to resume.
3. **Decide what to propose**, in this priority order:
   - If `session-state.md` shows a mid-lesson or mid-exercise state from <14 days ago: resume that. "Welcome back. Last time we were [where we left off]. Want to continue, or break first to clear stale items?"
   - Else if SR queue has overdue items: "Quick review first — you have N items due. Then we continue with [next planned step]."
   - Else if curriculum has a clear next step: "Today: [topic]. Sound good?"
   - Else (first session): trigger onboarding flow (in `SKILL.md`).
4. **Propose, don't ask.** Don't say "what would you like to do?" — say "Today: X. Yes, or detour?"

If `session-state.md` is older than 14 days, treat the resume context as stale: "It's been a while. Quick recap: last we covered [X]. I'd suggest a 10-minute review of [topics] before forward progress. Sound good?"

## Session checkpoints (during session)

Update `session-state.md` whenever:

- A lesson finishes (and the user hasn't asked for the next one yet)
- An exercise finishes
- The user says anything that sounds like pausing ("hold on", "let me go think about this", "I'll come back later")
- 30+ minutes have passed since last checkpoint
- You're about to suggest `/compact` or `/clear` (see context management below)

Updating means rewriting the relevant sections. **Always overwrite the whole file**, don't try to append — the goal is "always up to date", not "audit log."

## Context window management (Opus 4.7 specific)

Opus 4.7 has a large context window but it's not infinite, and even when it fits, *long conversations get noisy*. Old turns clutter attention. The skill should proactively manage this.

### The two tools the user has

The user is in **Claude Code** or the Claude.ai app. Both support context management, but the commands are different.

**In Claude Code:**
- `/compact` — summarizes the conversation so far and continues. Cheaper than `/clear` because it preserves working state via the summary.
- `/clear` — wipes context entirely. Claude starts fresh.

**In Claude.ai:**
- "Start new chat" is the equivalent of `/clear`.
- There is no direct equivalent of `/compact` in the consumer chat app — the user can ask Claude to summarize and copy the summary to a new chat manually.

The skill should know which environment it's in (it can usually tell from context — if there are file tools and a working directory it's likely Claude Code; if not, Claude.ai) and adjust its language accordingly.

### When to suggest /compact (or summary-and-resume)

You're mid-lesson, the user wants to keep going *right now*, but messages are accumulating. Suggest compaction when:

- The current session has gone 60+ messages and you're about to start a new sub-topic or exercise
- The user has fired off many short messages that are no longer relevant to current state
- A long exercise just finished with lots of code-debugging back-and-forth, and you're moving on to something else
- You can feel the lesson getting "muddier" — earlier confusion is no longer relevant

How to suggest:

> "We've covered ground — let me write a checkpoint, then run `/compact` (or start a new chat in Claude.ai) before we dive into the next part. The checkpoint is on disk, so we'll lose nothing."

Then:
1. Update `session-state.md` with current position and "next planned step"
2. Update `progress.json` with anything earned this session
3. Tell the user: "Done. Checkpoint saved. Run `/compact` now and say 'continue' when you're back."

### When to suggest /clear (or new chat)

Suggest a clean break when:

- Switching from a long theory session to a practical exercise (different mental mode)
- Multi-hour session, user is tired, but wants to do "one more thing"
- Conversation has accumulated enough digressions that compaction would still leave noise
- Starting a new mode entirely (e.g., from study to mock interview)

> "Good place to reset. Update progress, you run `/clear`, then say 'continue' — I'll reload state and we'll start the next part fresh."

Same checkpoint protocol: write state first, *then* suggest.

### When NOT to suggest either

- Mid-exercise, user is debugging code — wait until the bug is fixed.
- Mid-lesson, user is engaged with a concept — wait until the concept lands.
- User just resumed from a break — let them get into flow first.

The asymmetry: it's much worse to break flow than to let context get a bit long.

## User-initiated pause

If the user says any of:
- "let's pause" / "pause here" / "I need to go" / "I'll come back later"
- "stop for today" / "that's enough"
- "I have to run"

Respond with the **end-of-session protocol** below. Don't argue, don't try to squeeze in one more thing.

## End-of-session protocol

On user pause, or end of natural unit of work:

1. **Acknowledge briefly.** "Got it — let me checkpoint."
2. **Update `session-state.md`** with current position and a "next planned step" written specifically for resumption.
3. **Update `progress.json`**:
   - Topics worked on this session
   - Any weak spots that surfaced
   - Session log entry
   - Any flashcards generated
4. **Generate any pending artifacts** they should have (summary notes, diagrams, exercise write-ups).
5. **Brief summary to the user**: 3-4 lines max.
   > "Saved. Today we covered [X], you nailed [Y], and I've queued [Z] for next session. See you next time."
6. **Don't propose more.** Don't ask "before you go..." Just close out.

## Resumption protocol

User comes back, possibly days later. They say "continue" or "let's pick up" or just open a new session with the skill active:

1. **Read `session-state.md` and `progress.json`.**
2. **Tell the user where you are**, briefly:
   > "Welcome back. Last time we [paused mid-X]. Today's plan: [resume X], then [next step]. Sound good, or want to do something else first?"
3. **Wait for confirmation or override.** If they say yes, dive in. If they say "actually, let's review first," shift to recall mode.
4. **Be aware of staleness**:
   - <3 days: full speed ahead
   - 3-14 days: brief recap (1-2 sentences) before continuing
   - 14+ days: suggest a review session before forward progress

## Mid-session crash recovery

If the user opens a fresh session and `session-state.md` is recent (today/yesterday) but no explicit pause was logged, assume the conversation crashed or context was cleared without checkpointing. Handle gracefully:

> "Looks like our last conversation cut off mid-lesson on [topic]. I have most of it from the checkpoint at [time]. Want to pick up there, or recap what we covered so I can fill any gaps?"

This is also why checkpoints should fire on a 30-minute timer, not only at lesson boundaries — crashes don't wait for natural break points.

## Anti-patterns

- ❌ Suggesting `/compact` or `/clear` *before* writing state to disk
- ❌ Ending a session without updating `session-state.md`
- ❌ Long resume preambles ("Welcome back! Last time we covered all of...") — keep it tight
- ❌ Ignoring `session-state.md` and starting from scratch
- ❌ Resuming as if no time has passed when 3+ weeks have actually passed
- ❌ Asking "what would you like to do?" at session start — propose, don't ask
- ❌ Not knowing whether you're in Claude Code or Claude.ai (affects which command to suggest)

## Quick reference: command summary

| Situation | Action |
|---|---|
| Session starts | Read both state files; propose next step |
| Lesson finishes mid-session | Checkpoint `session-state.md`; propose next |
| 60+ messages, mid-session | Checkpoint, suggest `/compact` (Claude Code) or summary-and-new-chat (Claude.ai) |
| User says pause/break | End-of-session protocol; close out cleanly |
| Major mode switch (theory → exercise) | Checkpoint; suggest `/clear` if conversation is long |
| Resuming after <3 days | Brief recap, dive in |
| Resuming after 3-14 days | Recap + suggest light review first |
| Resuming after 14+ days | Suggest a review session before forward progress |
| Crash recovery | Acknowledge what was lost; offer to recap |
