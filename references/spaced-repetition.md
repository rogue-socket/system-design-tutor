# Spaced Repetition

The progress system. This is what makes the skill remember what the user knows, what they struggle with, and what they should review. **Update it religiously** — the system is only as good as the data in it.

## Schema: `progress.json`

Located at the workspace root. Here's the full schema:

```json
{
  "user": {
    "started": "2026-04-29",
    "level": "intermediate",
    "goal": "interview-prep",
    "preferred_language": "python"
  },
  "course_position": {
    "current_step": "P3",
    "current_step_title": "Hot keys, secondary indexes, scatter/gather",
    "next_planned_steps": ["P4", "P5"],
    "deviations": [
      { "step": "RL1", "reason": "user requested early dive into rate limiting", "return_to": "P5" }
    ],
    "completed_steps": ["F1", "F2", "S1", "S2", "P1", "P2"]
  },
  "current_session": {
    "active": false,
    "started_at": "2026-04-30T14:00:00",
    "last_checkpoint": "2026-04-30T14:23:00",
    "mode": "theory",
    "topic": "consistent-hashing",
    "needs_compaction_check": false
  },
  "topics": {
    "consistent-hashing": {
      "status": "in-progress",
      "first_seen": "2026-04-29",
      "last_reviewed": "2026-04-29",
      "confidence": 3,
      "notes": "Got the wraparound case wrong twice. Solid on virtual nodes.",
      "weak_points": ["wraparound when key hash > all node hashes"]
    },
    "single-leader-replication": {
      "status": "complete",
      "first_seen": "2026-04-22",
      "last_reviewed": "2026-04-28",
      "confidence": 4,
      "notes": "Strong intuition. Read-your-own-writes was instant.",
      "weak_points": []
    }
  },
  "flashcards": {
    "consistent-hashing-001": {
      "ease": 2.5,
      "interval_days": 1,
      "next_review": "2026-04-30",
      "review_history": [
        {"date": "2026-04-29", "rating": 3}
      ]
    }
  },
  "exercises_completed": [
    {
      "topic": "consistent-hashing",
      "folder": "exercises/2026-04-29-consistent-hashing",
      "completed": "2026-04-29",
      "notes": "Working impl. Took ~90 min. Stuck on wraparound for 15 min."
    }
  ],
  "session_log": [
    {
      "date": "2026-04-29",
      "duration_min": 75,
      "topics": ["consistent-hashing"],
      "type": "theory+exercise"
    }
  ]
}
```

### Field meanings

**`course_position`** (NEW): Where the user is in the ordered course path from `curriculum.md`.
- `current_step`: The step ID (e.g., "P3") they're working on right now
- `next_planned_steps`: The next 2-3 steps Claude plans to do, in order
- `deviations`: User-requested detours from the default path, with notes about where to return
- `completed_steps`: List of step IDs that are done (status: complete, confidence ≥ 4)

**`current_session`** (NEW): Live state during a session. Reset to `active: false` when session ends.
- `active`: Is a session currently running?
- `started_at` / `last_checkpoint`: For detecting stale state
- `mode`: theory | practical | review | mock-interview | design-review | onboarding
- `topic`: What's being worked on right now
- `needs_compaction_check`: Set to true when the skill should evaluate whether to suggest /compact next turn

**`topics[topic].status`**:
- `not-started` (default if missing)
- `in-progress` — being learned right now
- `needs-review` — covered but flagged for revisit
- `complete` — solid

**`topics[topic].confidence`**: 1-5
- 1: barely seen
- 2: shaky, needs reteaching
- 3: gets the basics, hazy on details
- 4: solid
- 5: could teach it

**`flashcards[id].ease`**: SM-2 ease factor. Starts at 2.5. Adjusted by performance.

## SM-2 lite: scheduling logic

When the user reviews a flashcard, they rate it 0-5. Update the card:

```python
def update_card(card, rating):
    """
    rating:
      0 = blank ("I forgot completely")
      1 = wrong, but it came back when I saw the answer
      2 = wrong, struggled to recognize even with the answer
      3 = correct with effort
      4 = correct
      5 = trivially correct
    """
    if rating < 3:
        # Failed — reset interval, but keep ease (don't punish twice)
        card["interval_days"] = 1
        card["ease"] = max(1.3, card["ease"] - 0.2)
    else:
        # Passed — extend interval
        if card["interval_days"] == 0:
            card["interval_days"] = 1
        elif card["interval_days"] == 1:
            card["interval_days"] = 6
        else:
            card["interval_days"] = round(card["interval_days"] * card["ease"])
        # Adjust ease based on rating
        card["ease"] = max(1.3, card["ease"] + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)))

    card["next_review"] = today + timedelta(days=card["interval_days"])
    card["review_history"].append({"date": today, "rating": rating})
```

