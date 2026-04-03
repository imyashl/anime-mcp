"""
tools/search.py — Search & Discovery tools (Tools 1–4)
"""

from mcp.server.fastmcp import FastMCP
from utils import jikan


def register(app: FastMCP):

    @app.tool()
    async def search_anime(
        query: str,
        genre: str | None = None,
        year: int | None = None,
        status: str | None = None,
    ) -> str:
        """
        Search for anime by title, genre, release year, or airing status.
        Use this when a user asks about a specific anime or wants to find anime
        matching certain criteria like 'romance anime from 2023' or
        'currently airing shonen shows'.

        Args:
            query: Anime title or keywords to search for
            genre: Filter by genre (e.g., 'Action', 'Romance', 'Horror')
            year: Filter by release year (e.g., 2023)
            status: Filter by status — 'airing', 'complete', 'upcoming'

        Returns:
            Formatted list of matching anime with title, synopsis, rating,
            episodes, status, genres, and MyAnimeList URL.
        """
        try:
            data = await jikan.search_anime(query, genre=genre, year=year, status=status)
            results = data.get("data", [])
            if not results:
                return f"No anime found for '{query}'."

            lines = [f"🔍 **Anime search results for '{query}'**\n"]
            for i, anime in enumerate(results[:10], 1):
                attrs = anime
                title = attrs.get("title", "Unknown")
                title_en = attrs.get("title_english", "")
                score = attrs.get("score")
                episodes = attrs.get("episodes", "?")
                status_str = attrs.get("status", "Unknown")
                synopsis = (attrs.get("synopsis") or "No synopsis available.")[:200]
                genres = ", ".join(g["name"] for g in attrs.get("genres", [])[:5]) or "N/A"
                url = attrs.get("url", "")
                mal_id = attrs.get("mal_id", "")

                score_str = f"{score:.1f}/10" if score else "Not rated"
                en_str = f" / {title_en}" if title_en and title_en != title else ""

                lines.append(
                    f"{i}. **{title}{en_str}**\n"
                    f"   🆔 ID: `{mal_id}` | ⭐ {score_str} | 📺 {episodes} eps | {status_str}\n"
                    f"   🏷️ Genres: {genres}\n"
                    f"   📖 {synopsis}...\n"
                    f"   🔗 {url}\n"
                )

                # Genre filter post-processing
                if genre and not any(
                    genre.lower() in g["name"].lower()
                    for g in anime.get("genres", [])
                ):
                    lines.pop()  # remove if genre doesn't match

            if len(lines) == 1:
                return f"No anime matching genre '{genre}' found for '{query}'."

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Search failed: {e}"

    @app.tool()
    async def search_manga(
        query: str,
        genre: str | None = None,
        status: str | None = None,
    ) -> str:
        """
        Search for manga by title, genre, or publication status.
        Use when a user asks about finding manga to read.

        Args:
            query: Manga title or keywords
            genre: Optional genre filter (e.g., 'Fantasy', 'Slice of Life')
            status: Optional status filter — 'publishing', 'complete', 'discontinued'

        Returns:
            List of matching manga with title, author, volumes, chapters,
            genres, and synopsis.
        """
        try:
            data = await jikan.search_manga(query)
            results = data.get("data", [])
            if not results:
                return f"No manga found for '{query}'."

            lines = [f"📚 **Manga search results for '{query}'**\n"]
            for i, manga in enumerate(results[:10], 1):
                title = manga.get("title", "Unknown")
                score = manga.get("score")
                volumes = manga.get("volumes") or "?"
                chapters = manga.get("chapters") or "?"
                status_str = manga.get("status", "Unknown")
                synopsis = (manga.get("synopsis") or "No synopsis.")[:200]
                genres = ", ".join(g["name"] for g in manga.get("genres", [])[:5]) or "N/A"
                authors = ", ".join(
                    a["name"] for a in manga.get("authors", [])
                ) or "Unknown"
                url = manga.get("url", "")
                mal_id = manga.get("mal_id", "")

                score_str = f"{score:.1f}/10" if score else "Not rated"

                if status and status.lower() not in status_str.lower():
                    continue
                if genre and not any(
                    genre.lower() in g["name"].lower()
                    for g in manga.get("genres", [])
                ):
                    continue

                lines.append(
                    f"{i}. **{title}**\n"
                    f"   🆔 ID: `{mal_id}` | ⭐ {score_str} | 📖 {volumes} vols / {chapters} chs | {status_str}\n"
                    f"   ✏️ Author: {authors} | 🏷️ {genres}\n"
                    f"   📝 {synopsis}...\n"
                    f"   🔗 {url}\n"
                )

            return "\n".join(lines) if len(lines) > 1 else f"No manga matching your criteria found for '{query}'."

        except Exception as e:
            return f"⚠️ Manga search failed: {e}"

    @app.tool()
    async def search_character(name: str) -> str:
        """
        Search for any anime or manga character by name.
        Use when a user asks about a specific character — their backstory,
        which anime they appear in, or who voices them.

        Args:
            name: Character name to search (e.g., 'Goku', 'Levi Ackerman')

        Returns:
            Character details including anime appearances and voice actors.
        """
        try:
            data = await jikan.search_characters(name)
            results = data.get("data", [])
            if not results:
                return f"No character found named '{name}'."

            lines = [f"🎭 **Character search results for '{name}'**\n"]
            for i, char in enumerate(results[:5], 1):
                char_name = char.get("name", "Unknown")
                char_id = char.get("mal_id", "")
                nicknames = ", ".join(char.get("nicknames", [])[:3])
                about = (char.get("about") or "No description available.").replace("\n", " ")[:150]
                url = char.get("url", "")

                lines.append(
                    f"{i}. **{char_name}** (ID: `{char_id}`)\n"
                    f"   {'Nicknames: ' + nicknames + chr(10) + '   ' if nicknames else ''}"
                    f"� {about}...\n"
                    f"   🔗 {url}\n"
                )

            lines.append(
                f"\n💡 **Tip:** Use `get_character_details(character_id)` "
                f"with the ID above for full voice actor info!"
            )
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Character search failed: {e}"

    @app.tool()
    async def search_studio(name: str) -> str:
        """
        Search for anime production studios by name.
        Use when a user asks about a studio (e.g., 'Studio Ghibli', 'MAPPA',
        'Kyoto Animation') or wants to know what a studio has produced.

        Args:
            name: Studio name to search

        Returns:
            Studio info including founding year and list of anime produced.
        """
        try:
            data = await jikan.search_producers(name)
            results = data.get("data", [])
            if not results:
                return f"No studio found named '{name}'."

            lines = [f"🎬 **Studio search results for '{name}'**\n"]
            for i, studio in enumerate(results[:5], 1):
                studio_name = studio.get("titles", [{}])[0].get("title", "Unknown")
                studio_id = studio.get("mal_id", "")
                established = studio.get("established", "Unknown")
                about = (studio.get("about") or "No description.")[:200]
                count = studio.get("count", 0)
                url = studio.get("url", "")

                lines.append(
                    f"{i}. **{studio_name}** (ID: `{studio_id}`)\n"
                    f"   📅 Founded: {established} | 🎞️ {count} anime produced\n"
                    f"   📝 {about}...\n"
                    f"   🔗 {url}\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Studio search failed: {e}"
