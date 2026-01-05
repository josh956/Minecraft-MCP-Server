# mcp_minecraft_server.py
import os
from pathlib import Path

from mcrcon import MCRcon
from mcp.server.fastmcp import FastMCP, Context  # FastMCP provides the .tool() decorator

# ---- Config ----
BASE_DIR = Path(__file__).resolve().parent
SRV_DIR = BASE_DIR / "server"
RCON_PW_FILE = SRV_DIR / ".rcon_password"

RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = RCON_PW_FILE.read_text().strip() if RCON_PW_FILE.exists() else ""

# Natural-language -> command translation (optional)
USE_LLM_TRANSLATION = True

# Set OPENAI_API_KEY in your shell; script will read it at runtime
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ---- MCP server ----
mcp = FastMCP("minecraft-mcp")

@mcp.tool()
async def minecraft_run_command(request: str, ctx: Context) -> str:
    """
    Run a Minecraft server command via RCON.
    - If `request` starts with '/', it's sent as-is.
    - Otherwise (and if USE_LLM_TRANSLATION), an LLM will translate the intent to a single safe '/command'.
    Returns the raw server reply text.
    """
    # Status ticker in Cursor
    await ctx.info("Connecting to RCON …")

    # Prepare command
    cmd = request.strip()

    if USE_LLM_TRANSLATION and not cmd.startswith("/"):
        if not OPENAI_API_KEY:
            await ctx.warn("No OPENAI_API_KEY set; send a literal /command or export the key.")
        else:
            await ctx.info("Translating natural language → exact command …")
            try:
                import openai
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                prompt = f"""Translate the user's intent into ONE safe Minecraft Java server console command.
Rules:
- Output ONLY the command line, starting with '/'.
- Prefer harmless actions when ambiguous (e.g., /say).
- If a player target is needed and none is provided, use @a.
User request: {request}
"""
                resp = client.responses.create(
                    model="gpt-5-mini",
                    input=prompt
                )
                cmd = (resp.output_text or "").strip()
                if not cmd.startswith("/"):
                    return f"LLM did not return a slash command. Got: {cmd}"
            except Exception as e:
                return f"LLM translation error: {e}"

    if not cmd.startswith("/"):
        cmd = "/" + cmd

    if not RCON_PASSWORD:
        return "RCON password file missing. Re-run setup_server.py to create server/.rcon_password."

    # Send over RCON
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as rcon:
            await ctx.info(f"Sending: {cmd}")
            reply = rcon.command(cmd[1:])  # drop leading '/'
            await ctx.info("Reply received.")
            return reply or "(no reply)"
    except Exception as e:
        return f"RCON error: {e}"

if __name__ == "__main__":
    # FastMCP will run a stdio server, which Cursor expects.
    mcp.run()
