# Skill Tests

This directory holds tests for the `system-design-tutor` skill itself. **Read this first** before running anything — it explains the philosophy of what we test (and what we don't).

## What's testable, what isn't

The skill-creator framework lets you run automated evals against a skill — test prompts in, outputs out, with grading via subagents. For most skills with **objectively verifiable outputs** (does the .docx have the right table? does the regex match? does the code compile?), this works well.

For a teaching skill, most of what matters is **subjective**: did the lesson teach well? Did the Socratic question land? Was the incident relevant? You can't grade that with an assertion. The only honest way to evaluate teaching quality is *use it for two weeks and notice what fails*.

So we test the **mechanics** — the things that are verifiable — and we trust your judgment for the rest.

## What's tested here

Three tests with checkable outputs:

### 1. Triggering test (`test-triggering.md`)
Does the skill activate when it should, and stay quiet when it shouldn't? Verifiable: either the skill engaged or it didn't.

### 2. Routing test (`test-routing.md`)
When the skill triggers, does it dispatch to the right mode? "Design Twitter" should go to mock interview; "what's due today" should go to review; "explain CAP" should go to theory. Verifiable: either it routed correctly or it didn't.

### 3. Progress.json hygiene (`test-progress-json.md`)
After a mock lesson, does the skill produce valid JSON that conforms to the schema in `references/spaced-repetition.md`? Verifiable: parse it and validate.

### 4. Practical coverage (`test-practical-coverage.md`)
Does practical work cover the course breadth (tiers + required checkpoints), not just repeated exercises in one area? Verifiable from `progress.json.practical_coverage`.

## What's NOT tested here, and why not

- **Lesson quality.** Subjective. Use it and judge for yourself.
- **Diagram quality.** Subjective. Open the HTML and see.
- **Whether the Socratic questions are good.** Subjective.
- **Whether the incidents are well-chosen.** Subjective.

If you find yourself wanting a test for something subjective, the right move is usually:
- Write down what bothered you in a real session
- Tweak the skill (usually the relevant reference file)
- Re-run that real session

That's a tighter feedback loop than building elaborate evals.

## How to run the tests

### Automated (mechanical / structural)

```bash
python tests/run_all.py
```

Runs `validate_progress.py` against the template and `fixtures/progress_valid.json`, plus structural checks: curriculum step IDs, exercise-bank coverage tags, SKILL.md frontmatter and references, incidents.md tier coverage, doc/validator sync, Tier 6 primary-sources + per-item citations, the production-readiness template existing alongside `practical-mode.md` documenting it and `exercise-bank.md` declaring `production_readiness_focus` with at least 3 populated entries, `practical-mode.md` not hardcoding a language default, `practical-mode.md` declaring Patterns D and E inline-only (matching the actual contents of `assets/exercise-templates/`), `user.goal` capture during onboarding, and the diagnostic question count matching its framing. All pass = the skill's mechanical scaffolding is intact.

### Manual (behavioral / triggering)

The triggering, routing, and behavior tests below are **prompt-and-check** style. The format:

1. Open the test file
2. Read the prompts and expected behavior
3. Either:
   - **In Claude Code or Claude.ai**: paste a prompt to a fresh session and check the response against the expected behavior
   - **Manual** for now — these aren't automated unless you set up the skill-creator's `run_eval.py` (see "Going further" below)

I keep them as markdown rather than JSON so they're readable and you can iterate the prompts as the skill evolves.

## Going further: automated evaluation

If you want to automate triggering tests, the skill-creator framework's `run_loop.py` does this. It's designed for description optimization but works for triggering tests generally. Setup is in the skill-creator skill at `/mnt/skills/examples/skill-creator/`.

The catch: it requires the `claude` CLI tool, which is only available in Claude Code. If you're on Claude.ai, manual is your option.

## Two-week iteration loop (recommended)

Forget the tests for the first two weeks. Just use the skill. Keep a `gripes.md` file in your workspace where you note:

- "It explained X for too long without checking in"
- "It missed an obvious incident"
- "The mock interview was too easy"
- "It made a flashcard that's just trivia"

After two weeks, batch the gripes and update the skill. Run the triggering and routing tests once to make sure you didn't break anything mechanical. Done.

This is a more honest workflow than chasing perfect evals on a teaching skill.
