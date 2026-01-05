# Minecraft MCP Server Bridge (Sharable)

This folder contains a portable Model Context Protocol (MCP) config that lets your IDE call a tool named `minecraft_run_command`, which forwards commands to a local Minecraft Java server over RCON. It works with Paper/Spigot servers and runs entirely on localhost.

## What you get
- `mcp.json` — drop this into any repo as `.vscode/mcp.json` to enable the MCP server in an MCP‑aware IDE (Cursor, etc.).
- You also need the Python bridge script from your project: `mcp_minecraft_server.py` (place in the project root).

---
## Prerequisites
- Minecraft Java server (Paper recommended) running locally
  - Java 17+ (Java 21 also fine)
  - Paper JAR (e.g., 1.21.1)
- Python 3.10+
- Python packages: `mcrcon`, `openai`, and an MCP server package (FastMCP). Install:
  
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  pip install mcrcon openai mcp-server-fastmcp || pip install mcrcon openai fastmcp || true
  ```
  
  Notes:
  - The bridge imports `from mcp.server.fastmcp import FastMCP`. If your environment uses a different package name, install the variant that provides `mcp.server.fastmcp` (some distributions package it as `fastmcp` or `mcp-server-fastmcp`).

---
## Configure your Paper server
1. Create a server folder (e.g., `server/`) and place your `paper.jar` there.
2. Accept the EULA:
   ```bash
   cd server
   echo "eula=true" > eula.txt
   ```
3. Enable RCON in `server.properties` (create or edit):
   ```properties
   enable-rcon=true
   rcon.port=25575
   rcon.password=REDACTED_PASSWORD
   server-ip=127.0.0.1
   online-mode=false   # optional for local demo
   ```
4. Save the RCON password in a local file the bridge reads:
   ```bash
   echo "REDACTED_PASSWORD" > .rcon_password
   ```
5. Start the server:
   ```bash
   java -Xmx4G -jar paper.jar --nogui
   ```

Security: keep `server-ip=127.0.0.1` for demos so RCON isn’t exposed.

---
## Add the MCP config to your project
1. Copy `mcp.json` to your project at `.vscode/mcp.json`.
2. Put `mcp_minecraft_server.py` in the project root (same folder shown as `${workspaceFolder}` in the config).
3. Optional: Set your OpenAI key in the shell if you want natural‑language → command translation:
   ```bash
   export OPENAI_API_KEY=sk-...  # or let the IDE prompt you
   ```

The config in `mcp.json` runs:
```json
{
  "servers": {
    "minecraft-mcp": {
      "command": "python",
      "args": ["${workspaceFolder}/mcp_minecraft_server.py"],
      "env": { "OPENAI_API_KEY": "${input:OPENAI_API_KEY}" },
      "cwd": "${workspaceFolder}"
    }
  }
}
```

---
## Run the MCP server
In an MCP‑aware IDE (Cursor):
- The MCP server will auto‑launch from `.vscode/mcp.json`, or run it manually:
  ```bash
  source .venv/bin/activate
  python mcp_minecraft_server.py
  ```

---
## Use the tool
Call the `minecraft_run_command` tool from your IDE:
- Literal command (no OpenAI needed):
  - Input: `"/say hello from MCP"`
- Natural language (requires `OPENAI_API_KEY`):
  - Input: `"set the time to day"` → translated to `/time set day`

The server’s response is returned in the IDE, and the effect happens immediately in game.

---
## Troubleshooting
- `RCON error: Authentication failed` → password mismatch. Update `server/.rcon_password` or `server.properties`.
- `RCON error: [WinError]/ECONNREFUSED` → server not running or wrong port/IP.
- `LLM translation error` or warning about `OPENAI_API_KEY` → set the key or send a literal slash command.
- Nothing happens in game → confirm your Paper console shows RCON startup and that the world is running.

---
## Recommended .gitignore
Add to your repo to avoid leaking secrets or heavy assets:
```
server/.rcon_password
server/world/
server/logs/
.venv/
.bot/
bot/bot.log
.vscode/
```

---
## License & credit
- PaperMC server is third‑party. This MCP bridge script is yours to share; include attribution if you publish.
