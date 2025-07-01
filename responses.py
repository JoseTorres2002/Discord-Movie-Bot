import collections
from random import randint, sample
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_TOKEN = os.getenv("TMDB_TOKEN")
DEFAULT_COUNT = 10
#dict for watched since its faster and easier to update
user_watchlists = collections.defaultdict(lambda: {"to_watch": [], "watched": {}})

MovieGENRE_IDS = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "drama": 18,
    "documentary": 99,
    "family": 10751,
    "history": 36,
    "music": 18,
    "fantasy": 10402,
    "war": 10752,
    "western": 37,
    "horror": 27,
    "mystery": 9648,
    "romance": 10749,
    "sci-fi": 878,
    "thriller": 53
}

def get_response(user_id: str,user_input: str) -> str:

    user_input = user_input.lower().strip()
    print(f"Debug: User input is '{user_input}'")

    if user_input.startswith("top"):  # For toprated
        return get_top_rating(user_input)

    if user_input.startswith("random"):  # For random movie
        return get_random(user_input)

    if user_input.startswith("trending"):  # For trending
        return get_trending(user_input)

    if user_input.startswith("movie "):  # For a movie
        return get_movie(user_input)

    if user_input.startswith("watchlist"):  # For movie info
        return get_watchlist_movies(user_id,user_input)

    if user_input == "help":  # For command help
        return get_help()
    else:
        return "Command not recognized. Try: top [...], random [...], trending [...], movie [...] or watchlist [...]."

def fetch_from_tmdb(endpoint: str, params: dict) -> dict:
    """Fetch data from a given TMDB endpoint with provided parameters."""
    tmdb_base_url = "https://api.themoviedb.org/3"
    params["api_key"] = TMDB_TOKEN
    params["language"] = "en-US"
    response = requests.get(f"{tmdb_base_url}/{endpoint}", params=params)
    return response.json()

def format_movie_list(movies: list, count: int) -> str:
    """Format a list of movies into a numbered string."""
    return "\n".join([
        f"{i + 1}. {m['title']} ({m.get('release_date', 'Unknown')[:4]}) - ⭐ {m['vote_average']}"
        for i, m in enumerate(movies[:count])
    ])

def get_random(user_input: str) -> str:
    parts = user_input.split()
    count = DEFAULT_COUNT
    genre = None
    year = None

    for part in parts[1:]:
        if part.isdigit():
            if len(part) == 4:  # Year input
                year = part
            else:  # Count input
                count = int(part)
        elif part.lower() in MovieGENRE_IDS:
            genre = part.lower()

    #dictionary
    params = {"sort_by": "vote_average.desc", "vote_count.gte": 1000}
    if genre:
        params["with_genres"] = MovieGENRE_IDS[genre]
    if year:
        params["primary_release_year"] = year

    data = fetch_from_tmdb("discover/movie", params)

    random_movies = sample(data["results"], min(count, len(data["results"])))
    return f"**{count} Random Movies:**\n{format_movie_list(random_movies, count)}"

def get_top_rating(user_input: str) -> str: #general
    parts = user_input.split()
    count = DEFAULT_COUNT
    genre = None
    year = None

    for part in parts[1:]:
        if part.isdigit():
            if len(part) == 4:  # Year input
                year = part
            else:  # Count input
                count = int(part)
        elif part.lower() in MovieGENRE_IDS:
            genre = part.lower()

    params = {"sort_by": "vote_average.desc", "vote_count.gte": 1000}
    if genre:
        params["with_genres"] = MovieGENRE_IDS[genre]
    if year:
        params["primary_release_year"] = year

    data = fetch_from_tmdb("discover/movie", params)

    top_movies = data["results"][:count]
    return f"**Top {count} Movies:**\n{format_movie_list(top_movies, count)}"

