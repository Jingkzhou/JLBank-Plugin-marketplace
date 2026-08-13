---
name: compress
description: Popular skill mirrored from https://www.skills.sh/juliusbrussee/caveman/compress.
---

Caveman Compress

Purpose

Compress natural language files (CLAUDE.md, todos, preferences) into caveman-speak to reduce input tokens. Compressed version overwrites original. Human-readable backup saved as <filename>.original.md.

Trigger

/caveman:compress <filepath> or when user asks to compress a memory file.

Process



This SKILL.md lives alongside scripts/ in the same directory. Find that directory.




Run:




cd <directory_containing_this_SKILL.md> && python3 -m scripts <absolute_filepath>
Show more
