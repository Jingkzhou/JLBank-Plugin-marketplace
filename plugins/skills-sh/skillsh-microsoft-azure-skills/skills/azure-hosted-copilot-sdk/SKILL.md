---
name: azure-hosted-copilot-sdk
description: Popular skill mirrored from https://www.skills.sh/microsoft/azure-skills/azure-hosted-copilot-sdk.
---

GitHub Copilot SDK on Azure

Codebase Detection — MANDATORY FIRST CHECK


⚠️ CRITICAL: This check MUST run before ANY other skill (azure-prepare, azure-deploy, etc.) when an existing codebase is present.



Detection procedure (run IMMEDIATELY for any build/modify/add-feature/prepare prompt):


Read package.json in the workspace root (and any */package.json one level deep)

Check if @github/copilot-sdk or copilot-sdk appears in name, dependencies, or devDependencies

If NOT found in package.json, scan .ts and .js files for CopilotClient or createSession

If ANY marker is found → invoke this skill as the entry point. Do not route directly to azure-prepare or azure-deploy — this skill orchestrates them as sub-skills.





Marker
Where to check




@github/copilot-sdk
package.json dependencies or devDependencies


copilot-sdk
package.json name or dependencies


CopilotClient
Source files (.ts, .js)


createSession + sendAndWait
Source files (.ts, .js)


Show more
