# Minecraft MCP Server Bridge

A minimal repo to control a local Minecraft Java server via MCP (Model Context Protocol) tools in your IDE.

This repo includes everything you need to run the bridge:
- `.vscode/mcp.json` — MCP config (works out of the box in Cursor/compatible IDEs)
- `mcp_minecraft_server.py` — Python bridge (FastMCP + RCON + optional OpenAI translation)
- `.gitignore` — avoids committing secrets/heavy server data
- `server.properties.example` — safe template for local RCON setup

## Prerequisites
- Java 17+ and a Paper/Spigot server JAR (e.g., Paper 1.21.1)
- Python 3.10+
- Python packages: `mcrcon`, `openai`, and a FastMCP server implementation

Install Python deps:
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install mcrcon openai fastmcp || pip install mcrcon openai mcp-server-fastmcp
```

## Configure the Minecraft server (local only)
1) Create a `server/` folder next to this README and place `paper.jar` there.
2) Accept EULA:
```bash
echo "eula=true" > server/eula.txt
```
3) Create `server/server.properties` using the template:
```bash
cp server.properties.example server/server.properties
# edit rcon.password=CHANGE_ME to your secret
```
4) Save the RCON password to `server/.rcon_password` (read by the bridge):
```bash
echo "YOUR_RCON_PASSWORD" > server/.rcon_password
```
5) Start the server:
```bash
cd server
java -Xmx4G -jar paper.jar --nogui
```

Keep `server-ip=127.0.0.1` for demos so RCON isn’t exposed externally.

## Run the MCP bridge
In a new terminal (venv activated):
```bash
python mcp_minecraft_server.py
```
Your IDE can also auto‑launch it via `.vscode/mcp.json`.

Optional: enable natural‑language → command translation by exporting your key:
```bash
export OPENAI_API_KEY=sk-...   # or let the IDE prompt you
```

## Use the tool
From your IDE’s MCP palette, call `minecraft_run_command`:
- Literal: `"/say hello from MCP"`
- Natural language (with OPENAI key): `"set the time to day"` → `/time set day`

## Troubleshooting
- `RCON error: Authentication failed` → mismatch between `server/.rcon_password` and `rcon.password` in `server.properties`.
- `ECONNREFUSED` → server not running or wrong IP/port.
- LLM translation warnings → set `OPENAI_API_KEY` or use literal slash commands.

## Security & Hygiene
- Do not commit `server/.rcon_password` or real `server/server.properties` values.
- This repo binds RCON to `127.0.0.1` by default.
- The `.gitignore` excludes secrets, worlds, and logs by default.

Enjoy!
