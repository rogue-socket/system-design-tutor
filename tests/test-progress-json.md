# Progress.json Hygiene Test

After the skill teaches a lesson, runs an exercise, or completes a mock interview, it should write a valid `progress.json` matching the schema in `references/spaced-repetition.md`. This test verifies that.

## Method

Run a short scripted session, then inspect the resulting `progress.json`. Either:

- **Manual**: paste the script prompts one at a time, then `cat ~/system-design/progress.json` and check.
- **Automated**: use the Python validator below.

## Test scenarios

### Scenario A: First lesson (creates progress.json)

**Prompts** (paste in order, fresh workspace):

```
1. "I want to start system design. Quick lesson on consistent hashing."
2. [answer probing question with reasonable response]
3. [answer 1-2 follow-up questions]
4. "Thanks, that's enough for today."
```

**Expected after the session**:
- `~/system-design/progress.json` exists
- `progress.json` has `topics["consistent-hashing"]` with `status` set, `confidence` set (1-5), `last_reviewed` set to today's date
- `session_log` has one entry for today
- `event_log` has append-only entries including at least `session_started` and one lesson-related event
- `practical_coverage` exists with `tier_counts`, required tag lists, and `coverage_score`
- If flashcards were generated, `flashcards/` directory exists with at least one .json file
- If diagrams were generated, `notes/diagrams/` exists with HTML files

**Schema validation**: run `python tests/validate_progress.py ~/system-design/progress.json`. Should print "VALID".

### Scenario B: Practical exercise

**Prompts** (after Scenario A):

```
1. "Give me a practical exercise on consistent hashing."
2. [follow the exercise — be a "user who finishes successfully"]
3. "Done."
```

**Expected after the session**:
- `~/system-design/exercises/<date>-consistent-hashing/` exists with README.md, starter.py, etc.
- `progress.json` has a new entry in `exercises_completed` referencing this folder
- `topics["consistent-hashing"].confidence` may have increased
- `event_log` has `exercise_started` and `exercise_completed` entries appended (not replacing prior entries)
- Exercise entry records adaptive data when available: `planned_difficulty`, `observed_difficulty`, `hints_used_max_level`, `attempt_count`
- `practical_coverage.tier_counts` and required tag lists update based on exercise `coverage_tags`

### Scenario C: Mock interview

**Prompts**:

```
1. "Mock interview me on a URL shortener."
2. [be a learner who does OK but stumbles on database choice]
3. [continue through the interview]
4. "End interview."
```

**Expected after the session**:
- `~/system-design/reviews/<date>-url-shortener.md` exists with the design + feedback
- `progress.json` has session_log entry with type "mock-interview"
- Topics that came up are in `topics{}` with appropriate status
- If specific weak spots surfaced (e.g., "couldn't pick database"), they're captured
- `event_log` includes mock interview events appended

### Scenario D: Spaced repetition update

**Prompts** (assumes Scenario A already ran):

```
1. "What's due for review today?"
2. [the skill surfaces flashcards from Scenario A]
3. [answer them, mix of correct and incorrect]
```

**Expected after the session**:
- Flashcards' `next_review` dates have been updated
- `ease`, `interval_days`, `review_history` all updated correctly
- The math follows the SM-2 lite algorithm in `references/spaced-repetition.md`
- Cards rated < 3 have shorter `interval_days` than cards rated ≥ 3

### Scenario E: Pause and resume

**Prompts**:

```
1. "Continue" (Scenario A workspace, mid-lesson)
2. [follow lesson partway]
3. "Pause"
```

**Expected after pause**:
- `session-state.md` exists, with sections: "Where we left off", "Open threads", "Next planned step", "Active artifacts", "Recent confusion / weak spots"
- `progress.json.current_session.active` = false
- `progress.json.current_session.last_checkpoint` updated
- `progress.json.event_log` has a `session_paused` or `session_ended` style event appended
- Brief closing message from Claude (3-4 lines max), no preamble for "next session"

