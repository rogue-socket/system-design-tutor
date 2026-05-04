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

The canonical validator lives at `tests/validate_progress.py`. It validates every required top-level field (`user`, `course_position`, `current_session`, `topics`, `flashcards`, `exercises_completed`, `session_log`, `event_log`, `practical_coverage`) plus per-field shape and value constraints.

Run it on a real `progress.json`:

```bash
python tests/validate_progress.py ~/system-design/progress.json
```

Or run the full automated suite (validator + structural checks):

```bash
python tests/run_all.py
```

A filled-in valid example is at `tests/fixtures/progress_valid.json` — use it as a reference for what a healthy `progress.json` looks like mid-course.

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
