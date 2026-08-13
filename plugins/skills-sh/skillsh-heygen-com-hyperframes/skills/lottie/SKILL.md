---
name: lottie
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/lottie.
---

Lottie for HyperFrames

HyperFrames can seek both lottie-web and dotLottie players through its lottie runtime adapter. Lottie is a strong fit because the animation timeline is already encoded in the asset; HyperFrames only needs a player object it can seek.

Contract


Load assets from local project files, usually under assets/.

Set autoplay: false.

Prefer loop: false unless the user explicitly wants a loop.

Register every returned animation or player on window.__hfLottie.

Keep the Lottie container dimensions stable with CSS.


The adapter seeks lottie-web with goToAndStop(timeMs, false) and dotLottie with frame or percentage APIs depending on player shape.

lottie-web Pattern
Show more
