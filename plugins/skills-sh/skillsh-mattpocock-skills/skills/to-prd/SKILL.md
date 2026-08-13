---
name: to-prd
description: Popular skill mirrored from https://www.skills.sh/mattpocock/skills/to-prd.
---

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run /setup-matt-pocock-skills if not.

Process



Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.




Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.




Check with the user that these seams match their expectations.


Write the PRD using the template below, then publish it to the project issue tracker. Apply the ready-for-agent triage label - no need for additional triage.


Problem Statement

The problem that the user is facing, from the user's perspective.
Show more
