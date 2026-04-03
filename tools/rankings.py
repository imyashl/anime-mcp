"""
tools/rankings.py — Rankings & Trending tools (Tools 11–14)
"""

import datetime
from mcp.server.fastmcp import FastMCP
from utils import jikan, anilist


# Season detection helper
def _current_season() -> tuple[str, int]:
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if month in (1, 2, 3):
        return "winter", year
    elif month in (4, 5, 6):
        return "spring", year
    elif month in (7, 8, 9):
        return "summer", year
    else:
        return "fall", year


def register(app: FastMCP):

    @app.tool()
    async def get_top_anime(
        category: str = "all",
        limit: int = 10,
    ) -> str:
        """
        Get the top-ranked anime from MyAnimeList.
        Use when a user asks 'what are the best anime?' or wants ranked lists.

        Args:
            category: Ranking category — 'all', 'airing', 'upcoming',
                      'movie', 'ova', 'special', 'bypopularity', 'favorite'
            limit: Number of results (1–25)

        Returns:
            Ranked list with scores, episode counts, and status.
        """
        try:
            # Map user-friendly category names to Jikan filter params
            cat_map = {
                "all": "bypopularity",
                "airing": "airing",
                "upcoming": "upcoming",
                "movie": "bypopularity",
                "ova": "bypopularity",
                "favorite": "favorite",
                "bypopularity": "bypopularity",
            }
            filter_type = cat_map.get(category.lower(), "bypopularity")

            data = await jikan.get_top_anime(filter_type)
            anime_list = data.get("data", [])[:min(limit, 25)]

            if not anime_list:
                return "Could not retrieve top anime."

            cat_label = {
                "airing": "Currently Airing",
                "upcoming": "Upcoming",
                "bypopularity": "All Time by Popularity",
                "favorite": "Most Favorited",
            }.get(filter_type, "All Time")

            lines = [f"🏆 **Top {limit} Anime — {cat_label}**\n"]
            medals = ["🥇", "🥈", "🥉"]

            for i, anime in enumerate(anime_list, 1):
                medal = medals[i - 1] if i <= 3 else f"**#{i}**"
                title = anime.get("title", "Unknown")
                score = anime.get("score")
                episodes = anime.get("episodes", "?")
                status = anime.get("status", "")
                genres = ", ".join(g["name"] for g in anime.get("genres", [])[:3]) or "N/A"
                mal_id = anime.get("mal_id", "")

                score_str = f"⭐ {score:.2f}" if score else "⭐ N/A"
                lines.append(
                    f"{medal} **{title}**\n"
                    f"     {score_str} | 📺 {episodes} eps | {status}\n"
                    f"     🏷️ {genres} | 🆔 `{mal_id}`\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch top anime: {e}"

    @app.tool()
    async def get_top_manga(
        category: str = "all",
        limit: int = 10,
    ) -> str:
        """
        Get the top-ranked manga from MyAnimeList.

        Args:
            category: Ranking type — 'all', 'manhwa', 'novel',
                      'oneshot', 'doujin', 'favorite', 'bypopularity'
            limit: Number of results (1–25)

        Returns:
            Ranked manga list with scores, volumes, and chapter counts.
        """
        try:
            cat_map = {
                "all": "bypopularity",
                "manhwa": "bypopularity",
                "novel": "bypopularity",
                "oneshot": "bypopularity",
                "favorite": "favorite",
                "bypopularity": "bypopularity",
            }
            filter_type = cat_map.get(category.lower(), "bypopularity")

            data = await jikan.get_top_manga(filter_type)
            manga_list = data.get("data", [])[:min(limit, 25)]

            if not manga_list:
                return "Could not retrieve top manga."

            lines = [f"📚 **Top {limit} Manga**\n"]
            medals = ["🥇", "🥈", "🥉"]

            for i, manga in enumerate(manga_list, 1):
                medal = medals[i - 1] if i <= 3 else f"**#{i}**"
                title = manga.get("title", "Unknown")
                score = manga.get("score")
                volumes = manga.get("volumes") or "Ongoing"
                chapters = manga.get("chapters") or "Ongoing"
                authors = ", ".join(a["name"] for a in manga.get("authors", [])[:2]) or "Unknown"
                mal_id = manga.get("mal_id", "")

                score_str = f"⭐ {score:.2f}" if score else "⭐ N/A"
                lines.append(
                    f"{medal} **{title}**\n"
                    f"     {score_str} | 📖 {volumes} vols / {chapters} chs\n"
                    f"     ✏️ {authors} | 🆔 `{mal_id}`\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch top manga: {e}"

    @app.tool()
    async def get_seasonal_anime(
        season: str | None = None,
        year: int | None = None,
    ) -> str:
        """
        Get anime airing in a specific season, or the current season if
        not specified. Use when a user asks 'what's airing this season?'
        or about anime from a specific season like 'Fall 2023'.

        Args:
            season: 'winter', 'spring', 'summer', or 'fall'
                    (defaults to current season)
            year: Year (defaults to current year)

        Returns:
            List of anime airing that season with scores and studio info.
        """
        try:
            cur_season, cur_year = _current_season()
            target_season = (season or cur_season).lower()
            target_year = year or cur_year

            season_map = {
                "winter": "WINTER", "spring": "SPRING",
                "summer": "SUMMER", "fall": "FALL",
            }
            if target_season not in season_map:
                return "Invalid season. Choose: winter, spring, summer, fall"

            # Try AniList first (richer data), fall back to Jikan
            try:
                results = await anilist.get_seasonal_anilist(
                    season_map[target_season], target_year, limit=20
                )
                if not results:
                    raise ValueError("Empty AniList result")

                lines = [
                    f"🌸 **{target_season.title()} {target_year} Anime** "
                    f"(via AniList)\n"
                ]
                for i, anime in enumerate(results, 1):
                    title_obj = anime.get("title", {})
                    title = title_obj.get("english") or title_obj.get("romaji", "Unknown")
                    score = anime.get("averageScore")
                    episodes = anime.get("episodes", "?")
                    genres = ", ".join(anime.get("genres", [])[:4]) or "N/A"
                    studios = ", ".join(
                        s.get("name", "") for s in
                        anime.get("studios", {}).get("nodes", [])[:2]
                    ) or "N/A"
                    status = anime.get("status", "")
                    url = anime.get("siteUrl", "")

                    score_str = f"⭐ {score/10:.1f}" if score else "⭐ N/A"
                    lines.append(
                        f"{i}. **{title}**\n"
                        f"   {score_str} | 📺 {episodes} eps | {status}\n"
                        f"   🎬 {studios} | 🏷️ {genres}\n"
                        f"   🔗 {url}\n"
                    )
                return "\n".join(lines)

            except Exception:
                # Jikan fallback
                data = await jikan.get_seasonal_anime(target_year, target_season)
                results = data.get("data", [])[:20]
                lines = [
                    f"🌸 **{target_season.title()} {target_year} Anime** "
                    f"(via Jikan)\n"
                ]
                for i, anime in enumerate(results, 1):
                    title = anime.get("title", "Unknown")
                    score = anime.get("score")
                    episodes = anime.get("episodes", "?")
                    studios = ", ".join(s["name"] for s in anime.get("studios", [])[:2]) or "N/A"
                    genres = ", ".join(g["name"] for g in anime.get("genres", [])[:3]) or "N/A"
                    score_str = f"⭐ {score:.1f}" if score else "⭐ N/A"
                    lines.append(
                        f"{i}. **{title}**\n"
                        f"   {score_str} | 📺 {episodes} eps | 🎬 {studios} | 🏷️ {genres}\n"
                    )
                return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch seasonal anime: {e}"

    @app.tool()
    async def get_trending_anime() -> str:
        """
        Get the currently trending anime from AniList.
        Use when a user asks 'what's popular right now?' or
        'what's everyone watching?'

        Returns:
            Top 10 trending anime with popularity scores and genre tags.
        """
        try:
            results = await anilist.get_trending_anime(limit=10)
            if not results:
                return "Could not fetch trending anime."

            lines = ["🔥 **Currently Trending Anime** (via AniList)\n"]
            for i, anime in enumerate(results, 1):
                title_obj = anime.get("title", {})
                title = title_obj.get("english") or title_obj.get("romaji", "Unknown")
                trending = anime.get("trending", 0)
                popularity = anime.get("popularity", 0)
                score = anime.get("averageScore")
                episodes = anime.get("episodes", "?")
                genres = ", ".join(anime.get("genres", [])[:4]) or "N/A"
                season = anime.get("season") or ""
                season_year = anime.get("seasonYear") or ""
                url = anime.get("siteUrl", "")

                score_str = f"⭐ {score/10:.1f}" if score else "⭐ N/A"
                season_str = f"{season.title()} {season_year}" if season else "?"

                lines.append(
                    f"{'🔥' if i == 1 else str(i) + '.'} **{title}**\n"
                    f"   📈 Trending score: {trending:,} | 👥 Popularity: {popularity:,}\n"
                    f"   {score_str} | 📺 {episodes} eps | 📅 {season_str}\n"
                    f"   🏷️ {genres}\n"
                    f"   🔗 {url}\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ Could not fetch trending anime: {e}"