def get_trending(user_input: str) -> str:
    parts = user_input.split()
    count = DEFAULT_COUNT
    genre = None
    year = None

    for part in parts[1:]:
        if part.isdigit():
            if len(part) == 4:  # Year input
                year = part
            else:  # Count input
                count = int(part)
        elif part.lower() in MovieGENRE_IDS:
            genre = part.lower()

    # Default to Trending API if no year or genre is given
    if not year and not genre:
        data = fetch_from_tmdb("trending/movie/day", {})
    else:
        params = {"sort_by": "popularity.desc", "vote_count.gte": 1000}
        if genre:
            params["with_genres"] = MovieGENRE_IDS[genre]
        if year:
            params["primary_release_year"] = year

        data = fetch_from_tmdb("discover/movie", params)

    trending_movies = data["results"][:count]
    return f"**Top {count} Trending Movies:**\n{format_movie_list(trending_movies, count)}"

def get_movie(user_input: str) -> str: #trivia about the movie and 5 similar movies to it
    parts = user_input.split()

    movie_name = " ".join(parts[1:])  # Extract movie name after "movie"
    year = None

    # Extract the year if the last part is a 4-digit number
    if parts[-1].isdigit() and len(parts[-1]) == 4:
        year = parts[-1]
        movie_name = " ".join(parts[1:-1])

    params = {"query": movie_name}
    if year:
        params["year"] = year

    search_data = fetch_from_tmdb("search/movie", params)
    if not search_data["results"]:
        return "Movie not found."

    movie = search_data["results"][0]
    movie_id = movie["id"]

    movie_details = f"**{movie['title']} ({movie.get('release_date', 'Unknown')[:4]})**\n{movie.get('overview', 'No description available.')}\n"

    similar_data = fetch_from_tmdb(f"movie/{movie_id}/similar", {})
    similar_movies = similar_data.get("results", [])[:5]

    similar_text = "\n".join([f"- {m['title']} ({m.get('release_date', 'Unknown')[:4]})" for m in
                              similar_movies]) if similar_movies else "No similar movies found."

    return f"{movie_details}\n**Similar Movies:**\n{similar_text}"

