# System Design Tutor

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that runs an end-to-end system design course — driven entirely by Claude. Anchored to [Designing Data-Intensive Applications](https://dataintensive.net/) (DDIA) and the [System Design Primer](https://github.com/donnemartin/system-design-primer).

## What it does

Once installed, say **"start the course"** or **"system design tutor"** in Claude Code and the skill takes over:

- **Drives the curriculum** — Claude proposes the next topic, runs lessons, schedules reviews. You steer when you want a detour.
- **Multiple teaching modes** — theory (flowcharts, mindmaps, Socratic dialogue, auto-quizzes), runnable code exercises, mock interviews, and design reviews.
- **Real-world incidents** — every concept is tied to a real postmortem (GitHub split-brain, Discord hot partitions, Cloudflare regex catastrophe, etc.).
- **Spaced repetition** — tracks your confidence per topic and resurfaces weak spots using SM-2 scheduling.
- **Persistent progress** — saves state across sessions so you can pick up where you left off days or weeks later.
- **30+ hands-on exercises** — from building a hash index to designing a distributed rate limiter.

## Topics covered

Distributed systems, storage & retrieval, replication, partitioning, transactions, consistency, batch & stream processing, caching, load balancing, microservices, and more.

## Installation

### Recommended: skills.sh CLI

```bash
npx skills add rogue-socket/system-design-tutor
```

### Manual install

```bash
mkdir -p ~/.claude/skills && git clone https://github.com/rogue-socket/system-design-tutor.git ~/.claude/skills/system-design-tutor
```

### Other distributions

This skill ships in four flavors — pick the branch that matches your host and platform:

| Branch | Host | Platform | Install guide |
|---|---|---|---|
| `main` | Claude Code | macOS / Linux | (this README) |
| `cc-windows` | Claude Code | Windows | [`install/windows.md`](https://github.com/rogue-socket/system-design-tutor/blob/cc-windows/install/windows.md) |
| `codex-macos` | Codex CLI | macOS / Linux | [`install/codex-macos.md`](https://github.com/rogue-socket/system-design-tutor/blob/codex-macos/install/codex-macos.md) |
| `codex-windows` | Codex CLI | Windows | [`install/codex-windows.md`](https://github.com/rogue-socket/system-design-tutor/blob/codex-windows/install/codex-windows.md) |

The Claude Code distributions share all curriculum content with `main`; only install paths and shell conventions differ. The Codex distributions add an `AGENTS.md` entry point and document a few host-specific behavior differences (no `/compact`, etc.).

## Usage

Open Claude Code and say any of:

- `"start the course"` or `"system design tutor"` — begin or resume the course
- `"teach me consistent hashing"` — jump to a specific topic
- `"mock interview me on designing a chat system"` — run a mock interview
- `"review my design"` — get feedback on a design you're working on
- `"what's due today"` — check spaced repetition reviews
- During coding exercises: `"make this easier"` or `"make this harder"` — adjust difficulty without changing topic

The skill creates a workspace at `~/system-design/` where it stores your progress, exercise files, and session state.

## Structure

```
SKILL.md                              # Router and session controller
LICENSE                               # MIT license
references/
  curriculum.md                       # Full topic tree (8 tiers, mapped to DDIA chapters)
  theory-modes.md                     # Flowcharts, mindmaps, flashcards, Socratic mode
  practical-mode.md                   # Exercise patterns and workflow
  exercise-bank.md                    # 30+ exercises with success criteria
  incidents.md                        # 20+ real-world postmortems
  spaced-repetition.md                # SM-2 scheduling and progress schema
  session-control.md                  # State management, pause/resume
assets/
  workspace-README.md                 # User-facing workspace docs
  progress-template.json              # Initial progress state
  exercise-templates/                 # Python scaffolds (A/B/C) + production-readiness template
tests/
  test-triggering.md                  # Skill activation test cases
  test-routing.md                     # Mode routing test cases
  test-progress-json.md               # Progress state validation
  test-practical-coverage.md          # Tier + required-tag breadth checks
  validate_progress.py                # JSON schema validator
  run_all.py                          # Automated structural + schema test suite
  fixtures/progress_valid.json        # Reference filled-in progress.json
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI or IDE extension
- Works best with Claude Opus

## License

MIT — see [LICENSE](./LICENSE).

## Publish (Both Places)

This skill can be published in:
- Claude Skills (direct upload in Claude app)
- skills.sh ecosystem (GitHub + Agent Skills format)

### A) Publish to Claude Skills

1. Package the skill folder as a zip (build artifact — not committed; regenerated each publish):
```bash
cd /path/to/parent
zip -r system-design-tutor.zip system-design-tutor
```
2. In Claude, open:
   - `Customize` → `Skills` → `+ Create skill` → `Upload a skill`
3. Upload `system-design-tutor.zip`.
4. Enable the skill toggle.
5. On Team/Enterprise, use Share to publish to your org directory.

### B) Publish to skills.sh ecosystem

1. Push this repository to a public GitHub repo.
2. Confirm `SKILL.md` frontmatter includes:
   - `name`
   - `description`
   - `license`
   - optional `compatibility`, `metadata`
3. Keep the directory layout standard:
   - `SKILL.md`
   - `references/`
   - `assets/`
   - `tests/`
4. Follow skills.sh docs for listing/install flow and CLI usage:
   - https://skills.sh/docs
5. Keep your README examples current so listing reviewers can quickly verify usage prompts.

### Quick pre-publish checklist

- `SKILL.md` name matches directory name (`system-design-tutor`)
- Description includes clear trigger phrases
- License is present (`MIT`)
- No private/internal links
- Test prompts in `tests/` still match actual behavior
