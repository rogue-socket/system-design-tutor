# Practical Coverage Test

This test verifies that practical exercise coverage is broad and measurable across the course, not concentrated in a few familiar topics.

## What to check

From `~/system-design/progress.json`, inspect `practical_coverage`:

- `tier_counts` has non-zero values in the tiers the learner has already studied.
- `required_tags_missing` shrinks over time.
- `coverage_score` increases monotonically unless progress is reset.

Required tags to complete before course completion:
- `required-consistent-hashing`
- `required-replication-lag`
- `required-idempotency`
- `required-distributed-rate-limiter`
- `required-failure-injection`

## Coverage minimums

Use the standard in `references/curriculum.md`:

- Tier 1: >= 1 exercise
- Tier 2: >= 2 exercises
- Tier 3: >= 2 exercises
- Tier 4: >= 2 exercises
- Tier 5: >= 1 exercise
- Tier 6: >= 2 exercises
- Tier 7: >= 2 exercises
- Tier 8: >= 3 integration builds/interviews

## Scenario checks

### Scenario A: Mid-course learner

If learner has finished through Tier 3 theory:
- `tier1-storage`, `tier2-replication`, `tier3-partitioning` should be >= 1 each.
- At least one of `required-consistent-hashing` or `required-replication-lag` should be complete.

### Scenario B: Reliability stage

After completing rate limiting exercises:
- `tier6-reliability` should increment.
- `required-distributed-rate-limiter` should move from missing to completed.

### Scenario C: Final readiness

Before calling course complete:
- `required_tags_missing` must be empty.
- `coverage_score` should be `1.0`.
- Tier minimums above should be satisfied.

## Pass criteria

- Coverage data exists and is valid schema.
- Required tags are tracked correctly as exercises complete.
- Course completion is blocked until required practical tags are complete.
