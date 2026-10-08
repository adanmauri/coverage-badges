---
name: retro
description: "Run a session retrospective: detect lessons learned and friction, then propose or apply concrete improvements to the agentic workspace (rules, skills, AGENTS.md, docs, settings, checks) and log the iteration. Treats each session as one turn of a self-improvement loop. Use when wrapping up a substantive session, or whenever the user asks to capture lessons / improve the workspace."
---

# Retro

## Objective

Turn what happened in this session into a durable improvement of the workspace, so the next
session starts better. One retro is one iteration of the loop, recorded in
[`docs/RETRO-LOG.md`](../../../docs/RETRO-LOG.md).

## Workflow

1. **Collect signals** from the session, concretely (quote the moment, not a paraphrase):
   - Corrections: the user said "no", "that's wrong", or redid something by hand.
   - Friction: repeated questions, failed commands, missing context that had to be dug up.
   - Wins: an approach the user explicitly confirmed and that should become the default.
   - Drift: a rule, skill, or doc that turned out stale, contradictory, or missing.

2. **Diagnose each signal** to the asset that should have prevented it:

   | Signal was about                                   | Fix goes in                                                                  |
   |----------------------------------------------------|------------------------------------------------------------------------------|
   | How to work in this repo                           | `AGENTS.md`                                                                  |
   | A recurring workflow                               | a skill under `.agents/skills/`                                              |
   | A constraint on code                               | `.agents/rules/`                                                             |
   | Layout, or the bar for "done"                      | `AGENTS.md`                                                                  |
   | A decision and its rationale                       | a new or superseding ADR in `docs/adr/`                                      |
   | How to set up, run or check things                 | `docs/DEVELOPMENT.md`                                                        |
   | A check that should have caught it                 | a hook in `.pre-commit-config.yaml` or a check in `tooling/`                 |
   | A command the agent kept asking permission for     | `.claude/settings.json` (shared) or `.claude/settings.local.json` (personal) |
   | A personal preference of the user, not a repo rule | the agent's own memory, not the repo                                         |
   | Work still to do                                   | an item in `TODO.md`                                                         |

   Drop signals that only mattered to this session. Prefer editing an existing asset over
   adding a new one; prefer deleting a stale line over adding a correcting one.

3. **Propose** the changes as a short list: signal → asset → exact edit. Ask the user which
   to apply. Apply directly only what the user already asked for in this session.

4. **Apply** the approved edits on a branch (`chore/...`), never on `main`.
   Edit only canonical files under `.agents/`, then run `make sync-agents` so the tool pointers
   stay in sync, and `make check` before committing.

5. **Log the iteration** at the top of `docs/RETRO-LOG.md`:

   ```markdown
   ## YYYY-MM-DD: <one-line theme>

   - **Context:** what the session was about.
   - **Changes:** what was edited, and why (signal → asset).
   - **Follow-ups:** what was proposed but not applied, or items added to `TODO.md`.
   ```

6. **Report** the list of applied changes and follow-ups. Do not commit unless asked.

## Rules

- Evidence over opinion: every change traces to a concrete moment of the session.
- No signals, no changes: if the session had none, log a one-line "no changes" entry. Never
  invent a lesson to fill the log.
- Prefer a check over a sentence: when a rule was broken, ask first whether a hook or a
  `tooling/` check could have caught it.
- Keep assets terse; a rule points to where the rationale lives instead of repeating it.
- Never weaken a guardrail or a check in a retro without the user's approval.
- No tool attribution in any edited file (see `create-commit`).
