---
name: gsap
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/gsap.
---

GSAP

HyperFrames Contract

HyperFrames controls GSAP through its gsap runtime adapter. Create a paused timeline synchronously, register it on window.__timelines with the exact data-composition-id, and let HyperFrames seek it.

<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });

  tl.from(".title", { y: 48, opacity: 0, duration: 0.6, ease: "power3.out" }, 0);
  tl.to(".accent", { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.25);

  window.__timelines["main"] = tl; // key must equal data-composition-id on the composition root
</script>

Show more
