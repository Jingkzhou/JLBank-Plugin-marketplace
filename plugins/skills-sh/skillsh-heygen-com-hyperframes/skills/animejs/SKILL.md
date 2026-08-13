---
name: animejs
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/animejs.
---

Anime.js for HyperFrames

HyperFrames can seek Anime.js instances through its animejs runtime adapter. The composition owns the animation objects; HyperFrames owns the clock.

Contract


Create animations or timelines synchronously during composition initialization.

Set autoplay: false so Anime.js does not advance on its own clock.

Register every returned animation or timeline on window.__hfAnime.

Use finite durations and loop counts.

Avoid callbacks that mutate DOM based on wall-clock time, network state, or unseeded randomness.


The adapter seeks every registered instance with instance.seek(timeMs), where timeMs is HyperFrames time in milliseconds.

Basic Pattern
Show more