This is "lite" SM-2: the standard algorithm with simplified inputs (5-point scale instead of separate quality + grade). Good enough for our purposes.

## At session start: check what's due

Pseudocode for what to do when you load `progress.json`:

```
today = current date
due_cards = [c for c in progress.flashcards if c.next_review <= today]
weak_topics = [t for t in progress.topics if t.confidence <= 2 and t.status != "not-started"]
recently_seen = [t for t in progress.topics if t.last_reviewed within last 3 days]
```

Then surface to the user:

> "Welcome back. You have:
> - **3 flashcards due today**: consistent hashing (×2), quorum reads (×1)
> - **1 weak topic to revisit**: 2PC coordinator failure (you got this wrong last time)
> - **Last session**: replication (3 days ago)
>
> Knock out the cards first (5 min), then continue with replication, or pick something else?"

## At session end: update progress

After **every meaningful interaction**, update `progress.json`:

### After a theory lesson on topic X
```
topics[X].status = "in-progress" (or "complete" if they nailed it)
topics[X].last_reviewed = today
topics[X].confidence = your-honest-assessment-1-to-5
topics[X].notes = brief summary of what they learned, and any weak points
```

### After flashcard review
```
For each card reviewed:
  apply update_card(card, rating)
```

### After a practical exercise
```
exercises_completed.append({
  topic, folder, completed: today, notes: what tripped them up
})
topics[X].confidence += 1 (if exercise went well)
topics[X].weak_points = update with any specific stumbles
```

### After a mock interview
```
session_log.append({date, duration, topics covered, type: "mock-interview"})
For each topic surfaced as weak:
  topics[T].status = "needs-review"
  topics[T].confidence = adjust down
  topics[T].weak_points.append(specific thing)
  -- consider auto-generating a flashcard
```

## Weak-spot escalation

If a topic's confidence stays at 2 across 3+ reviews, **escalate**:
- Suggest a different approach (different exercise, different mode)
- Ask the user: "We've revisited X three times. Want to try a totally different angle — maybe a multi-process exercise instead of theory?"
- If still stuck, suggest going back to a prerequisite topic.

## Generating flashcards from a session

After a lesson, offer to make 5-10 cards. Prioritize:

1. **Things they got wrong.** Anything they stumbled on in Socratic questions.
2. **Trade-offs.** "Pros and cons of X vs Y."
3. **Calculations.** Back-of-envelope math is highly forget-prone.
4. **Gotchas.** Common misconceptions you corrected.

Skip purely definitional cards unless they specifically struggled with a definition.

Card schema (for reference; full version in `theory-modes.md`):
```json
{
  "id": "<topic>-<seq>",
  "topic": "<topic-slug>",
  "type": "what|why|when|trade-off|gotcha|calculation|scenario",
  "front": "...",
  "back": "...",
  "difficulty": "easy|medium|hard",
  "created": "YYYY-MM-DD",
  "ease": 2.5,
  "interval_days": 0,
  "next_review": "YYYY-MM-DD",
  "review_history": []
}
```

Save to `flashcards/<topic>.json` (one file per topic for easy editing). Add card metadata to `progress.json` `flashcards` field.

## Review session UX

When the user says "review" or you surface due cards:

1. Show the front of one card.
2. Wait for their answer.
3. Show the back. Ask: "How did that feel? 0-5."
4. Apply `update_card`.
5. Move to the next.
6. After all due cards, show summary: "Reviewed 5 cards. 4 were solid. 1 (consistent hashing wraparound) needs another pass — scheduled for tomorrow."

Don't drag this out. A 10-card session should take 10 minutes max.

## Edge cases

- **No cards due, no weak topics**: Suggest forward progress. "Nothing on the SR queue today. Want to learn something new? Based on your progress, [next topic from curriculum] is ready."
- **User wants to ignore SR for a session**: Fine. Don't nag. But still update progress at the end.
- **User says "I'm rusty, let me redo X"**: Reset `topics[X].confidence` and re-add prerequisites' due reviews to the queue.
- **Cards getting stale because user hasn't logged in for weeks**: Don't dump 80 due cards. Surface 10 most-overdue, suggest a "rust removal" session.

## Implementation note

You don't need to actually run Python to do this math — just compute it inline and write the updated JSON back to disk. Use the workspace's filesystem tools (Read, Write, Edit) directly.
