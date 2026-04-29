# Triggering Tests

Does the skill activate when it should, and stay quiet when it shouldn't?

For each prompt, paste it into a fresh session (Claude Code or Claude.ai) where the skill is installed, and check whether the skill loads. In Claude Code you can usually tell because the response references the skill's structure (workspace setup, modes, references). If the response is generic, the skill didn't trigger.

## Should TRIGGER (skill engages)

These should all activate the skill. If any don't, the description in `SKILL.md` needs strengthening.

| # | Prompt | Why it should trigger |
|---|--------|----------------------|
| T1 | "Start the system design course" | Direct invocation |
| T2 | "Continue the course" | Resume invocation |
| T3 | "system design tutor" | Naming the skill |
| T4 | "Let's keep going" (with workspace present) | Resume signal |
| T5 | "Teach me about consistent hashing" | Topical detour, should trigger |
| T6 | "Design Twitter for me" | Mock interview detour |
| T7 | "Quiz me on CAP theorem" | Review detour |
| T8 | "What's the difference between sync and async replication?" | Topical question |
| T9 | "Help me understand sharding" | Topical learning request |
| T10 | "What's due today?" | Review session request |
| T11 | "Give me a practical exercise on rate limiting" | Practical mode detour |
| T12 | "Review this design" + a sysdesign sketch | Design review |
| T13 | "How does Kafka guarantee message ordering?" | Topical, no explicit "teach" verb |
| T14 | "Where are we in the course?" | Status check |
| T15 | "I'm studying DDIA chapter 5, can you help?" | Source reference |

## Should NOT trigger (skill stays quiet)

These should be handled by Claude normally without the skill activating.

| # | Prompt | Why it should NOT trigger |
|---|--------|--------------------------|
| N1 | "Fix this Python bug" + code | Unrelated coding |
| N2 | "Write me a sorting function" | Unrelated coding |
| N3 | "Help me design a logo" | "Design" but not system design |
| N4 | "What's the weather in Hyderabad?" | Unrelated |
| N5 | "Explain how Bitcoin works" | Adjacent but not sysdesign |
| N6 | "Database normalization rules?" | Pure DB theory, not sysdesign |
| N7 | "How do I install Postgres?" | Ops/install, not learning sysdesign |

## Borderline / discuss

These are judgment calls. Worth deciding what you want each to do, then aligning the skill description.

| # | Prompt | Question |
|---|--------|----------|
| B1 | "How do I scale my Postgres database?" | Is this learning or ops? |
| B2 | "Should I use Redis or Memcached?" | Tech-choice question — counts as topical? |
| B3 | "What's the architecture of YouTube?" | Curiosity vs learning? |

For the borderlines, my default would be **trigger** — better to over-engage on learning-shaped questions than miss them. But if you find the skill being too eager, tighten the description.

## How to interpret results

- **All triggers fire, no mistriggers**: Description is well-tuned.
- **Some triggers miss**: Description is too narrow. Add more example phrasings. Look at which trigger types are missing — vague ones, topical ones, mode keywords.
- **Mistriggers on N1-N7**: Description is too aggressive. Pull back the "trigger even without explicit teach verb" language.
- **Borderlines went the way you wanted**: ✓
- **Borderlines went the wrong way**: Decide which way you want them, then adjust description with example phrasings (in or out).

## When to re-run

- Whenever you edit `SKILL.md`'s description (the YAML frontmatter), re-run all triggers.
- Whenever you add a new mode, add corresponding test prompts.
- Once a month even if nothing changed — model behavior drifts.

## Notes on scoring

This isn't a pass/fail bar at 100%. Skills are inherently fuzzy:
- 12/12 triggers + 0 mistriggers = excellent
- 10-11/12 triggers + 0 mistriggers = good, fix the misses
- 12/12 triggers + 1-2 mistriggers = good, tighten
- < 10/12 triggers OR 3+ mistriggers = the description needs a rewrite

If you're using the skill-creator's automated evaluator, run each prompt 3 times to get a trigger rate (LLMs are non-deterministic). 80%+ on shoulds and < 10% on shouldn'ts is a reasonable bar.
