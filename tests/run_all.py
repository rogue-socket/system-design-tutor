"""Run all automated tests for the system-design-tutor skill.

Covers:
  - JSON schema validator on the template (expects placeholder failures)
  - JSON schema validator on the filled fixture (expects VALID)
  - Structural checks across reference files

Usage:
    python tests/run_all.py [--verbose]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
REFS = ROOT / "references"
ASSETS = ROOT / "assets"

REQUIRED_TAGS = [
    "required-consistent-hashing",
    "required-replication-lag",
    "required-idempotency",
    "required-distributed-rate-limiter",
    "required-failure-injection",
]

TIER_TAGS = [
    "tier1-storage",
    "tier2-replication",
    "tier3-partitioning",
    "tier4-consistency",
    "tier5-messaging",
    "tier6-reliability",
    "tier7-specialized",
    "tier8-integration",
]


def run(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
        return True
    except AssertionError as e:
        print(f"FAIL  {name}: {e}")
        return False
    except Exception as e:
        print(f"ERROR {name}: {type(e).__name__}: {e}")
        return False


def test_validator_template_has_placeholders():
    r = subprocess.run(
        [sys.executable, str(TESTS / "validate_progress.py"), str(ASSETS / "progress-template.json")],
        capture_output=True, text=True,
    )
    assert r.returncode == 1, f"template should fail validation due to placeholders, got rc={r.returncode}"
    assert "REPLACE_WITH_TODAY" in r.stdout, f"unexpected output: {r.stdout}"


def test_validator_fixture_valid():
    r = subprocess.run(
        [sys.executable, str(TESTS / "validate_progress.py"), str(TESTS / "fixtures" / "progress_valid.json")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"fixture should validate, stdout={r.stdout}"
    assert r.stdout.strip() == "VALID"


def test_template_has_required_top_level_fields():
    data = json.loads((ASSETS / "progress-template.json").read_text())
    for key in ("user", "course_position", "current_session", "topics",
                "flashcards", "exercises_completed", "session_log",
                "event_log", "practical_coverage"):
        assert key in data, f"template missing {key}"


def test_template_practical_coverage_lists_all_required_tags():
    data = json.loads((ASSETS / "progress-template.json").read_text())
    missing = set(data["practical_coverage"]["required_tags_missing"])
    assert missing == set(REQUIRED_TAGS), f"required_tags_missing mismatch: {missing} vs {set(REQUIRED_TAGS)}"


def test_template_practical_coverage_has_all_tiers():
    data = json.loads((ASSETS / "progress-template.json").read_text())
    counts = data["practical_coverage"]["tier_counts"]
    for tier in TIER_TAGS:
        assert tier in counts, f"tier_counts missing {tier}"


def test_required_tags_documented_in_exercise_bank():
    bank = (REFS / "exercise-bank.md").read_text()
    for tag in REQUIRED_TAGS:
        assert tag in bank, f"exercise-bank.md doesn't reference required tag {tag}"


def test_tier_tags_documented_in_exercise_bank():
    bank = (REFS / "exercise-bank.md").read_text()
    for tag in TIER_TAGS:
        assert tag in bank, f"exercise-bank.md doesn't reference tier tag {tag}"


def test_curriculum_step_ids_well_formed():
    """Steps in curriculum.md are like F1, S2, P3, RL4, CA1, etc."""
    text = (REFS / "curriculum.md").read_text()
    # Extract the section between the ``` fences containing the path
    m = re.search(r"```\n(=== FOUNDATIONS.+?)```", text, re.DOTALL)
    assert m, "curriculum.md path block not found"
    path = m.group(1)
    steps = re.findall(r"^([A-Z]{1,3}\d+)\.\s", path, re.MULTILINE)
    assert len(steps) >= 30, f"too few steps in curriculum: {len(steps)}"
    assert len(steps) == len(set(steps)), f"duplicate step IDs: {steps}"


def test_pattern_templates_exist_for_referenced_patterns():
    """Pattern A, B, C are claimed templates. D and E are inline. Verify A/B/C exist."""
    tpl_dir = ASSETS / "exercise-templates"
    expected = {"pattern-a-starter.py", "pattern-b-multiprocess.py", "pattern-c-asyncio.py"}
    have = {p.name for p in tpl_dir.iterdir()}
    missing = expected - have
    assert not missing, f"missing exercise templates: {missing}"


def test_skill_md_references_exist():
    skill = (ROOT / "SKILL.md").read_text()
    referenced = re.findall(r"references/([\w\-]+\.md)", skill)
    referenced += re.findall(r"assets/([\w\-/]+\.(?:md|json))", skill)
    referenced += re.findall(r"assets/(exercise-templates)", skill)
    for ref in set(referenced):
        path = ROOT / ("references" if ref.endswith(".md") and "exercise-templates" not in ref else "assets")
        # slightly clumsy: handle both
        candidates = [
            ROOT / "references" / ref,
            ROOT / "assets" / ref,
        ]
        assert any(c.exists() for c in candidates), f"SKILL.md references missing file: {ref}"


def test_skill_md_has_required_frontmatter():
    skill = (ROOT / "SKILL.md").read_text()
    fm_match = re.match(r"^---\n(.+?)\n---", skill, re.DOTALL)
    assert fm_match, "SKILL.md missing frontmatter"
    fm = fm_match.group(1)
    for key in ("name:", "description:", "license:"):
        assert key in fm, f"SKILL.md frontmatter missing {key}"


def test_incidents_md_covers_main_tiers():
    inc = (REFS / "incidents.md").read_text().lower()
    for term in ("replication", "partitioning", "consistency", "caching", "rate limiting"):
        assert term in inc, f"incidents.md missing coverage of {term}"


# Sources required to be cited under Tier 6 (issue #5).
TIER6_REQUIRED_SOURCES = [
    "Site Reliability Engineering",
    "SRE Workbook",
    "Release It!",
    "Production-Ready Microservices",
    "Observability Engineering",
]


def test_tier6_has_primary_sources_block():
    """Tier 6 must list the five primary sources (issue #5)."""
    text = (REFS / "curriculum.md").read_text()
    tier6 = re.search(r"## Tier 6:.+?(?=\n## )", text, re.DOTALL)
    assert tier6, "curriculum.md missing Tier 6 section"
    body = tier6.group(0)
    for src in TIER6_REQUIRED_SOURCES:
        assert src in body, f"Tier 6 missing primary source: {src}"


def test_progress_test_doc_validator_in_sync():
    """The validator inlined in test-progress-json.md should not be drastically out of date."""
    doc = (TESTS / "test-progress-json.md").read_text()
    # If the doc inlines a validator with REQUIRED_TOP_LEVEL, that list should
    # include the same fields the real validator requires.
    actual = (TESTS / "validate_progress.py").read_text()
    actual_required = re.search(r"REQUIRED_TOP_LEVEL\s*=\s*\[(.+?)\]", actual)
    assert actual_required, "couldn't find REQUIRED_TOP_LEVEL in real validator"
    real_fields = set(re.findall(r'"([\w_]+)"', actual_required.group(1)))

    doc_required = re.search(r"REQUIRED_TOP_LEVEL\s*=\s*\[(.+?)\]", doc)
    if doc_required:
        doc_fields = set(re.findall(r'"([\w_]+)"', doc_required.group(1)))
        missing = real_fields - doc_fields
        assert not missing, (
            f"test-progress-json.md inlines a stale validator missing: {missing}. "
            f"Update the doc's snippet (or remove it and reference validate_progress.py)."
        )


TESTS_LIST = [
    ("validator: template has placeholder errors", test_validator_template_has_placeholders),
    ("validator: filled fixture is VALID", test_validator_fixture_valid),
    ("template: top-level fields present", test_template_has_required_top_level_fields),
    ("template: required tags listed in coverage", test_template_practical_coverage_lists_all_required_tags),
    ("template: all tier tags present", test_template_practical_coverage_has_all_tiers),
    ("exercise-bank: required tags documented", test_required_tags_documented_in_exercise_bank),
    ("exercise-bank: tier tags documented", test_tier_tags_documented_in_exercise_bank),
    ("curriculum: step IDs well-formed and unique", test_curriculum_step_ids_well_formed),
    ("assets: pattern A/B/C templates exist", test_pattern_templates_exist_for_referenced_patterns),
    ("SKILL.md: referenced files exist", test_skill_md_references_exist),
    ("SKILL.md: required frontmatter present", test_skill_md_has_required_frontmatter),
    ("incidents.md: covers main tiers", test_incidents_md_covers_main_tiers),
    ("curriculum: Tier 6 has primary sources block", test_tier6_has_primary_sources_block),
    ("docs/validator: in sync", test_progress_test_doc_validator_in_sync),
]


def main():
    results = [run(name, fn) for name, fn in TESTS_LIST]
    passed = sum(results)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
