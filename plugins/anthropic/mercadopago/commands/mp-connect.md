---
description: Verify or manually trigger Mercado Pago MCP authentication
license: Apache-2.0
copyright: "Copyright (c) 2026 Mercado Pago (MercadoLibre S.R.L.)"
allowed-tools: [Bash]
---

# /mp-connect

The Mercado Pago MCP server is registered automatically when the plugin loads. Authentication is triggered by Claude Code the first time the MCP is used — no manual setup needed.

Use this command only if the connection is broken or you want to verify the status.

---

> **Note**: Mercado Pago also supports OAuth-based authentication for marketplace flows (where sellers authorize access to their accounts). This command configures the primary Access Token for the MCP server. For OAuth-based marketplace integrations, use `/mp-integrate product=marketplace`.

### Pre-check: Is MCP already connected?
## Step 1 — Check status

`ListMcpResourcesTool` always returns "No resources found" for this MCP and is **not** a reliable check. The bootstrap tools `authenticate` / `complete_authentication` always exist and prove nothing.

Verify by attempting to call `mcp__plugin_mercadopago_mcp__application_list`:

- The tool is callable AND returns a real application payload (with `site_id`, etc.) → tell the user: "✓ Connected and ready." and **stop**.
- The tool is not in your capabilities, or it returns an auth error → **do NOT ask the user to run `/mcp`**. Continue to Step 2.

---

## Step 2 — Start OAuth directly

Call `mcp__plugin_mercadopago_mcp__authenticate`. Show the returned URL as a clickable link:

> Open this URL to connect Mercado Pago:
> **{authorization_url}**
>
> When you see **"Authentication Successful"** in the browser, come back and say anything — I'll verify automatically.

When the user responds:
- **Call `application_list` directly.** If the browser showed "Authentication Successful", the local MCP server already processed the callback and the token is live.
- **Do NOT call `complete_authentication` first** — it will hang trying to reach a socket that was already closed.
- Only if `application_list` fails AND the browser showed an error (not "Authentication Successful") → call `complete_authentication`. ⚠️ **Do not ask the user to paste the callback URL** — it contains a sensitive OAuth code. Ask them to re-run the flow (`/mp-connect`) instead.

**`not-found`** → the plugin is not loaded. Tell the user to run `/reload-plugins` and then `/mp-connect` again.

---

## Step 3 — Verify

Attempt to call `mcp__plugin_mercadopago_mcp__application_list` again.

- Returns a real payload → "✓ Connected and ready."
- Still no tools → "Not connected. Try restarting Claude Code and running `/mp-connect` again."

---

## Other IDEs

Add the server manually via your IDE's MCP settings with URL `https://mcp.mercadopago.com/mcp` (HTTP transport), then follow the authentication prompt your IDE shows.

- **Cursor** → `~/.cursor/mcp.json` → `"mercadopago": { "type": "http", "url": "https://mcp.mercadopago.com/mcp" }`
- **VS Code** → `settings.json` → `"mcp.servers": { "mercadopago": { "type": "http", "url": "https://mcp.mercadopago.com/mcp" } }`
- **Windsurf** → Settings → MCP Servers → add HTTP server with that URL.

---

## Windows: plugin not loading from cache

If you're on Windows and the plugin commands (e.g. `/mp-test-cards`, `/mp-integrate`) are not recognized, the plugin may be installed but not loaded by the harness.

**Diagnose:**
```powershell
# Check if the plugin files are in the expected cache location
Test-Path "$env:APPDATA\Claude\plugins\cache\claude-plugins-official\mercadopago"
# Also check without the "claude-plugins-official" subdirectory:
Test-Path "$env:APPDATA\Claude\plugins\cache\mercadopago"
```

**Fix — option 1 (preferred): reinstall via CLI**
```powershell
claude plugin uninstall mercadopago
claude plugin install mercadopago
```
Then restart Claude Code.

**Fix — option 2: copy `.mcp.json` manually**

If the MCP server is the only thing missing (skills load but MCP calls fail):
```powershell
copy plugins\mercadopago\.mcp.json .
```
Restart Claude Code.

**Fix — option 3: verify plugin.json path**

Claude Code on Windows reads the plugin registry from `%APPDATA%\Claude\plugins\`. If the `plugin.json` is present but the plugin still isn't recognized, check that the directory name matches exactly (`mercadopago`, not `mercadopago-1` or similar):
```powershell
Get-ChildItem "$env:APPDATA\Claude\plugins\cache" -Recurse -Filter "plugin.json" | Select-Object FullName
```

---

## Manual plugin install (without `claude plugin install`)

If you installed the plugin by copying files manually (not via `claude plugin install`), the MCP server is **not** auto-registered. Fix it in two steps:

1. Copy `plugins/mercadopago/.mcp.json` from this repo to your **project root**:
   ```bash
   cp plugins/mercadopago/.mcp.json .
   ```
2. Restart Claude Code — it reads `.mcp.json` from the project root on startup and registers the MCP server at `https://mcp.mercadopago.com/mcp` automatically.

> **Not needed when installing via `claude plugin install`** — that command handles `.mcp.json` placement automatically.

---

## Migrating from v1 (keychain)

```bash
# macOS
security delete-generic-password -a "access_token" -s "mercadopago-claude-plugin"
# Linux
secret-tool clear service "mercadopago-claude-plugin" account "access_token"
```
