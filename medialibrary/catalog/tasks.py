import logging

from celery import shared_task

from medialibrary.catalog.imdb import (
    get_people_info,
    get_staff_info,
    get_top_movies_ids_and_info,
    prepare_movie_data,
    update_or_create_movies,
)

logger = logging.getLogger(__name__)


@shared_task
def fetch_movies():
    try:
        ids, basic_info = get_top_movies_ids_and_info(1000)
        staff_info = get_staff_info(ids)
        people_info = get_people_info(staff_info["nconst"].unique().tolist())
        movies_data = [
            prepare_movie_data(movie_id, basic_info, staff_info, people_info)
            for movie_id in ids
        ]
        update_or_create_movies(movies_data)
    except Exception as e:
        logger.error(f"Failed to fetch movies: {type(e)} {e}")
