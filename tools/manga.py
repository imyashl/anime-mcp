"""
tools/manga.py — Manga Reading tools (Tools 15–16)
"""

from mcp.server.fastmcp import FastMCP
from utils import mangadex


def register(app: FastMCP):

    @app.tool()
    async def get_manga_chapters(
        manga_title: str,
        limit: int = 20,
    ) -> str:
        """
        Fetch the chapter list for a manga from MangaDex.
        Use when a user wants to browse chapters of a manga or find
        out how many chapters are available to read online.

        Args:
            manga_title: Manga title to search for
            limit: Number of chapters to show (default 20)

        Returns:
            Chapter list with numbers, titles, upload dates,
            and direct reading links.
        """
        try:
            mangas = await mangadex.search_manga(manga_title, limit=3)
            if not mangas:
                return f"Manga '{manga_title}' not found on MangaDex."

            manga = mangas[0]
            manga_id = manga["id"]
            found_title = manga["title"]
            tags = ", ".join(manga.get("tags", [])[:5]) or "N/A"

            chapters = await mangadex.get_manga_chapters(manga_id, limit=min(limit, 100))

            if not chapters:
                return f"No English chapters found for '{found_title}' on MangaDex."

            lines = [
                f"📖 **{found_title}** — MangaDex Chapters\n"
                f"🏷️ Tags: {tags} | 📡 Status: {manga.get('status', 'unknown')}\n"
                f"Showing {len(chapters)} chapters\n"
            ]

            for ch in chapters[:limit]:
                ch_num = ch.get("chapter", "?")
                title = ch.get("title", f"Chapter {ch_num}")
                pages = ch.get("pages", "?")
                pub_date = (ch.get("publishAt") or "")[:10]
                read_url = ch.get("reading_url", "")

                lines.append(
                    f"  **Ch.{ch_num}** — {title}\n"
                    f"    📄 {pages} pages | 📅 {pub_date} | 🔗 {read_url}"
                )

            lines.append(
                f"\n💡 Use `get_manga_reading_link('{manga_title}', chapter_number)` "
                f"to get a direct link to any chapter!"
            )
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch chapters: {e}"

    @app.tool()
    async def get_manga_reading_link(
        manga_title: str,
        chapter: int | float,
    ) -> str:
        """
        Get a direct reading link for a specific chapter of a manga on MangaDex.
        Use when a user says 'I want to read chapter X of [manga]' or
        'where can I read One Piece chapter 1000?'

        Args:
            manga_title: Name of the manga
            chapter: Chapter number (can be decimal like 10.5)

        Returns:
            Direct MangaDex reader URL for that chapter.
        """
        try:
            result = await mangadex.get_chapter_reading_link(manga_title, chapter)

            if "error" in result:
                return f"❌ {result['error']}"

            manga = result["manga"]
            ch_num = result["chapter"]
            url = result["reading_url"]
            pages = result["pages"]

            text = (
                f"📖 **{manga}** — Chapter {ch_num}\n\n"
                f"📄 {pages} pages\n"
                f"🔗 **Read now:** {url}\n\n"
                f"_(Opens in MangaDex reader — works in browser)_"
            )
            return text

        except Exception as e:
            return f"⚠️ Could not get reading link: {e}"
