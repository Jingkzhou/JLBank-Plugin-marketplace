---
name: expo-api-routes
description: Popular skill mirrored from https://www.skills.sh/expo/skills/expo-api-routes.
---

When to Use API Routes

Use API routes when you need:


Server-side secrets — API keys, database credentials, or tokens that must never reach the client

Database operations — Direct database queries that shouldn't be exposed

Third-party API proxies — Hide API keys when calling external services (OpenAI, Stripe, etc.)

Server-side validation — Validate data before database writes

Webhook endpoints — Receive callbacks from services like Stripe or GitHub

Rate limiting — Control access at the server level

Heavy computation — Offload processing that would be slow on mobile


When NOT to Use API Routes

Avoid API routes when:
Show more
