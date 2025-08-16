import requests
from rating_grid_generator import generate_episode_grid

API_KEY = "ebaea042"  # 🔑 put your OMDb API key here
TITLE = "death note"     # 🎬 anime/series name


def fetch_imdb_id(title: str, api_key: str):
    """Search OMDb for a title and return IMDb ID + basic info"""
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}"
    data = requests.get(url).json()
    if data.get("Response") == "True":
        return data["imdbID"], float(data["imdbRating"]) if data["imdbRating"] != "N/A" else None, data.get("Year", "-")
    return None, None, None


def fetch_episode_ratings(imdb_id: str, api_key: str):
    """Fetch all season episode ratings for a show"""
    season_to_ratings = {}
    season = 1
    while True:
        url = f"http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}&Season={season}"
        data = requests.get(url).json()
        if data.get("Response") != "True":
            break

        episodes = data.get("Episodes", [])
        ratings = []
        for ep in episodes:
            rating = ep.get("imdbRating", "N/A")
            if rating == "N/A":
                ratings.append(0.0)  # ✅ replace None with 0.0
            else:
                ratings.append(float(rating))

        # ✅ Print ratings of each season
        print(f"Season {season} ratings: {ratings}")

        season_to_ratings[f"S{season}"] = ratings
        season += 1

    return season_to_ratings



if __name__ == "__main__":
    imdb_id, overall_rating, years = fetch_imdb_id(TITLE, API_KEY)
    if imdb_id:
        season_to_ratings = fetch_episode_ratings(imdb_id, API_KEY)

        generate_episode_grid(
            out_path=f"./{TITLE.lower().replace(' ', '_')}_ratings.png",
            title=TITLE,
            overall_rating=overall_rating,
            years=years,
            season_to_ratings=season_to_ratings,
            poster_path=None  # optional: download poster image if you want
        )
        print(f"✅ Ratings grid generated for {TITLE}")
    else:
        print("❌ Could not find this title on OMDb")

