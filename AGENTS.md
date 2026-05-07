# system-design-tutor (Codex CLI distribution)

This is the Codex CLI distribution of the `system-design-tutor` skill. The canonical operating manual lives in **`SKILL.md`** at the repo root. Read it now and follow it for this session.

`AGENTS.md` exists because Codex CLI loads agent instructions from `AGENTS.md` files (project-scope at the repo root, global-scope at `~/.codex/AGENTS.md`), not from a Claude-Skills-style manifest. This file is the entry point that routes you into `SKILL.md`.

## How to read the skill

1. Read `SKILL.md` first — it is the router and session controller.
2. Load `references/*.md` files **lazily**, only when the mode dispatched in `SKILL.md` § Step 2 calls for them. Do not preload everything — the references are large.
3. Treat `assets/workspace-README.md` and `assets/progress-template.json` as the workspace seed (`SKILL.md` § First-Time Onboarding describes how they're used).
4. The user's persistent workspace defaults to `~/system-design/` — identical to the Claude Code distribution.

## Trigger phrases

The trigger phrases are listed in the `description` field of `SKILL.md`'s frontmatter ("start the course", "system design tutor", "teach me X", "design Y", "review my design", "what's due today", etc.). Treat them as the entry point and run the dispatch logic in `SKILL.md` § Step 1.

## CC → Codex translations

`SKILL.md` is written for Claude Code. The substance applies unchanged, but a handful of host-specific references need translation when you encounter them:

| In `SKILL.md` you'll see... | On Codex CLI, do this instead |
|---|---|
| "Claude Code" | Codex CLI |
| "Claude.ai" (as an alternate host) | Not applicable — this distribution is Codex-only |
| `/compact` (suggest to user) | Suggest the user end the session and start a new one *after* you've written `session-state.md` and `progress.json` to disk. Codex sessions don't have an in-place compaction equivalent; a fresh session re-loads `AGENTS.md` and the persisted state, which is the same outcome. |
| `/clear` (suggest to user) | Same as above — write state first, then start a new Codex session. |
| "Claude Skills upload" (in `SKILL.md` frontmatter `compatibility:`) | Not applicable; Codex loads via `AGENTS.md`, not via a skill manifest. Ignore. |
| "interactive HTML diagrams" | Still works — file outputs are platform-agnostic. The user opens them with their browser. |

The router behavior, curriculum, reference lazy-loading, spaced repetition, mode dispatch, and checkpointing all work identically. Codex has the filesystem and shell access the skill needs.

## Anti-patterns specific to this distribution

- ❌ Treating `AGENTS.md` as the skill itself. It is only a pointer — the substance is in `SKILL.md` and `references/`.
- ❌ Preloading all reference files at session start. Lazy-load per `SKILL.md` § Step 2.
- ❌ Suggesting `/compact` literally. That's a Claude Code command. Use the new-session workaround above.
