---
name: three
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/three.
---

Three.js for HyperFrames

HyperFrames supports Three.js through its three runtime adapter. The adapter does not own your scene. It publishes HyperFrames time and dispatches a seek event so your composition can render the exact frame.

Contract


Create the scene, camera, renderer, materials, and assets synchronously when possible.

Render from HyperFrames time, not wall-clock time.

Listen for the hf-seek event and render exactly that time.

Load models, textures, and HDRIs before render-critical seeking. Do not fetch them at seek time.

Avoid requestAnimationFrame or renderer.setAnimationLoop as the source of truth for render-critical motion.


The adapter sets window.__hfThreeTime and dispatches new CustomEvent("hf-seek", { detail: { time } }) on each seek.

Basic Pattern
Show more
