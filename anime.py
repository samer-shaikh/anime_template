from rating_grid_generator import generate_episode_grid

my_ratings = [8.4, 8.9, 8.4, 8.7, 8.5, 8.2, 9.1, 8.4, 8.5, 8.1, 8.7, 8.2, 8.3, 8.2, 8.9, 8.3, 8.0, 7.3, 7.6, 7.3, 7.7, 8.1, 8.8, 9.3, 9.5, 0.0, 0.0, 0.0, 0.0, 7.6, 7.6, 0.0, 0.0, 0.0, 7.9, 8.9, 8.6]

generate_episode_grid(
    out_path="./banana_fish_ratings.png",
    title="Banana Fish",
    overall_rating=8.1,
    years="2018",
    season_to_ratings={"S1": my_ratings},  # add more seasons like {"S1": [...], "S2": [...]}
    poster_path=None,  # or path to a local JPG/PNG poster
    
)
