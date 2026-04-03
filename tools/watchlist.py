"""
tools/watchlist.py — Personal Watchlist tools (Tools 19–24)
Local JSON storage in data/watchlist.json
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

WATCHLIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "watchlist.json"
)

VALID_STATUSES = {"watching", "completed", "plan_to_watch", "dropped", "on_hold"}


def _load() -> dict:
    """Load watchlist from disk. Returns {watchlist: [...], favorites: [...]}."""
    if not os.path.exists(WATCHLIST_PATH):
        return {"watchlist": [], "favorites": []}
    try:
        with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            data.setdefault("watchlist", [])
            data.setdefault("favorites", [])
            return data
    except (json.JSONDecodeError, OSError):
        return {"watchlist": [], "favorites": []}


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(WATCHLIST_PATH), exist_ok=True)
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _status_emoji(status: str) -> str:
    return {
        "watching": "▶️",
        "completed": "✅",
        "plan_to_watch": "📋",
        "dropped": "❌",
        "on_hold": "⏸️",
    }.get(status, "❓")


def register(app: FastMCP):

    @app.tool()
    async def add_to_watchlist(
        anime_title: str,
        status: str = "plan_to_watch",
    ) -> str:
        """
        Add an anime to your personal watchlist with a watching status.
        Use when a user says 'add [anime] to my watchlist' or
        'I want to watch [anime]'.

        Args:
            anime_title: Name of the anime to add
            status: Current watching status — 'watching', 'completed',
                    'plan_to_watch', 'dropped', 'on_hold'
                    (default: 'plan_to_watch')

        Returns:
            Confirmation that the anime was added.
        """
        if status not in VALID_STATUSES:
            return f"❌ Invalid status '{status}'. Choose from: {', '.join(VALID_STATUSES)}"

        data = _load()
        watchlist: list = data["watchlist"]

        # Check if already in list
        for entry in watchlist:
            if entry["title"].lower() == anime_title.lower():
                old = entry["status"]
                entry["status"] = status
                entry["updated_at"] = datetime.now().isoformat()
                _save(data)
                return (f"🔄 **{anime_title}** was already in your watchlist.\n"
                         f"Status updated: {_status_emoji(old)} {old} → "
                         f"{_status_emoji(status)} {status}")

        watchlist.append({
            "title": anime_title,
            "status": status,
            "added_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        })
        _save(data)

        emoji = _status_emoji(status)
        return (f"✅ **{anime_title}** added to your watchlist!\n"
                 f"   Status: {emoji} {status}\n"
                 f"   Total in watchlist: {len(watchlist)} anime")

    @app.tool()
    async def get_watchlist(status: str | None = None) -> str:
        """
        View your anime watchlist, optionally filtered by status.
        Use when a user asks 'show me my watchlist' or
        'what anime am I watching?'

        Args:
            status: Optional filter — 'watching', 'completed',
                    'plan_to_watch', 'dropped', 'on_hold'
                    (omit to show all)

        Returns:
            Your watchlist grouped by status with dates.
        """
        data = _load()
        watchlist: list = data["watchlist"]

        if not watchlist:
            return ("📋 Your watchlist is empty!\n"
                     "Use `add_to_watchlist(anime_title)` to start tracking anime.")

        if status:
            if status not in VALID_STATUSES:
                return f"❌ Invalid status. Choose: {', '.join(VALID_STATUSES)}"
            filtered = [e for e in watchlist if e["status"] == status]
            if not filtered:
                return f"No anime with status '{status}' in your watchlist."
            entries = filtered
        else:
            entries = watchlist

        # Group by status
        groups: dict[str, list] = {}
        for entry in entries:
            s = entry["status"]
            groups.setdefault(s, []).append(entry)

        lines = [
            f"📋 **Your Watchlist** — {len(entries)} anime"
            + (f" (filtered: {status})" if status else "") + "\n"
        ]

        status_order = ["watching", "plan_to_watch", "completed", "on_hold", "dropped"]
        for s in status_order:
            if s not in groups:
                continue
            emoji = _status_emoji(s)
            label = s.replace("_", " ").title()
            lines.append(f"\n{emoji} **{label}** ({len(groups[s])})")
            for entry in groups[s]:
                title = entry["title"]
                added = entry["added_at"][:10]
                lines.append(f"  • {title}  _(added {added})_")

        return "\n".join(lines)

    @app.tool()
    async def update_watchlist_status(
        anime_title: str,
        status: str,
    ) -> str:
        """
        Update the watching status of an anime in your watchlist.
        Use when a user says 'I finished [anime]', 'I dropped [anime]',
        or 'I started watching [anime]'.

        Args:
            anime_title: Title of the anime to update
            status: New status — 'watching', 'completed',
                    'plan_to_watch', 'dropped', 'on_hold'

        Returns:
            Confirmation of the status change.
        """
        if status not in VALID_STATUSES:
            return f"❌ Invalid status '{status}'. Choose: {', '.join(VALID_STATUSES)}"

        data = _load()
        watchlist: list = data["watchlist"]

        for entry in watchlist:
            if entry["title"].lower() == anime_title.lower():
                old_status = entry["status"]
                entry["status"] = status
                entry["updated_at"] = datetime.now().isoformat()
                _save(data)
                return (f"✅ **{entry['title']}** status updated!\n"
                         f"   {_status_emoji(old_status)} {old_status} → "
                         f"{_status_emoji(status)} {status}")

        return (f"❌ '{anime_title}' not found in your watchlist.\n"
                 f"Use `add_to_watchlist('{anime_title}')` to add it first.")

    @app.tool()
    async def remove_from_watchlist(anime_title: str) -> str:
        """
        Remove an anime from your watchlist.
        Use when a user says 'remove [anime] from my watchlist'.

        Args:
            anime_title: Title of the anime to remove

        Returns:
            Confirmation of removal.
        """
        data = _load()
        watchlist: list = data["watchlist"]
        original_count = len(watchlist)

        data["watchlist"] = [
            e for e in watchlist
            if e["title"].lower() != anime_title.lower()
        ]

        if len(data["watchlist"]) == original_count:
            return f"❌ '{anime_title}' was not found in your watchlist."

        _save(data)
        return f"🗑️ **{anime_title}** has been removed from your watchlist."

    @app.tool()
    async def add_to_favorites(anime_title: str) -> str:
        """
        Add an anime to your personal favorites list.
        Use when a user says 'add [anime] to my favorites'
        or 'I love [anime]'.

        Args:
            anime_title: Name of the anime to favorite

        Returns:
            Confirmation that it was added to favorites.
        """
        data = _load()
        favorites: list = data.get("favorites", [])

        if any(f["title"].lower() == anime_title.lower() for f in favorites):
            return f"💛 **{anime_title}** is already in your favorites!"

        favorites.append({
            "title": anime_title,
            "added_at": datetime.now().isoformat(),
        })
        data["favorites"] = favorites
        _save(data)

        return (f"⭐ **{anime_title}** added to your favorites!\n"
                 f"   Total favorites: {len(favorites)} anime")

    @app.tool()
    async def get_favorites() -> str:
        """
        View your anime favorites list.
        Use when a user asks 'what are my favorite anime?'
        or 'show me my favorites'.

        Returns:
            All favorited anime with dates added.
        """
        data = _load()
        favorites: list = data.get("favorites", [])

        if not favorites:
            return ("⭐ Your favorites list is empty!\n"
                     "Use `add_to_favorites(anime_title)` to save anime you love.")

        lines = [f"⭐ **Your Favorites** — {len(favorites)} anime\n"]
        for i, entry in enumerate(favorites, 1):
            title = entry["title"]
            added = entry["added_at"][:10]
            lines.append(f"  {i}. **{title}**  _(added {added})_")

        return "\n".join(lines)
