# System Design Course Workspace

This is your system design course, run by the `system-design-tutor` skill.

## How it works

**The skill drives.** When you start a session, Claude will tell you what's next — whether that's resuming where you left off, knocking out spaced-repetition reviews, or starting the next topic in the curriculum. You don't need to know the path; Claude does.

You can interject any time:
- **"Pause"** / **"I have to go"** — Claude saves state and ends the session cleanly.
- **"Continue"** / **"yes"** — Accept the proposed next step.
- **"Actually, let's do X"** — Detour. Claude will note where to return.
- **"Make this easier"** / **"Make this harder"** — During coding exercises, Claude keeps the same topic and adjusts difficulty.
- **"Where are we?"** — Claude shows your course position.
- **"What's due today?"** — Claude surfaces SR queue.

## Structure

```
system-design/
├── progress.json         ← long-term state: course position, topics, SR queue
├── session-state.md      ← short-term state: where you left off mid-flow
├── notes/                ← written explanations, organized by topic
│   └── diagrams/         ← interactive HTML flowcharts and mindmaps
├── exercises/            ← runnable Python code exercises
├── reviews/              ← mock interview write-ups with feedback
├── flashcards/           ← topic-organized flashcard decks (JSON)
└── meta/                 ← gripes, course-meta files
```

## Multi-session use & context management

The course is designed for sessions spread across days/weeks. Two files handle this:

- **`progress.json`** — your full progress. Topics learned, weak spots, course position, SR queue. Survives forever.
- **`session-state.md`** — the "where we left off" file. Updated during every session. Tells the next session exactly where to resume.

If a session gets long (lots of debugging, lots of explanation), Claude will proactively suggest:
- **`/compact`** (Claude Code) — keep going, free up context
- **`/clear`** (Claude Code) or new chat (Claude.ai) — clean slate, reload state from disk

In both cases, **state is saved to disk first**, so nothing is lost.

## Sources

The course is anchored to:
- **Designing Data-Intensive Applications** by Martin Kleppmann
- **The System Design Primer** (donnemartin/system-design-primer)

Claude cites chapters/sections when relevant, and pulls from elsewhere when needed.

## Tips

- Trust the drive. Claude has the curriculum; you don't need to plan.
- For exercises, *run the code*. The lesson is in the failure modes you observe.
- If something feels rushed or too slow, say so. The pace adapts.
- Your default language for exercises is set during onboarding and stored in `progress.json`. You can change it any time — it's just a starting point, and Claude confirms before each exercise.
- Keep a `meta/gripes.md` of things that annoyed you. Tell Claude about them periodically — that's how the skill gets better for you specifically.

## Resetting

If something goes wrong with state files, deleting `session-state.md` is safe — Claude will use `progress.json` to figure out where you are. Deleting `progress.json` resets your progress entirely (don't do this unless you mean it).
