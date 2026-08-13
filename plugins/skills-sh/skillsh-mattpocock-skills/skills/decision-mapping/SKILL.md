---
name: decision-mapping
description: Popular skill mirrored from https://www.skills.sh/mattpocock/skills/decision-mapping.
---

This skill is invoked when a loose idea requires more than one agent session to turn into a plan. It creates a stateful decision map in a markdown file, and drives the user through a sequence of tickets to resolve the open questions - which may require either prototyping, research or grilling. The map is domain-agnostic: it plans engineering work, course content, or anything else that fits the same shape.

The Decision Map

The decision map is a single compact Markdown file, one per planning effort, git-tracked alongside the project. It is the canonical artifact — the whole map is loaded as context into every session, so it must stay compact.

Assets created during tickets should be linked to from the map, not duplicated within it.

Structure

Entries ("tickets"), each its own section keyed by a short dash-case slug that
reads as a mini-title (e.g. relational-db, auth-strategy, cache-layer) —
terse enough to stay token-efficient, and unique within the map.

## relational-db: Relational Or Non-Relational Database?

Show more
