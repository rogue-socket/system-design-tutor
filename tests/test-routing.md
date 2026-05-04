# Routing Tests

Once the skill triggers, does it dispatch to the right mode? The dispatch table is in `SKILL.md` (Step 2). These tests verify that table is doing its job.

## Method

Paste each prompt into a fresh session with the skill installed. Check the response against the expected mode. Look for these signals:

- **Theory mode**: response involves explanation, asks a probing question, mentions diagrams/visualizations, references DDIA/Primer
- **Practical mode**: response talks about setting up an `exercises/<topic>/` folder, mentions Python scaffold, asks language preference
- **Recall mode**: response mentions flashcards, due cards, or quiz
- **Mock interview mode**: response asks "where do you want to start?", refuses to drive, demands requirements first
- **Design review mode**: response analyzes the user's design, identifies load-bearing assumptions
- **Planning mode**: response references the curriculum, asks about goals, suggests a path
- **Onboarding mode**: response offers diagnostic / pick-topic / mock interview, since it's a first session

## Test prompts

| # | Prompt | Expected mode |
|---|--------|---------------|
| R1 | "Start the course" (no workspace exists) | First-Time Onboarding (creates workspace, asks for default language and goal, runs 8-question diagnostic weighted by goal) |
| R2 | "Continue" (workspace exists, session-state.md exists) | Warm Resume (proposes next step from state) |
| R3 | "Continue" (workspace exists, no session-state.md) | Cold Resume (lighter recalibration) |
| R4 | "Teach me consistent hashing" (mid-course) | Theory mode, queue current path step |
| R5 | "I want to understand quorum reads" | Theory |
| R6 | "Give me a practical exercise on rate limiting" | Practical |
| R6b | "Give me another coding exercise, harder this time" | Practical; next exercise selected with higher challenge |
| R6c | "Make this exercise easier" | Practical; same topic, downshift scope/constraints |
| R6d | "Make this harder with one failure scenario" | Practical; same topic, add adversarial constraint |
| R7 | "Quiz me" / "What's due today?" | Recall (SR queue) |
| R8 | "Design Twitter" | Mock interview |
| R9 | "Mock interview me on a URL shortener" | Mock interview |
| R10 | "Review my design: [pastes design]" | Design review |
| R11 | "Where are we in the course?" | Status from progress.json |
| R12 | "Pause" / "I have to go" | End-of-session protocol |
| R13 | "Save my progress and let me clear" | Checkpoint + suggest /clear |
| R14 | (Long session, 70+ messages) | Should proactively suggest /compact |
| R15 | "It's been 3 weeks since I did this" | Suggest review session before forward progress |

## Common routing failures to watch for

These are the routing mistakes I'd expect to see. Each has a fix.

### Failure: "Teach me X" → goes straight to lecturing instead of probing
- **Symptom**: Response is a long explanation, no probing question, no "what do you already know?"
- **Fix**: Strengthen the "calibration before teaching" rule in `SKILL.md`'s core philosophy section.

### Failure: "Design Twitter" → starts designing instead of making the user drive
- **Symptom**: Response begins with "Let me start with functional requirements..." instead of "Where do you want to start?"
- **Fix**: Strengthen the "Don't drive" rule in the Mock Interview section.

### Failure: "Quiz me" → makes up a quiz instead of pulling from SR queue
- **Symptom**: Generic quiz on random topics, doesn't reference `progress.json`
- **Fix**: Make sure the skill is actually reading `progress.json` at session start. Add explicit "if user says 'quiz me', check SR queue first" in `spaced-repetition.md`.

### Failure: Theory request → response too long without auto-quiz checkpoints
- **Symptom**: 500-word explanation, no questions, no checkpoints
- **Fix**: Strengthen the auto-quiz triggers in `theory-modes.md`. Possibly add a hard rule in `SKILL.md`: "Never deliver more than 200 words without a question or visual."

### Failure: First session → doesn't offer onboarding paths
- **Symptom**: Skill doesn't notice missing `progress.json`, just starts teaching
- **Fix**: Make sure Step 1 in `SKILL.md` actually checks for the workspace.

### Failure: "another exercise" → bounces back to theory
- **Symptom**: User asks for more coding practice and the skill proposes a theory lesson.
- **Fix**: Strengthen practical-priority routing and read `user.practice_preference` from `progress.json` before choosing the next step.

### Failure: "make this easier/harder" → changes topic instead of difficulty
- **Symptom**: Skill swaps to a different concept instead of resizing the same exercise.
- **Fix**: Enforce same-topic difficulty adjustment with `core/stretch/chaos` layering.

## How to interpret results

- All 18 routed correctly: skill is in good shape.
- 1-3 misroutings, all in the same mode: that mode's section in `SKILL.md` needs work.
- Misroutings spread across modes: the dispatch table in Step 2 needs to be more explicit.
- "Theory mode but no probing" or "mock interview but skill drives" — that's a *behavior* failure inside the right mode, not a routing failure. Document it and fix the relevant reference file.

## Re-run when

- You add a new mode
- You change the dispatch table
- You change any reference file's opening behavior
