# Connectors

## LegalZoom MCP Server (Required)

The LegalZoom MCP server provides attorney consultation and escalation functionality — seamless AI-to-human handoff with full context preservation.

### Configuration

```json
{
  "mcpServers": {
    "legalzoom": {
      "type": "http",
      "url": "https://www.legalzoom.com/mcp/claude/v1"
    }
  }
}
```

### Authentication

The LegalZoom MCP server requires OAuth authentication:
- Users will be prompted to authenticate with their LegalZoom account
- Subscription tier determines available features
- Entitlements are checked in real-time

### Available Tools

| Tool | Description |
|------|-------------|
| `check_attorney_consultation_entitlements` | Check if the user has attorney consultation access |
| `get_consultation_topics` | Get available attorney consultation specializations |
| `get_valid_locations` | Get valid US state/territory codes for attorney matching |
| `get_attorney_availability` | Check when attorneys are available by topic and location |
| `request_attorney_review` | Connect user with a LegalZoom attorney for professional legal review |
| `attach_document_to_attorney_review` | Attach documents to an existing attorney review |
| `add_bap_to_cart` | Add an attorney consultation plan to the user's cart |

### Troubleshooting MCP Connection Issues

If you can't connect to the LegalZoom MCP server or tools aren't available, work through the following:

#### 1. Verify the LegalZoom Connector Is Enabled

The most common issue is that the LegalZoom connector hasn't been set up. Open your Claude app settings, navigate to the **Connectors** section, and make sure the **LegalZoom** connector is connected. If it isn't listed or shows as disconnected, add it and follow the prompts to complete setup.

#### 2. Confirm the Plugin Is Loaded

If the plugin is installed but the MCP tools don't appear, the connector may not have been picked up. Try:
- Restarting your Claude session after enabling or modifying the connector
- Checking that the LegalZoom connector shows as connected in your Claude app settings

#### 3. Authentication Failures

The LegalZoom MCP server requires OAuth authentication. If tools are visible but calls fail:
- You may need to re-authenticate with your LegalZoom account
- Your session token may have expired — restarting the session can trigger a fresh auth flow
- Ensure your LegalZoom account is active and in good standing

#### 4. Network and Server Issues

If the connector is configured correctly but calls still fail:
- Check your network connection
- The LegalZoom MCP endpoint may be temporarily unavailable — try again later
- If the issue persists, visit [legalzoom.com](https://www.legalzoom.com) directly to verify service availability

#### 5. Partial Failures

Some tools may work while others fail. This can indicate:
- Entitlement issues (your plan may not include certain features)
- Jurisdiction-specific availability constraints
- Temporary service degradation on specific endpoints

In all cases, the plugin will stop at the point of failure and report what happened. It will never fabricate responses or simulate success.
