# LegalZoom Plugin

AI-powered business legal assistance — contract review, document analysis, and attorney consultation via LegalZoom.

> **Disclaimer:** This plugin assists with legal workflows but does not provide legal advice. AI-generated analysis should be reviewed by qualified legal professionals before being relied upon for legal decisions.

## Commands

| Command | Description |
|---------|-------------|
| `/review-contract` | In-depth contract analysis with risk-scored findings and redline suggestions |
| `/attorney-assist` | Connect with a LegalZoom attorney who sees your full conversation context |

## How It Works

- **Review a contract** with `/review-contract` — upload a PDF, DOCX, or paste text and get risk-scored findings with suggested redlines
- **Connect with an attorney** via `/attorney-assist` for any business legal matter — the attorney gets your full conversation and analysis to give you quality advice

## Requirements

- LegalZoom connector enabled in your Claude app settings
- LegalZoom Business Attorney Plan for attorney consultations

## Troubleshooting

If LegalZoom MCP tools aren't connecting or aren't available, the most common fix is enabling the LegalZoom connector. Open your Claude app settings, go to **Connectors**, and make sure the LegalZoom connector is connected. See [CONNECTORS.md](CONNECTORS.md#troubleshooting-mcp-connection-issues) for detailed debugging steps.
