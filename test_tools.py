import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

funcs = {}

class FakeMCP:
    def tool(self, name=None):
        def decorator(f):
            funcs[name or f.__name__] = f
            return f
        return decorator

app = FakeMCP()

from tools import search, details, rankings, manga, watchlist, extras, art

search.register(app)
details.register(app)
rankings.register(app)
manga.register(app)
watchlist.register(app)
extras.register(app)
art.register(app)

async def test_tool(func_name, **kwargs):
    print(f"\n{'='*50}\n🔍 Testing [{func_name}] with {kwargs}")
    try:
        res = await funcs[func_name](**kwargs)
        if isinstance(res, str):
            print(res)
        else:
            print(f"Error: Tool did not return a string! Returned: {type(res)}")
    except Exception as e:
        print(f"Exception running {func_name}: {e}")

async def run_all():
    # 1. Search
    await test_tool("search_anime", query="Death Note")
    await test_tool("search_manga", query="Berserk")
    await test_tool("search_character", name="Gojo Satoru")
    await test_tool("search_studio", name="Madhouse")

    # 2. Details
    await test_tool("get_anime_details", anime_id=20)   # Naruto ID
    await test_tool("get_manga_details", manga_id=2)    # Berserk
    await test_tool("get_character_details", character_id=17) # Naruto Char
    await test_tool("get_anime_episodes", anime_id=20)
    await test_tool("get_anime_staff", anime_id=20)
    await test_tool("get_anime_reviews", anime_id=20)

    # 3. Rankings
    await test_tool("get_top_anime", category="all", limit=3)
    await test_tool("get_top_manga", limit=3)
    await test_tool("get_seasonal_anime")
    await test_tool("get_trending_anime")

    # 4. Manga Reading
    await test_tool("get_manga_chapters", manga_title="Chainsaw Man", limit=5)
    await test_tool("get_manga_reading_link", manga_title="Chainsaw Man", chapter=1)

    # 5. Watchlist & Favorites
    await test_tool("add_to_watchlist", anime_title="Bleach", status="watching")
    await test_tool("update_watchlist_status", anime_title="Bleach", status="completed")
    await test_tool("get_watchlist")
    await test_tool("remove_from_watchlist", anime_title="Bleach")
    await test_tool("add_to_favorites", anime_title="Steins;Gate")
    await test_tool("get_favorites")

    # 6. Extras
    await test_tool("get_anime_recommendations", anime_id=20)
    await test_tool("get_personalized_recommendations", genres=["Action", "Comedy"])
    await test_tool("get_random_anime")
    await test_tool("get_anime_quotes")
    await test_tool("get_upcoming_anime")
    await test_tool("compare_anime", anime_id_1=20, anime_id_2=21)

    # 7. Art
    await test_tool("get_anime_pictures", anime_id=20)
    await test_tool("get_character_pictures", character_id=17)

if __name__ == "__main__":
    asyncio.run(run_all())
