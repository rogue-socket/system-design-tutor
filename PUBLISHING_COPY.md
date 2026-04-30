# Publishing Copy

Use this copy for both Claude Skill upload details and marketplace listings (skills.sh or similar).

## Title

System Design Tutor

## One-line Pitch

A Claude-driven, end-to-end system design course with adaptive coding exercises, spaced repetition, and persistent progress tracking.

## Short Description (<= 200 chars)

Learn system design hands-on with adaptive coding exercises, mock interviews, incident-driven lessons, and persistent progress across sessions.

## Full Description

System Design Tutor turns Claude into your dedicated system design coach. It runs a full learning path anchored to DDIA and the System Design Primer, with theory, practical coding, mock interviews, and design reviews.

Core capabilities:
- Curriculum-driven progression with pause/resume state
- Adaptive practical exercises with `core/stretch/chaos` layers
- Difficulty controls during exercises: "make this easier" / "make this harder"
- Spaced repetition with confidence tracking and weak-spot resurfacing
- Real-world postmortem anchors for each major concept
- Persistent progress in `~/system-design/` (`progress.json`, `session-state.md`, exercises, notes)

Best for intermediate engineers preparing for interviews or building stronger distributed systems intuition.

## Tags

system-design, distributed-systems, education, interview-prep, backend, reliability, architecture, ddia, tutoring, coding-exercises

## Trigger Prompts (for listing examples)

- start the course
- system design tutor
- continue the course
- teach me consistent hashing
- give me another coding exercise
- make this harder
- what's due today
- mock interview me on a URL shortener

## What Users Should Know

- Requires filesystem access to create and maintain a course workspace at `~/system-design/`.
- Designed for multi-session use across days/weeks.
- Works best when users run the generated exercises locally and share outputs back.
