---
name: firebase-ai-logic
description: Popular skill mirrored from https://www.skills.sh/firebase/agent-skills/firebase-ai-logic.
---

Firebase AI Logic Basics

Overview

Firebase AI Logic is a product of Firebase that allows developers to add gen AI to their mobile and web apps using client-side SDKs. You can call Gemini models directly from your app without managing a dedicated backend. Firebase AI Logic, which was previously known as "Vertex AI for Firebase", represents the evolution of Google's AI integration platform for mobile and web developers.

It supports the two Gemini API providers:


Gemini Developer API: It has a free tier ideal for prototyping, and pay-as-you-go for production

Vertex AI Gemini API: Ideal for scale with enterprise-grade production readiness, requires Blaze plan


Use the Gemini Developer API as a default, and only Vertex AI Gemini API if the application requires it.

Setup & Initialization

Prerequisites


Before starting, ensure you have Node.js 16+ and npm installed. Install them if they aren’t already available.

Identify the platform the user is interested in building on prior to starting: Android, iOS, Flutter or Web.

If their platform is unsupported, Direct the user to Firebase Docs to learn how to set up AI Logic for their application (share this link with the user https://firebase.google.com/docs/ai-logic/get-started)

Show more
