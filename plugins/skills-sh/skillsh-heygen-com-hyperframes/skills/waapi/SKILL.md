---
name: waapi
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/waapi.
---

Web Animations API for HyperFrames

HyperFrames can seek Web Animations API animations through its waapi runtime adapter. WAAPI is useful when you want native browser keyframes with JavaScript-created timing and no GSAP dependency.

Contract


Create animations synchronously during composition initialization.

Use element.animate(...) with finite duration and iterations.

Use fill: "both" so seeked states persist.

Pause animations after creation or let the adapter pause them on first seek.

Avoid callbacks and promises for render-critical state.


The adapter calls document.getAnimations(), sets each animation's currentTime to HyperFrames time in milliseconds, then pauses it.

Basic Pattern

<div id="orb" class="clip orb" data-start="2" data-duration="3" data-track-index="2"></div>

Show more
