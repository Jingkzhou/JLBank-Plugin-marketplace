---
name: developing-genkit-python
description: Popular skill mirrored from https://www.skills.sh/firebase/agent-skills/developing-genkit-python.
---

Genkit Python

Prerequisites


Runtime: Python 3.14+, uv for deps (install).

CLI: genkit --version — install via npm install -g genkit-cli if missing.


New projects: Setup (bootstrap + env). Patterns and code samples: Examples.

Hello World

from genkit import Genkit
from genkit.plugins.google_genai import GoogleAI

ai = Genkit(
    plugins=[GoogleAI()],
    model='googleai/gemini-flash-latest',
)

Show more
