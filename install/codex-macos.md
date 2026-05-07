# Codex CLI install (macOS / Linux)

How to run the `system-design-tutor` skill via OpenAI's Codex CLI on macOS or Linux.

## Prerequisites

- Codex CLI installed and authenticated. See https://developers.openai.com/codex/cli for current install instructions.

## Two install patterns

Codex CLI loads agent instructions from `AGENTS.md` files. Pick whichever fits your workflow.

### Pattern A — Project-local (recommended for trying it out)

Clone this branch and run Codex from inside the repo. The repo's `AGENTS.md` is picked up automatically as project-scope guidance, which routes Codex into `SKILL.md`.

```bash
git clone -b codex-macos https://github.com/rogue-socket/system-design-tutor.git ~/system-design-tutor
cd ~/system-design-tutor
codex
```

Then say "start the course" or any trigger phrase from `SKILL.md`'s frontmatter description.

### Pattern B — Global (always-on)

If you want trigger phrases to work from any directory, link the skill's `AGENTS.md` into Codex's global config dir. Every Codex session will then have the system-design-tutor instructions loaded.

```bash
git clone -b codex-macos https://github.com/rogue-socket/system-design-tutor.git ~/system-design-tutor
mkdir -p ~/.codex
ln -s ~/system-design-tutor/AGENTS.md ~/.codex/AGENTS.md
```

**Caveat:** Codex's global scope reads `~/.codex/AGENTS.md` (or `AGENTS.override.md` if present). If you already have a global `AGENTS.md` from another setup, this symlink will replace it. Either:
- Append the contents of this repo's `AGENTS.md` to your existing global file instead of symlinking, or
- Use `CODEX_HOME` to point Codex at a different config dir for this skill.

## Workspace location

Identical to the Claude Code distribution: `~/system-design/`. The skill creates this directory and its subfolders (`notes/`, `exercises/`, `reviews/`, `flashcards/`, `meta/`) on first invocation.

## Updating

```bash
cd ~/system-design-tutor
git pull
```

If shared content (curriculum, references, exercises) changed on `main`, the `codex-macos` branch is rebased on top of it, so a `git pull` brings both the shared updates and any Codex-specific deltas.

## Known divergences from CC

See `AGENTS.md` for the full SKILL.md → Codex translation table. The substantive ones:
- Codex has no `/compact` or `/clear`. The skill works around this by writing state to disk first, then having you start a new Codex session.
- Codex doesn't have a "skill manifest" mechanism. `AGENTS.md` is the entry point instead.
