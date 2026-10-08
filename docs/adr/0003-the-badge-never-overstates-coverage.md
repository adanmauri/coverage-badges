# 0003. The badge never overstates coverage

**Status:** Accepted · **Date:** 2026-10-07

## Context

A badge is read as a claim about the code. Two choices decide whether that claim is honest: which
number each report format contributes, and how that number is shown. The previous pre-generated
badges rounded to steps of 5% and printed one decimal (`85.0%` for 83%), a precision the value did
not have. Rounding has a sharper edge: 99.96% rounds to 100.0%, a claim of full coverage.

## Options

- **Round to the nearest step (5%, 1%):** fewer distinct badges, but shows values the code does
  not have.
- **Round to one decimal:** precise, but can round up across a color threshold (79.96 to 80.0,
  green) or to 100%.
- **Truncate to one decimal:** precise, and every shown value is at most the real one.

## Decision

- The value is **truncated** to one decimal: 99.96% shows as 99.9%. A float tolerance of 1e-6
  absorbs representation noise, so 28.999999999 shows as 29.0%.
- Each format contributes **line coverage**, the one metric all of them report: Cobertura
  `line-rate`, JaCoCo's report-level `LINE` counter, LCOV `LH`/`LF`, Istanbul `total.lines`.
  Go reports statements; a block listed twice (with `-coverpkg`) counts once, covered if any copy
  was. coverage.py JSON contributes its own total, which includes branches when branch coverage is
  enabled, so the badge matches what `coverage report` prints.
- A report with no coverable lines is an error, not 0% or 100%.

## Consequences

### Positive

- A shown value is never higher than the real one, and colors never jump a threshold upward.

### Negative / trade-offs

- The badge can show 0.1% less than the tool's own summary, which rounds.
- Branch coverage is not shown separately.

### Follow-ups

- [`action-guardrails.md`](../../.agents/rules/action-guardrails.md) cites this ADR for values.
