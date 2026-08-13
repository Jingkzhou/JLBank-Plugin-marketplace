# Atlassian Teamwork Graph CLI

A skills-only plugin repository with thin adapters for coding agents that support repository plugins, extensions, or skills.

## Install

### Claude Code

```text
/plugin marketplace add atlassian-labs/twg-plugins
/plugin install atlassian-twg-cli@atlassian-twg-cli
```

### Codex

```bash
codex plugin marketplace add atlassian-labs/twg-plugins
codex plugin add twg@twg
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add atlassian-labs/twg-plugins
copilot plugin install atlassian-twg-cli@atlassian-twg-cli
```

### Gemini CLI

```bash
gemini extensions install https://github.com/atlassian-labs/twg-plugins
```

### Devin CLI

```bash
devin plugins install atlassian-labs/twg-plugins
```

### Pi

```bash
pi install git:github.com/atlassian-labs/twg-plugins
```

### Hermes Agent

```bash
hermes plugins install atlassian-labs/twg-plugins --enable
```

Cursor and Qoder can ingest their repository manifests directly. Other skill-capable agents can load `skills/twg-setup/SKILL.md` without a host adapter.

## Setup

Install the plugin for your coding agent, then run `/twg-setup` to install or verify TWG CLI and sign in.

The package contains no CLI binary, runtime wrapper, or credentials. The installed `twg` CLI owns execution and authentication.

Using a coding agent in the browser? Install the Atlassian Rovo MCP plugin instead.

Learn more: https://developer.atlassian.com/cloud/twg-cli/
