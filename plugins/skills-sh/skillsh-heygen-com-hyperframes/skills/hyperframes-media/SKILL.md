---
name: hyperframes-media
description: Popular skill mirrored from https://www.skills.sh/heygen-com/hyperframes/hyperframes-media.
---

HyperFrames Media

Create the audio and media assets a composition needs — voiceover (TTS), background music + sound effects, transcription, captions, background removal — then consume and animate that data in HTML. For placing assets into compositions, see hyperframes-core.

The audio engine — one source for TTS · BGM · SFX

Workflows do NOT hand-roll audio or vendor a copy. There is one engine — scripts/audio.mjs — that takes a neutral audio_request.json and writes audio_meta.json (plus assets under assets/voice|bgm|sfx):

# <MEDIA_DIR> = this skill's directory
node <MEDIA_DIR>/scripts/audio.mjs --request ./audio_request.json --hyperframes . --out ./audio_meta.json


All three capabilities degrade on ONE switch — whether a HeyGen credential is present (resolved from $HEYGEN_API_KEY / $HYPERFRAMES_API_KEY / ~/.heygen, not the CLI):
Show more