**Then start a new session**:

```
4. "Continue"
```

**Expected on resume**:
- Claude reads `session-state.md`
- Opens with: "Welcome back. Last time we [content from session-state]. Today: [resume + next planned step]."
- Doesn't ask "what do you want to do?"
- After user confirms, proceeds without long preamble

### Scenario F: Long-session compaction prompt

**Prompts**:

```
1. "Continue" + carry on for 60+ messages of varied content
   (theory + Q&A + code debugging, etc.)
```

**Expected**:
- At some point Claude proactively says something like "We've covered a lot — let me checkpoint, then run /compact (or new chat) before we continue."
- State is written to disk *before* the suggestion
- After compaction, "continue" should pick up cleanly

## Schema validator script

Save this as `tests/validate_progress.py`:

```python
"""Validate that progress.json conforms to the schema."""
import json
import sys
from datetime import datetime


REQUIRED_TOP_LEVEL = ["user", "topics", "flashcards", "exercises_completed", "session_log"]
REQUIRED_USER_FIELDS = ["started", "level", "preferred_language"]
VALID_TOPIC_STATUS = {"not-started", "in-progress", "needs-review", "complete"}


def validate_date(s, field):
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise AssertionError(f"{field} should be YYYY-MM-DD, got {s!r}")


def validate_progress(p):
    errors = []

    for f in REQUIRED_TOP_LEVEL:
        if f not in p:
            errors.append(f"missing top-level field: {f}")

    if "user" in p:
        for f in REQUIRED_USER_FIELDS:
            if f not in p["user"]:
                errors.append(f"missing user.{f}")
        if "started" in p["user"]:
            try:
                validate_date(p["user"]["started"], "user.started")
            except AssertionError as e:
                errors.append(str(e))

    for topic_id, topic in p.get("topics", {}).items():
        if "status" in topic and topic["status"] not in VALID_TOPIC_STATUS:
            errors.append(f"topics.{topic_id}.status invalid: {topic['status']!r}")
        if "confidence" in topic and not (1 <= topic["confidence"] <= 5):
            errors.append(f"topics.{topic_id}.confidence out of range: {topic['confidence']}")
        for date_field in ("first_seen", "last_reviewed"):
            if date_field in topic:
                try:
                    validate_date(topic[date_field], f"topics.{topic_id}.{date_field}")
                except AssertionError as e:
                    errors.append(str(e))

    for card_id, card in p.get("flashcards", {}).items():
        for f in ("ease", "interval_days", "next_review"):
            if f not in card:
                errors.append(f"flashcards.{card_id} missing {f}")
        if "ease" in card and not (1.3 <= card["ease"] <= 3.0):
            errors.append(f"flashcards.{card_id}.ease out of expected range: {card['ease']}")
        if "next_review" in card:
            try:
                validate_date(card["next_review"], f"flashcards.{card_id}.next_review")
            except AssertionError as e:
                errors.append(str(e))

    for i, ex in enumerate(p.get("exercises_completed", [])):
        for f in ("topic", "folder", "completed"):
            if f not in ex:
                errors.append(f"exercises_completed[{i}] missing {f}")

    return errors


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "progress.json"
    with open(path) as fp:
        data = json.load(fp)
    errs = validate_progress(data)
    if errs:
        print("INVALID:")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("VALID")
```

## Pass criteria

- All four scenarios produce valid JSON (validator returns "VALID")
- All expected files are created in the right locations
- All expected fields are populated with sensible values
- No fields contain placeholder strings like "TBD" or "REPLACE_WITH_TODAY" after a real session
- `event_log` is append-only across scenarios (earlier entries remain present)
- Adaptive exercise fields are valid when present (`difficulty` values and hint/attempt ranges)

## When to re-run

- After editing `references/spaced-repetition.md` (schema changes)
- After editing the workspace setup logic in `SKILL.md`
- Before sharing the skill with someone else
