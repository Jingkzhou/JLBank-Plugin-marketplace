---
name: developing-genkit-js
description: Popular skill mirrored from https://www.skills.sh/firebase/agent-skills/developing-genkit-js.
---

Genkit JS

Prerequisites

Ensure the genkit CLI is available.


Run genkit --version to verify. Minimum CLI version needed: 1.29.0

If not found or if an older version (1.x < 1.29.0) is present, install/upgrade it: npm install -g genkit-cli@^1.29.0.


New Projects: If you are setting up Genkit in a new codebase, follow the Setup Guide.

Hello World

import { z, genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

Show more
