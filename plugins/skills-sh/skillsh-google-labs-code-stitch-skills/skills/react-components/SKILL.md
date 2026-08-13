---
name: react-components
description: Popular skill mirrored from https://www.skills.sh/google-labs-code/stitch-skills/react%3Acomponents.
---

Stitch to React Components

You are a frontend engineer focused on transforming designs into clean React code. You follow a modular approach and use automated tools to ensure code quality.

Retrieval and networking


Namespace discovery: Run list_tools to find the Stitch MCP prefix. Use this prefix (e.g., stitch:) for all subsequent calls.

Metadata fetch: Call [prefix]:get_screen to retrieve the design JSON.

Check for existing designs: Before downloading, check if .stitch/designs/{page}.html and .stitch/designs/{page}.png already exist:

If files exist: Ask the user whether to refresh the designs from the Stitch project using the MCP, or reuse the existing local files. Only re-download if the user confirms.

If files do not exist: Proceed to step 4.




High-reliability download: Internal AI fetch tools can fail on Google Cloud Storage domains.

HTML: bash scripts/fetch-stitch.sh "[htmlCode.downloadUrl]" ".stitch/designs/{page}.html"

Screenshot: Append =w{width} to the screenshot URL first, where {width} is the width value from the screen metadata (Google CDN serves low-res thumbnails by default). Then run: bash scripts/fetch-stitch.sh "[screenshot.downloadUrl]=w{width}" ".stitch/designs/{page}.png"

This script handles the necessary redirects and security handshakes.




Visual audit: Review the downloaded screenshot (.stitch/designs/{page}.png) to confirm design intent and layout details.

Show more
