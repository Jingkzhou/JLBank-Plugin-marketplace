---
name: writing-great-skills
description: Popular skill mirrored from https://www.skills.sh/mattpocock/skills/writing-great-skills.
---

A skill exists to wrangle determinism out of a stochastic system. Predictability — the agent taking the same process every run, not producing the same output — is the root virtue; every lever below serves it.

Bold terms are defined in GLOSSARY.md; look them up there for the full meaning.

Invocation

Two choices, trading different costs:


A model-invoked skill keeps a description, so the agent can fire it autonomously and other skills can reach it (you can still type its name too). It contributes to context load — the description sits in the window every turn. Mechanics: omit disable-model-invocation, and write a model-facing description with rich trigger phrasing ("Use when the user wants…, mentions…").

A user-invoked skill strips the description from the agent's reach: only you, typing its name, can invoke it — and no other skill can. Zero context load, but it spends cognitive load: you are the index that must remember it exists. Mechanics: set disable-model-invocation: true; the description becomes human-facing — a one-line summary, trigger lists stripped.


Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a router skill: one user-invoked skill that names the others and when to reach for each.

Writing the description

A model-invoked description does two jobs — state what the skill is, and list the branches that should trigger it. Every word increases context load, so a description earns even harder pruning than the body:
Show more
