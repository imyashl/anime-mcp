"""
tools/extras.py — Recommendations, Fun & Extra tools (Tools 17–18, 25–28)
"""

import httpx
from mcp.server.fastmcp import FastMCP
from utils import jikan, anilist


def register(app: FastMCP):

    @app.tool()
    async def get_anime_recommendations(anime_id: int) -> str:
        """
        Get anime recommendations similar to a given anime.
        Always call this after the user expresses interest in finding
        similar shows to one they've watched or enjoyed.

        Args:
            anime_id: MAL ID of the anime to base recommendations on

        Returns:
            List of recommended anime with titles and vote counts.
        """
        try:
            data = await jikan.get_anime_recommendations(anime_id)
            recs = data.get("data", [])[:10]
            if not recs:
                return f"No recommendations found for anime ID {anime_id}."

            lines = [f"💡 **Recommendations based on anime `{anime_id}`**\n"]
            for i, rec in enumerate(recs, 1):
                entry = rec.get("entry", {})
                title = entry.get("title", "Unknown")
                votes = rec.get("votes", 0)
                url = entry.get("url", "")
                mal_id = entry.get("mal_id", "")
                lines.append(
                    f"{i}. **{title}** — 👍 {votes} votes\n"
                    f"   🆔 `{mal_id}` | 🔗 {url}\n"
                )

            lines.append(
                "\n💡 Use `get_anime_details(id)` on any of these for full info!"
            )
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch recommendations: {e}"

    @app.tool()
    async def get_personalized_recommendations(
        genres: list[str],
        min_score: float = 7.0,
    ) -> str:
        """
        Get personalized anime recommendations based on preferred genres and
        minimum score. Use when a user tells you what genres they like or
        asks for recommendations matching their taste.

        Args:
            genres: List of preferred genres (e.g., ['Action', 'Fantasy', 'Romance'])
                    Valid AniList genres include: Action, Adventure, Comedy, Drama,
                    Fantasy, Horror, Mecha, Mystery, Psychological, Romance,
                    Sci-Fi, Slice of Life, Sports, Supernatural, Thriller
            min_score: Minimum average score (0–10 scale, default 7.0)

        Returns:
            Curated list of anime matching the genres with synopsis and scores.
        """
        try:
            if not genres:
                return "Please provide at least one genre."

            results = await anilist.get_recommendations_by_genre(genres, min_score)
            if not results:
                return f"No anime found for genres {genres} with score ≥ {min_score}."

            genre_str = " + ".join(genres)
            lines = [
                f"🎯 **Personalized Recommendations** — {genre_str} | Min score: {min_score}\n"
            ]

            for i, anime in enumerate(results, 1):
                title_obj = anime.get("title", {})
                title = title_obj.get("english") or title_obj.get("romaji", "Unknown")
                score = anime.get("averageScore")
                episodes = anime.get("episodes", "?")
                genres_list = ", ".join(anime.get("genres", [])[:5]) or "N/A"
                desc = (anime.get("description") or "No description.")[:200]
                url = anime.get("siteUrl", "")

                score_str = f"⭐ {score/10:.1f}/10" if score else "⭐ N/A"
                lines.append(
                    f"{i}. **{title}**\n"
                    f"   {score_str} | 📺 {episodes} eps\n"
                    f"   🏷️ {genres_list}\n"
                    f"   📖 {desc}...\n"
                    f"   🔗 {url}\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch personalized recommendations: {e}"

    @app.tool()
    async def get_random_anime(genre: str | None = None) -> str:
        """
        Get a random anime recommendation — great for when a user can't decide
        what to watch or wants a surprise. Optionally filter by genre.

        Args:
            genre: Optional genre to filter (e.g., 'Romance', 'Action')

        Returns:
            A random anime with full details as a surprise recommendation.
        """
        try:
            if genre:
                # Use AniList for genre-filtered random
                results = await anilist.get_recommendations_by_genre([genre], min_score=6.0,
                                                                       limit=20)
                if not results:
                    return f"No random anime found for genre '{genre}'."
                import random
                anime = random.choice(results)
                title_obj = anime.get("title", {})
                title = title_obj.get("english") or title_obj.get("romaji", "Unknown")
                score = anime.get("averageScore")
                episodes = anime.get("episodes", "?")
                genres = ", ".join(anime.get("genres", [])[:5]) or "N/A"
                desc = (anime.get("description") or "No description.")[:400]
                url = anime.get("siteUrl", "")
                score_str = f"⭐ {score/10:.1f}/10" if score else "⭐ N/A"

                text = (
                    f"🎲 **Random Anime Pick** _(genre: {genre})_\n\n"
                    f"**{title}**\n"
                    f"{score_str} | 📺 {episodes} eps\n"
                    f"🏷️ {genres}\n\n"
                    f"📖 {desc}...\n\n"
                    f"🔗 {url}"
                )
            else:
                data = await jikan.get_random_anime()
                anime = data.get("data", {})
                if not anime:
                    return "Could not fetch a random anime."

                title = anime.get("title", "Unknown")
                score = anime.get("score")
                episodes = anime.get("episodes", "?")
                status = anime.get("status", "")
                genres = ", ".join(g["name"] for g in anime.get("genres", [])[:5]) or "N/A"
                synopsis = (anime.get("synopsis") or "No synopsis.")[:400]
                url = anime.get("url", "")
                mal_id = anime.get("mal_id", "")
                score_str = f"⭐ {score:.1f}/10" if score else "⭐ Not rated"

                text = (
                    f"🎲 **Random Anime Pick!**\n\n"
                    f"**{title}** (ID: `{mal_id}`)\n"
                    f"{score_str} | 📺 {episodes} eps | {status}\n"
                    f"🏷️ {genres}\n\n"
                    f"📖 {synopsis}...\n\n"
                    f"🔗 {url}\n\n"
                    f"Use `get_anime_details({mal_id})` for full info!"
                )

            return text

        except Exception as e:
            return f"⚠️ Could not get random anime: {e}"

    @app.tool()
    async def get_anime_quotes() -> str:
        """
        Fetch a random famous anime quote.
        Use when a user asks for anime quotes, wants inspiration,
        or just to add some flair to the conversation.

        Returns:
            A random iconic anime quote with character and anime name.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://animechan.io/api/v1/quotes/random")
                resp.raise_for_status()
                data = resp.json()

            # animechan.io response structure
            quote_data = data.get("data", data)
            quote = quote_data.get("content") or quote_data.get("quote", "...")
            character = (quote_data.get("character") or {})
            char_name = character.get("name", "Unknown") if isinstance(character, dict) else str(character)
            anime = (quote_data.get("anime") or {})
            anime_name = anime.get("name", "Unknown") if isinstance(anime, dict) else str(anime)

            text = (
                f"💬 **Anime Quote**\n\n"
                f"_{quote}_\n\n"
                f"— **{char_name}**, *{anime_name}*"
            )
            return text

        except Exception as e:
            # Fallback quotes if API is down
            fallback = [
                ("People's dreams never end!", "Whitebeard", "One Piece"),
                ("I am the hope of the universe!", "Goku", "Dragon Ball Z"),
                ("Believe it!", "Naruto Uzumaki", "Naruto"),
                ("Even if you can't see or touch something, it can still exist.", "Korosensei", "Assassination Classroom"),
                ("Whatever you lose, you'll find it again. But what you throw away you'll never get back.", "Kenshin Himura", "Rurouni Kenshin"),
            ]
            import random
            q, char, anime = random.choice(fallback)
            return f"💬 **Anime Quote**\n\n_{q}_\n\n— **{char}**, *{anime}*\n\n_(Quote API unavailable, showing classic quote)_"

    @app.tool()
    async def get_upcoming_anime() -> str:
        """
        Get anime that are upcoming / releasing soon.
        Use when a user asks 'what anime is coming out soon?' or
        'what should I look forward to?'

        Returns:
            List of upcoming anime with expected season and studio info.
        """
        try:
            data = await jikan.get_upcoming_season()
            results = data.get("data", [])[:15]
            if not results:
                return "Could not fetch upcoming anime."

            lines = ["🗓️ **Upcoming Anime**\n"]
            for i, anime in enumerate(results, 1):
                title = anime.get("title", "Unknown")
                aired = anime.get("aired", {}).get("string", "TBA")
                studios = ", ".join(s["name"] for s in anime.get("studios", [])[:2]) or "TBA"
                genres = ", ".join(g["name"] for g in anime.get("genres", [])[:3]) or "N/A"
                source = anime.get("source", "")
                mal_id = anime.get("mal_id", "")

                lines.append(
                    f"{i}. **{title}**\n"
                    f"   📅 {aired} | 🎬 {studios}\n"
                    f"   🏷️ {genres}"
                    + (f" | 📚 Based on: {source}" if source else "")
                    + f"\n   🆔 `{mal_id}`\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch upcoming anime: {e}"

    @app.tool()
    async def compare_anime(
        anime_id_1: int,
        anime_id_2: int,
    ) -> str:
        """
        Compare two anime side by side across key metrics.
        Use when a user asks 'which is better, X or Y?' or
        'compare Naruto and Bleach'.

        Args:
            anime_id_1: MAL ID of the first anime
            anime_id_2: MAL ID of the second anime

        Returns:
            Side-by-side comparison table of ratings, episodes,
            genres, studios, and more.
        """
        try:
            import asyncio
            d1, d2 = await asyncio.gather(
                jikan.get_anime_by_id(anime_id_1),
                jikan.get_anime_by_id(anime_id_2),
            )
            a1 = d1.get("data", {})
            a2 = d2.get("data", {})

            if not a1:
                return f"Anime ID {anime_id_1} not found."
            if not a2:
                return f"Anime ID {anime_id_2} not found."

            def _g(a: dict, key: str, fallback="N/A"):
                v = a.get(key)
                return str(v) if v is not None else fallback

            t1 = a1.get("title", "Anime 1")
            t2 = a2.get("title", "Anime 2")

            score1 = a1.get("score")
            score2 = a2.get("score")
            s1_str = f"{score1:.2f}/10" if score1 else "N/A"
            s2_str = f"{score2:.2f}/10" if score2 else "N/A"

            # Determine winner per metric
            def cmp(v1, v2, higher_is_better=True):
                if v1 is None or v2 is None:
                    return "➖", "➖"
                if v1 > v2:
                    return ("🏆", "  ") if higher_is_better else ("  ", "🏆")
                elif v2 > v1:
                    return ("  ", "🏆") if higher_is_better else ("🏆", "  ")
                return "🤝", "🤝"

            sc = cmp(score1, score2)
            rank1, rank2 = a1.get("rank"), a2.get("rank")
            rk = cmp(rank1, rank2, higher_is_better=False)  # lower rank number = better
            pop1, pop2 = a1.get("popularity"), a2.get("popularity")
            pk = cmp(pop1, pop2, higher_is_better=False)
            fav1, fav2 = a1.get("favorites"), a2.get("favorites")
            fk = cmp(fav1, fav2)

            genres1 = ", ".join(g["name"] for g in a1.get("genres", [])[:4]) or "N/A"
            genres2 = ", ".join(g["name"] for g in a2.get("genres", [])[:4]) or "N/A"
            studios1 = ", ".join(s["name"] for s in a1.get("studios", [])[:2]) or "N/A"
            studios2 = ", ".join(s["name"] for s in a2.get("studios", [])[:2]) or "N/A"

            col_w = 24
            def row(label: str, v1: str, v2: str, w1="", w2=""):
                lv1 = f"{w1} {v1}".strip()
                lv2 = f"{w2} {v2}".strip()
                return f"{'│'} {label:<18} {'│'} {lv1:<{col_w}} {'│'} {lv2:<{col_w}} {'│'}"

            divider = f"+{'─'*20}+{'─'*(col_w+2)}+{'─'*(col_w+2)}+"
            header  = f"│ {'Metric':<18} │ {t1[:col_w]:<{col_w}} │ {t2[:col_w]:<{col_w}} │"

            lines = [
                f"\n⚔️  **Anime Comparison**\n",
                divider, header, divider,
                row("⭐ Score",    s1_str,           s2_str,           sc[0], sc[1]),
                row("🏆 Rank",    f"#{_g(a1,'rank')}",  f"#{_g(a2,'rank')}",  rk[0], rk[1]),
                row("📈 Popularity", f"#{_g(a1,'popularity')}", f"#{_g(a2,'popularity')}", pk[0], pk[1]),
                row("❤️ Favorites", f"{fav1:,}" if fav1 else "N/A", f"{fav2:,}" if fav2 else "N/A", fk[0], fk[1]),
                row("📺 Episodes",  _g(a1,"episodes"),  _g(a2,"episodes")),
                row("📡 Status",    _g(a1,"status"),    _g(a2,"status")),
                row("📅 Aired",     (a1.get("aired",{}).get("string","N/A") or "N/A")[:col_w],
                                    (a2.get("aired",{}).get("string","N/A") or "N/A")[:col_w]),
                row("🎭 Source",    _g(a1,"source"),    _g(a2,"source")),
                row("🎬 Studios",   studios1[:col_w],   studios2[:col_w]),
                row("🏷️ Genres",   genres1[:col_w],    genres2[:col_w]),
                divider,
                f"\n🔗 {t1}: {a1.get('url','')}",
                f"🔗 {t2}: {a2.get('url','')}",
            ]

            return "\n".join(str(l) for l in lines)

        except Exception as e:
            return f"⚠️ Could not compare anime: {e}"
