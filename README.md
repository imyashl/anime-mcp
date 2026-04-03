# 🎌 Anime MCP Server

A fully agentic **Model Context Protocol (MCP)** server that turns Claude into
a knowledgeable anime expert — searching, recommending, tracking watchlists,
fetching manga chapters, and more. **28 tools**, no API keys needed.

---

## ✨ Features

| Category | Tools |
|---|---|
| 🔍 **Search** | Anime, Manga, Characters, Studios |
| 📋 **Details** | Full profiles, Episodes, Staff, Reviews |
| 🏆 **Rankings** | Top Anime/Manga, Seasonal, Trending |
| 📚 **Manga** | Chapter lists, Reading links (MangaDex) |
| 📝 **Watchlist** | Add, view, update, remove, favorites |
| 🎯 **Recommendations** | By anime ID or preferred genres |
| 🎌 **Fun** | Random anime, quotes, upcoming, compare |

**APIs used (all free, no keys):**
- [Jikan v4](https://api.jikan.moe/v4) — MAL data, search, reviews
- [AniList GraphQL](https://graphql.anilist.co) — Trending, seasonal, genre recs
- [MangaDex](https://api.mangadex.org) — Manga chapters & reading links
- [AnimeChan](https://animechan.io) — Anime quotes

---

## 🚀 Installation

### 1. Clone / download
```bash
cd ~/Desktop   # or wherever you keep projects
# The project is already at: anime-mcp/
cd anime-mcp
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Test the server runs
```bash
python server.py
# Should hang (waiting for stdio input) — that's correct! Ctrl+C to exit.
```

---

## 🔌 Connect to Claude Desktop

### 1. Find your config file

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### 2. Add the MCP server block

Open the config and add (or merge) the `mcpServers` section:

```json
{
  "mcpServers": {
    "anime-mcp": {
      "command": "/Users/YOUR_USERNAME/Desktop/anime-mcp/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/Desktop/anime-mcp/server.py"],
      "env": {}
    }
  }
}
```

> **⚠️ Important:** Replace `/Users/YOUR_USERNAME/Desktop/anime-mcp` with the
> actual absolute path to where you placed this project.

To find the exact Python path:
```bash
cd anime-mcp && source .venv/bin/activate && which python
```

### 3. Restart Claude Desktop

Close and reopen Claude Desktop. You should see the anime tools available.

---

## 💬 Example Prompts to Try

### 🔍 Search & Discovery
- `"What are the top 10 anime of all time?"`
- `"Find me a romance anime from 2023"`
- `"Search for horror manga"`
- `"Who voices Goku in Japanese and English?"`
- `"Tell me about Studio MAPPA"`

### 📋 Deep Dives
- `"Tell me everything about One Piece"`
- `"Show me all the opening themes for Fullmetal Alchemist Brotherhood"`
- `"Who worked on Attack on Titan? Directors and composers?"`
- `"What do fans say about Neon Genesis Evangelion?"`

### 🏆 Rankings & Trending
- `"What's airing this season?"`
- `"What anime is trending right now?"`
- `"Show me the top 10 manga"`
- `"What was popular in Fall 2023?"`

### 📚 Manga Reading
- `"Show me the latest chapters of One Punch Man"`
- `"Where can I read Berserk chapter 100?"`
- `"List the chapters of Chainsaw Man"`

### 📝 Watchlist Management
- `"Add Demon Slayer to my watchlist"`
- `"I finished Death Note, mark it complete"`
- `"Show me my watchlist"`
- `"What am I currently watching?"`
- `"Add Steins;Gate to my favorites"`

### 🎯 Recommendations
- `"I loved Attack on Titan, what should I watch next?"`
- `"What manga is similar to Berserk?"`
- `"Recommend me action anime with a score above 8"`
- `"Give me romance + fantasy anime recommendations"`

### 🎌 Fun
- `"Give me a random anime recommendation"`
- `"Compare Naruto and Bleach"`
- `"What anime is coming out soon?"`
- `"Give me an anime quote"`

---

## 🧰 All 28 Tools

### Search & Discovery
| Tool | Description |
|---|---|
| `search_anime` | Search by title, genre, year, status |
| `search_manga` | Search manga by title or genre |
| `search_character` | Find any anime/manga character |
| `search_studio` | Find anime production studios |

### Detailed Info
| Tool | Description |
|---|---|
| `get_anime_details` | Full anime profile by MAL ID |
| `get_manga_details` | Full manga profile by MAL ID |
| `get_character_details` | Character + voice actors |
| `get_anime_episodes` | Episode list with filler flags |
| `get_anime_staff` | Directors, writers, composers |
| `get_anime_reviews` | User reviews from MAL |

### Rankings & Trending
| Tool | Description |
|---|---|
| `get_top_anime` | Top anime by category |
| `get_top_manga` | Top manga by category |
| `get_seasonal_anime` | Anime for a specific season |
| `get_trending_anime` | Currently trending (AniList) |

### Manga Reading
| Tool | Description |
|---|---|
| `get_manga_chapters` | Chapter list from MangaDex |
| `get_manga_reading_link` | Direct reading URL by chapter # |

### Recommendations
| Tool | Description |
|---|---|
| `get_anime_recommendations` | Similar anime by ID |
| `get_personalized_recommendations` | Genre + score based picks |

### Watchlist & Favorites
| Tool | Description |
|---|---|
| `add_to_watchlist` | Add anime with status |
| `get_watchlist` | View watchlist (filtered or all) |
| `update_watchlist_status` | Change watching status |
| `remove_from_watchlist` | Remove from watchlist |
| `add_to_favorites` | Star an anime as favorite |
| `get_favorites` | View all favorites |

### Fun & Extra
| Tool | Description |
|---|---|
| `get_random_anime` | Random pick (optional genre filter) |
| `get_anime_quotes` | Famous anime quotes |
| `get_upcoming_anime` | Anime releasing soon |
| `compare_anime` | Side-by-side comparison |

---

## 🏗️ Project Structure

```
anime-mcp/
├── server.py           # MCP server entry point (28 tools registered)
├── tools/
│   ├── search.py       # Tools 1–4:  Search & Discovery
│   ├── details.py      # Tools 5–10: Detailed Info
│   ├── rankings.py     # Tools 11–14: Rankings & Trending
│   ├── manga.py        # Tools 15–16: Manga Reading
│   ├── watchlist.py    # Tools 19–24: Personal Watchlist (JSON)
│   └── extras.py       # Tools 17–18, 25–28: Recs & Fun
├── utils/
│   ├── jikan.py        # Jikan API v4 client (rate-limited, cached)
│   ├── anilist.py      # AniList GraphQL client (cached)
│   └── mangadex.py     # MangaDex API client (cached)
├── data/
│   └── watchlist.json  # Local watchlist & favorites storage
├── requirements.txt    # mcp, httpx
└── README.md
```

---

## 🛡️ Rate Limiting & Caching

- **Jikan**: Max 3 req/sec (built-in rate limiter + retry with backoff)
- **All clients**: 3–5 min in-memory cache for repeated requests
- **Errors**: Friendly fallback messages — no raw exceptions shown to Claude

---

## 🎯 Agentic Behavior

Claude will automatically **chain tools** together for complex requests:

- `"I loved AoT, what next?"` → `search_anime` → `get_anime_recommendations` → `get_personalized_recommendations`
- `"Add Naruto to watchlist + find similar"` → `add_to_watchlist` + `get_anime_recommendations`
- `"What's good this season?"` → `get_seasonal_anime` + `get_trending_anime`
- `"Tell me about black clover"` → `search_anime` → `get_anime_details`
