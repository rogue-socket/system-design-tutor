"""Validate that progress.json conforms to the schema in references/spaced-repetition.md."""
import json
import sys
from datetime import datetime


REQUIRED_TOP_LEVEL = ["user", "course_position", "current_session", "topics", "flashcards", "exercises_completed", "session_log"]
REQUIRED_USER_FIELDS = ["started", "level", "preferred_language"]
REQUIRED_COURSE_POSITION_FIELDS = ["current_step", "next_planned_steps", "deviations", "completed_steps"]
REQUIRED_SESSION_FIELDS = ["active", "started_at", "last_checkpoint", "mode", "topic"]
VALID_TOPIC_STATUS = {"not-started", "in-progress", "needs-review", "complete"}
VALID_MODES = {None, "theory", "practical", "review", "mock-interview", "design-review", "onboarding"}


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

    if "course_position" in p:
        for f in REQUIRED_COURSE_POSITION_FIELDS:
            if f not in p["course_position"]:
                errors.append(f"missing course_position.{f}")
        cp = p["course_position"]
        if "next_planned_steps" in cp and not isinstance(cp["next_planned_steps"], list):
            errors.append("course_position.next_planned_steps must be a list")
        if "completed_steps" in cp and not isinstance(cp["completed_steps"], list):
            errors.append("course_position.completed_steps must be a list")
        if "deviations" in cp and not isinstance(cp["deviations"], list):
            errors.append("course_position.deviations must be a list")

    if "current_session" in p:
        for f in REQUIRED_SESSION_FIELDS:
            if f not in p["current_session"]:
                errors.append(f"missing current_session.{f}")
        cs = p["current_session"]
        if "active" in cs and not isinstance(cs["active"], bool):
            errors.append("current_session.active must be a boolean")
        if "mode" in cs and cs["mode"] not in VALID_MODES:
            errors.append(f"current_session.mode invalid: {cs['mode']!r}")

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
    try:
        with open(path) as fp:
            data = json.load(fp)
    except FileNotFoundError:
        print(f"FILE NOT FOUND: {path}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"INVALID JSON: {e}")
        sys.exit(2)

    errs = validate_progress(data)
    if errs:
        print("INVALID:")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("VALID")
