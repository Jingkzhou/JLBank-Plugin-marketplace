---
name: typegpu
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/typegpu.
---

TypeGPU / WebGPU for HyperFrames

HyperFrames supports TypeGPU and raw WebGPU through its typegpu runtime adapter. The adapter does not own your pipeline. It publishes HyperFrames time and dispatches a seek event so your composition can render the exact GPU frame.

Contract


Initialize WebGPU asynchronously (await navigator.gpu.requestAdapter()), but register all GSAP tweens synchronously — before any await. The HyperFrames player reads the timeline immediately at page load.

Render from HyperFrames time, not performance.now().

Listen for the hf-seek event and re-render at exactly that time.

Guard against environments where WebGPU is unavailable — the adapter does not check for you.

For video renders, call await device.queue.onSubmittedWorkDone() after submitting GPU work to ensure the canvas is flushed before the frame is captured.


The adapter sets window.__hfTypegpuTime and dispatches new CustomEvent("hf-seek", { detail: { time } }) on each seek.

Basic Pattern
Show more