def get_watchlist_movies(user_id: str, user_input: str) -> str:
    parts = user_input.split()

    if len(parts) < 2:
        return "Invalid command. Use 'watchlist create', 'watchlist add <movie> <year>', etc."

    command = parts[1].lower()
    user_watchlist = user_watchlists.get(user_id, {"to_watch": [], "watched": []})

    if command == "create":
        if user_watchlist["to_watch"] or user_watchlist["watched"]:
            return "You already have a watchlist."
        user_watchlists[user_id] = user_watchlist
        return "Your watchlist has been created!"

    elif command == "add":
        if len(parts) < 3:
            return "Please provide a movie name."
        # Extract movie name and optional year
        if parts[-1].isdigit() and len(parts[-1]) == 4:  # Year is provided
            movie_name = " ".join(parts[2:-1])
            year = parts[-1]
        else:  # No year provided
            movie_name = " ".join(parts[2:])
            year = None
        # Prevent duplicates (check by name and year combination)
        if any(m["movie_name"].lower() == movie_name.lower() and (
                m["year"] == year or (not year and m["year"] == "Unknown")) for m in user_watchlist["to_watch"]):
            return f"'{movie_name} ({year if year else 'Unknown'})' is already in your watchlist."

        params = {"query": movie_name}
        if year:
            params["year"] = year
        data = fetch_from_tmdb("search/movie", params)

        if data["results"]:
            movie_data = data["results"][0]
            movie_details = {"movie_name": movie_data["title"], "year": movie_data.get("release_date", "Unknown")[:4],
                             "id": movie_data["id"]}
            user_watchlist["to_watch"].append(movie_details)
            user_watchlists[user_id] = user_watchlist
            return f"Added '{movie_data['title']} ({movie_details['year']})' to your watchlist."
        return f"Movie '{movie_name}' not found on TMDB."

    elif command == "remove":
        if len(parts) < 4:
            return "Please provide a movie name and year."

        movie_name = " ".join(parts[2:-1])
        year = parts[-1]
        if not year.isdigit() or len(year) != 4:
            return "Please provide a valid 4-digit year."

        # Normalize movie name (remove 'the' if present and make lowercase)
        movie_name_normalized = movie_name.lower()
        # Try to find and remove the movie from the "To Watch" list
        for movie in user_watchlist["to_watch"]:
            stored_movie_name = movie["movie_name"].strip().lower()
            stored_movie_year = movie["year"]
            # Ensure both the movie name and year are matched correctly
            if stored_movie_name.strip().lower() == movie_name_normalized and stored_movie_year == year:
                user_watchlist["to_watch"].remove(movie)
                user_watchlists[user_id] = user_watchlist
                return f"Removed '{movie['movie_name']} ({movie['year']})' from your watchlist."
        # If not found in "To Watch", try removing from the "Watched" list
        for movie in user_watchlist["watched"]:
            stored_movie_name = movie["movie_name"].strip().lower()
            stored_movie_year = movie["year"]
            # Ensure both the movie name and year are matched correctly
            if stored_movie_name == movie_name_normalized and stored_movie_year == year:
                user_watchlist["watched"].remove(movie)
                user_watchlists[user_id] = user_watchlist
                return f"Removed '{movie['movie_name']} ({movie['year']})' from your watched list."

        return f"'{movie_name} ({year})' not found in your watchlist or watched list."

    elif command == "watched":
        if len(parts) < 4:
            return "Please provide a movie name and year."
        movie_name = " ".join(parts[2:-1])
        year = parts[-1]

        for movie in user_watchlist["to_watch"]:
            if movie["movie_name"].lower() == movie_name.lower() and movie["year"] == year:
                user_watchlist["to_watch"].remove(movie)
                user_watchlist["watched"].append({"movie_name": movie_name, "year": year, "rating": None})
                user_watchlists[user_id] = user_watchlist
                return f"Moved '{movie_name} ({year})' to your watched list."
        return f"'{movie_name} ({year})' not found in your watchlist."

    elif command.isdigit():
        rating = int(command)
        if rating < 1 or rating > 10:
            return "Please provide a rating between 1 and 10."

        if len(parts) < 4:
            return "Please provide a movie name and year to rate."
        movie_name = " ".join(parts[2:-1])
        year = parts[-1]

        for movie in user_watchlist["watched"]:
            if movie["movie_name"] == movie_name and movie["year"] == year:
                movie["rating"] = rating
                user_watchlists[user_id] = user_watchlist
                return f"Rated '{movie_name} ({year})' with {rating}/10."
        return f"'{movie_name} ({year})' not found in your watched list."

    elif command == "see":
        if not user_watchlist["to_watch"] and not user_watchlist["watched"]:
            return "You don't have a watchlist yet. Create one with 'watchlist create'."

        to_watch = "\n".join([f"- {movie['movie_name']} ({movie['year']})" for movie in user_watchlist["to_watch"]])
        watched = "\n".join([f"- {movie['movie_name']} ({movie['year']}) ⭐ {movie['rating']}/10"
                             if movie["rating"] else f"- {movie['movie_name']} ({movie['year']})"
                             for movie in user_watchlist["watched"]])

        return f"**Your Watchlist**\n\n**To Watch:**\n{to_watch if to_watch else 'None'}\n\n**Watched:**\n{watched if watched else 'None'}"

    elif command == "delete":
        if user_id in user_watchlists:
            del user_watchlists[user_id]
            return "Your watchlist has been deleted."
        return "You don't have a watchlist to delete."

    return "Unknown command. Use 'watchlist create', 'watchlist add <movie> <year>', etc."

def get_help() -> str:
    help_text = """
    **Available Commands:**

    1. **top [count] [year] [genre]:**  
       Get the top-rated movies.  
       - Example: `top (any combination)`  

    2. **random [count] [year] [genre]:**  
       Get a random selection of movies.  
       - Example: `random (any combination)`  

    3. **trending [count] [year] [genre]:**  
       Get the top trending movies.  
       - Example: `trending (any combination)`  

    4. **movie [movie_name]:**  
       Get information about a specific movie.  
       - Example: `movie Inception`

    5. **watchlist [create] [add] [remove] [rate] [watched] [delete]:**  
       - Add or remove movies from your watchlist.  
       - move movies from "to watch" to "wacthed"
       - rate movies in your watched list  
       - create or delete your watchlist
       
    """

    return help_text









