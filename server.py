#!/usr/bin/env python3
"""
🎌 Anime MCP Server
A fully agentic Model Context Protocol server for everything anime-related.
Supports Claude Desktop via stdio transport.

Tools: 28 tools across search, details, rankings, manga, watchlist, and extras.
APIs:  Jikan v4  |  AniList GraphQL  |  MangaDex  |  AnimeChan
"""

import sys
import os

# ── Path setup so tools/ and utils/ are importable ───────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP

# ── Tool modules ──────────────────────────────────────────────────────────────
from tools import search, details, rankings, manga, watchlist, extras

# ── Server init ───────────────────────────────────────────────────────────────
app = FastMCP("anime-mcp")

# ── Register all tool groups ──────────────────────────────────────────────────
search.register(app)    # Tools 1–4:  Search & Discovery
details.register(app)   # Tools 5–10: Detailed Info
rankings.register(app)  # Tools 11–14: Rankings & Trending
manga.register(app)     # Tools 15–16: Manga Reading
watchlist.register(app) # Tools 19–24: Personal Watchlist
extras.register(app)    # Tools 17–18, 25–28: Recommendations & Fun

# ── Resources ─────────────────────────────────────────────────────────────────
@app.resource("resource://watchlist")
def get_raw_watchlist() -> str:
    """Get the raw JSON backbone of your local anime watchlist."""
    try:
        path = os.path.join(os.path.dirname(__file__), "data", "watchlist.json")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "{}"

# ── Prompts ───────────────────────────────────────────────────────────────────
@app.prompt()
def discover_anime(genre: str = "Action", year: int = 2024) -> str:
    """A prompt to trigger Claude to act as an Anime Discovery Agent."""
    return f"""You are my personal Elite Anime Advisor! I'm looking for {genre} anime around the year {year}.
Please natively use your tools to:
1. Search AniList for trending {genre} anime from {year}.
2. Get the specific details of the top 3 recommendations.
3. Present them to me in a beautiful way and ask if I want to add them to my watchlist!"""

@app.prompt()
def plan_my_weekend() -> str:
    """Suggests an anime marathon for the weekend based on your watchlist."""
    return """Let's take a look at my current watchlist.
Please use your tools to load my watchlist and see what I have marked as 'plan_to_watch'.
Pick the best one, retrieve its synopsis, and tell me why I should binge it this weekend!"""


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run()
