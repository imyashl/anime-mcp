"""
utils/__init__.py — shared helpers across tool modules.
"""

from .jikan import jikan_get
from .anilist import anilist_query
from .mangadex import search_manga as md_search_manga

__all__ = ["jikan_get", "anilist_query", "md_search_manga"]


def fmt_list(items: list, key: str | None = None, sep: str = ", ") -> str:
    """Format a list of strings or dicts to a readable string."""
    if not items:
        return "N/A"
    if key:
        return sep.join(str(i.get(key, "")) for i in items if i.get(key))
    return sep.join(str(i) for i in items)


def safe_str(value, fallback: str = "N/A") -> str:
    return str(value) if value is not None else fallback


def score_bar(score: float | None, out_of: float = 10.0) -> str:
    """Return a simple visual score bar."""
    if score is None:
        return "No score yet"
    filled = int((score / out_of) * 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"{bar} {score:.1f}/{out_of:.0f}"
