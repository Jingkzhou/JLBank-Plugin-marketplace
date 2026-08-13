---
name: css-animations
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/css-animations.
---

CSS Animations for HyperFrames

HyperFrames can seek CSS keyframe animations through its css runtime adapter. Use this for simple repeated motifs, background motion, shimmer, glow, masks, and non-sequenced decoration.

For scene choreography, GSAP is usually clearer. CSS animations work best when the motion belongs to one element and has a fixed duration.

Contract


Put the animated element in the DOM before runtime initialization finishes.

Give timed elements a data-start value so local animation time matches the clip.

Use finite animation-duration and animation-iteration-count because the negative-delay fallback cannot represent unbounded duration in environments without WAAPI-backed CSS animations.

Prefer animation-fill-mode: both so seeked states hold before and after active motion.

Avoid wall-clock JavaScript, hover-triggered state, and class toggles that depend on user events.


The adapter discovers elements with computed animation-name, seeks their browser Animation handles when available, and falls back to pausing with negative animation-delay.

Basic Pattern
Show more
