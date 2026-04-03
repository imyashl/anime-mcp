"""
tools/art.py — Anime & Character Art tools (Tools 29-30)
"""

from mcp.server.fastmcp import FastMCP
from utils import jikan

def register(app: FastMCP):

    @app.tool()
    async def get_anime_pictures(anime_id: int) -> str:
        """
        Fetch high-quality promotional art, posters, and pictures for an anime.
        Use this when a user asks for pictures, wallpapers, or art of an anime.

        Args:
            anime_id: The MyAnimeList ID of the anime

        Returns:
            A string containing markdown image links to the art.
        """
        try:
            data = await jikan.jikan_get(f"/anime/{anime_id}/pictures")
            results = data.get("data", [])
            if not results:
                return f"No pictures found for anime ID {anime_id}."

            lines = [f"🖼️ **Pictures & Art for Anime `{anime_id}`**\n"]
            for i, pic in enumerate(results[:10], 1):
                img_url = pic.get("jpg", {}).get("large_image_url") or pic.get("jpg", {}).get("image_url", "")
                if img_url:
                    lines.append(f"{i}. [Link]({img_url})")

            return "\n".join(lines)
        except Exception as e:
            return f"⚠️ Failed to fetch anime pictures: {e}"

    @app.tool()
    async def get_character_pictures(character_id: int) -> str:
        """
        Fetch high-quality art and pictures for a specific anime character.
        Use this when a user asks for pictures or avatars of a character.

        Args:
            character_id: The MyAnimeList ID of the character

        Returns:
            A string containing markdown image links to the art.
        """
        try:
            data = await jikan.jikan_get(f"/characters/{character_id}/pictures")
            results = data.get("data", [])
            if not results:
                return f"No pictures found for character ID {character_id}."

            lines = [f"🖼️ **Pictures & Art for Character `{character_id}`**\n"]
            for i, pic in enumerate(results[:10], 1):
                img_url = pic.get("jpg", {}).get("image_url", "")
                if img_url:
                    lines.append(f"{i}. [Link]({img_url})")

            return "\n".join(lines)
        except Exception as e:
            return f"⚠️ Failed to fetch character pictures: {e}"
