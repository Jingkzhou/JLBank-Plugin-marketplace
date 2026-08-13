---
name: review
description: Popular skill mirrored from https://www.skills.sh/mattpocock/skills/review.
---

Two-axis review of the diff between HEAD and a fixed point the user supplies:


Standards — does the code conform to this repo's documented coding standards?

Spec — does the code faithfully implement the originating issue / PRD / spec?


Both axes run as parallel sub-agents so they don't pollute each other's context, then this skill aggregates their findings.

The issue tracker should have been provided to you — run /setup-matt-pocock-skills if docs/agents/issue-tracker.md is missing.

Process

1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, main, HEAD~5, etc. If they didn't specify one, ask for it.

Capture the diff command once: git diff <fixed-point>...HEAD (three-dot, so the comparison is against the merge-base). Also note the list of commits via git log <fixed-point>..HEAD --oneline.

Before going further, confirm the fixed point resolves (git rev-parse <fixed-point>) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.
Show more
