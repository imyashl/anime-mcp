"""
tools/details.py — Detailed Info tools (Tools 5–10)
"""

from mcp.server.fastmcp import FastMCP
from utils import jikan


def register(app: FastMCP):

    @app.tool()
    async def get_anime_details(anime_id: int) -> str:
        """
        Get full details for a specific anime by its MyAnimeList ID.
        Use after search_anime() to get in-depth info — synopsis, genres,
        studios, trailer, opening/ending themes, aired dates, and ratings.

        Args:
            anime_id: The MAL ID of the anime (get this from search_anime)

        Returns:
            Complete anime profile with all available metadata.
        """
        try:
            data = await jikan.get_anime_by_id(anime_id)
            a = data.get("data", {})
            if not a:
                return f"Anime ID {anime_id} not found."

            title = a.get("title", "Unknown")
            title_en = a.get("title_english", "")
            title_jp = a.get("title_japanese", "")
            score = a.get("score")
            rank = a.get("rank", "N/A")
            popularity = a.get("popularity", "N/A")
            episodes = a.get("episodes", "?")
            status = a.get("status", "Unknown")
            aired = a.get("aired", {}).get("string", "Unknown")
            duration = a.get("duration", "Unknown")
            rating = a.get("rating", "Unknown")
            source = a.get("source", "Unknown")
            synopsis = a.get("synopsis") or "No synopsis available."
            genres = ", ".join(g["name"] for g in a.get("genres", [])) or "N/A"
            themes = ", ".join(g["name"] for g in a.get("themes", [])) or ""
            studios = ", ".join(s["name"] for s in a.get("studios", [])) or "N/A"
            producers = ", ".join(p["name"] for p in a.get("producers", [])[:3]) or "N/A"
            trailer = a.get("trailer", {}).get("url", "")
            url = a.get("url", "")

            # Opening & ending themes
            ops = a.get("theme", {}).get("openings", [])
            eds = a.get("theme", {}).get("endings", [])
            op_str = "\n   ".join(ops[:3]) if ops else "N/A"
            ed_str = "\n   ".join(eds[:3]) if eds else "N/A"

            score_str = f"{score:.2f}/10" if score else "Not yet rated"
            title_line = title
            if title_en and title_en != title:
                title_line += f" / {title_en}"
            if title_jp:
                title_line += f"\n   🇯🇵 {title_jp}"

            text = f"""🎌 **{title_line}**

⭐ **Score:** {score_str}  |  🏆 Rank #{rank}  |  📈 Popularity #{popularity}
📺 **Episodes:** {episodes}  |  ⏱️ Duration: {duration}
📅 **Aired:** {aired}  |  📡 Status: {status}
🎭 **Source:** {source}  |  🔞 Rating: {rating}

🏷️ **Genres:** {genres}
{('🎨 **Themes:** ' + themes + chr(10)) if themes else ''}🎬 **Studios:** {studios}
🏭 **Producers:** {producers}

📖 **Synopsis:**
{synopsis}

🎵 **Opening Theme(s):**
   {op_str}
🎶 **Ending Theme(s):**
   {ed_str}

{('🎬 **Trailer:** ' + trailer + chr(10)) if trailer else ''}🔗 **MAL:** {url}

💡 Use `get_anime_episodes({anime_id})` for episode list or `get_anime_recommendations({anime_id})` for similar shows!"""

            return text

        except Exception as e:
            return f"⚠️ Could not fetch anime details: {e}"

    @app.tool()
    async def get_manga_details(manga_id: int) -> str:
        """
        Get full details for a specific manga by its MyAnimeList ID.

        Args:
            manga_id: The MAL ID of the manga (get from search_manga)

        Returns:
            Full manga profile: title, author, volumes, chapters,
            synopsis, serialization, genres, and score.
        """
        try:
            data = await jikan.get_manga_by_id(manga_id)
            m = data.get("data", {})
            if not m:
                return f"Manga ID {manga_id} not found."

            title = m.get("title", "Unknown")
            title_en = m.get("title_english", "")
            score = m.get("score")
            rank = m.get("rank", "N/A")
            volumes = m.get("volumes") or "Ongoing"
            chapters = m.get("chapters") or "Ongoing"
            status = m.get("status", "Unknown")
            published = m.get("published", {}).get("string", "Unknown")
            synopsis = m.get("synopsis") or "No synopsis."
            genres = ", ".join(g["name"] for g in m.get("genres", [])) or "N/A"
            themes = ", ".join(g["name"] for g in m.get("themes", [])) or ""
            authors = ", ".join(a["name"] for a in m.get("authors", [])) or "Unknown"
            serializations = ", ".join(s["name"] for s in m.get("serializations", [])) or "N/A"
            url = m.get("url", "")

            score_str = f"{score:.2f}/10" if score else "Not rated"
            title_line = title + (f" / {title_en}" if title_en and title_en != title else "")

            text = f"""📚 **{title_line}**

⭐ **Score:** {score_str}  |  🏆 Rank #{rank}
📖 **Volumes:** {volumes}  |  📑 Chapters: {chapters}
📅 **Published:** {published}  |  📡 Status: {status}
✏️ **Author(s):** {authors}
📰 **Serialized in:** {serializations}

🏷️ **Genres:** {genres}
{('🎨 **Themes:** ' + themes) if themes else ''}

📝 **Synopsis:**
{synopsis}

🔗 **MAL:** {url}"""

            return text

        except Exception as e:
            return f"⚠️ Could not fetch manga details: {e}"

    @app.tool()
    async def get_character_details(character_id: int) -> str:
        """
        Get a detailed profile for a specific anime/manga character.
        Use this when a user wants to know more about a character —
        their backstory, which anime they appear in, their voice actors
        in Japanese and English.

        Args:
            character_id: The MAL character ID (get from search_character)

        Returns:
            Full character profile including description, anime appearances,
            and voice actor info for JP and EN.
        """
        try:
            data = await jikan.get_character_by_id(character_id)
            c = data.get("data", {})
            if not c:
                return f"Character ID {character_id} not found."

            name = c.get("name", "Unknown")
            name_kanji = c.get("name_kanji", "")
            nicknames = ", ".join(c.get("nicknames", [])) or "None"
            about = (c.get("about") or "No description available.")[:600]
            url = c.get("url", "")

            # Anime appearances
            animes = c.get("anime", [])[:5]
            anime_lines = []
            for a in animes:
                role = a.get("role", "")
                atitle = a.get("anime", {}).get("title", "Unknown")
                anime_lines.append(f"   • {atitle} ({role})")

            # Manga appearances
            mangas = c.get("manga", [])[:3]
            manga_lines = [f"   • {m.get('manga',{}).get('title','?')} ({m.get('role','')})"
                           for m in mangas]

            # Voice actors
            voices = c.get("voices", [])
            va_lines = []
            for va in voices:
                lang = va.get("language", "")
                person = va.get("person", {}).get("name", "Unknown")
                va_lines.append(f"   🎙️ {lang}: **{person}**")

            text = f"""🎭 **{name}**{(' / ' + name_kanji) if name_kanji else ''}
{'🏷️ Nicknames: ' + nicknames + chr(10) if nicknames != 'None' else ''}
📄 **About:**
{about}

📺 **Anime Appearances:**
{chr(10).join(anime_lines) if anime_lines else '   None'}
{('📚 **Manga Appearances:**' + chr(10) + chr(10).join(manga_lines) + chr(10)) if manga_lines else ''}
🎤 **Voice Actors:**
{chr(10).join(va_lines) if va_lines else '   Not available'}

🔗 {url}"""

            return text

        except Exception as e:
            return f"⚠️ Could not fetch character details: {e}"

    @app.tool()
    async def get_anime_episodes(anime_id: int, page: int = 1) -> str:
        """
        Get the episode list for an anime.
        Use when a user wants to browse episodes, check if an episode is
        a filler, or find out when a specific episode aired.

        Args:
            anime_id: MAL anime ID
            page: Page number (each page has up to 100 episodes)

        Returns:
            Episode list with numbers, titles, air dates, and filler flags.
        """
        try:
            data = await jikan.get_anime_episodes(anime_id, page)
            episodes = data.get("data", [])
            if not episodes:
                return f"No episode data found for anime ID {anime_id}."

            pagination = data.get("pagination", {})
            total_pages = pagination.get("last_visible_page", 1)
            has_next = pagination.get("has_next_page", False)

            lines = [f"📺 **Episodes for anime `{anime_id}` — Page {page}/{total_pages}**\n"]
            for ep in episodes:
                num = ep.get("mal_id", "?")
                title = ep.get("title") or f"Episode {num}"
                title_jp = ep.get("title_japanese", "")
                aired = ep.get("aired", "Unknown")
                filler = ep.get("filler", False)
                recap = ep.get("recap", False)
                score = ep.get("score")

                tags = []
                if filler:
                    tags.append("🟡 FILLER")
                if recap:
                    tags.append("🔄 RECAP")
                tag_str = " " + " ".join(tags) if tags else ""

                score_str = f" ⭐{score:.1f}" if score else ""
                jp_str = f" / {title_jp}" if title_jp else ""
                aired_short = aired[:10] if aired else "?"

                lines.append(
                    f"  **Ep {num}**{tag_str}{score_str}: {title}{jp_str}  📅 {aired_short}"
                )

            if has_next:
                lines.append(f"\n📄 More episodes: use `get_anime_episodes({anime_id}, {page+1})`")

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch episodes: {e}"

    @app.tool()
    async def get_anime_staff(anime_id: int) -> str:
        """
        Get the staff list for an anime — directors, writers, composers, etc.
        Use when a user asks who directed or composed music for an anime.

        Args:
            anime_id: MAL anime ID

        Returns:
            List of staff members with their roles and notable works.
        """
        try:
            data = await jikan.get_anime_staff(anime_id)
            staff_list = data.get("data", [])
            if not staff_list:
                return f"No staff data found for anime ID {anime_id}."

            lines = [f"👥 **Staff for anime `{anime_id}`**\n"]
            for staff in staff_list[:20]:
                person = staff.get("person", {})
                name = person.get("name", "Unknown")
                positions = ", ".join(staff.get("positions", [])) or "Unknown role"
                url = person.get("url", "")
                lines.append(f"  🎬 **{name}** — {positions}  🔗 {url}")

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch staff: {e}"

    @app.tool()
    async def get_anime_reviews(anime_id: int, limit: int = 5) -> str:
        """
        Fetch user reviews for an anime from MyAnimeList.
        Use when a user wants to know what others think about a show.

        Args:
            anime_id: MAL anime ID
            limit: Number of reviews to return (max 20)

        Returns:
            List of user reviews with scores, review text, and helpful counts.
        """
        try:
            data = await jikan.get_anime_reviews(anime_id)
            reviews = data.get("data", [])[:min(limit, 20)]
            if not reviews:
                return f"No reviews found for anime ID {anime_id}."

            lines = [f"💬 **User Reviews for anime `{anime_id}`**\n"]
            for i, rev in enumerate(reviews, 1):
                reviewer = rev.get("user", {}).get("username", "Anonymous")
                score = rev.get("score", "?")
                helpful = rev.get("reactions", {}).get("helpful", 0)
                review_text = (rev.get("review") or "")[:400]
                date = (rev.get("date") or "")[:10]
                tags = ", ".join(rev.get("tags", [])) or ""

                lines.append(
                    f"{'─'*50}\n"
                    f"**{i}. {reviewer}** — ⭐ {score}/10  👍 {helpful} helpful  📅 {date}\n"
                    f"{'🏷️ ' + tags + chr(10) if tags else ''}"
                    f"{review_text}{'...' if len(rev.get('review',''))>400 else ''}\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch reviews: {e}"
