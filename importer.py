"""Functionality for importing data from
Star Wars API"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from sqlmodel import Session, select
from models import Character, Film, Starship, CharacterFilmLink, CharacterStarshipLink, StarshipFilmLink
from utils import fetch_ids_from_urls, remove_common_elements_from_list

# Constants
NA = 'n/a'
SWAPI_BASE_URL = 'https://swapi.py4e.com/api'

# Setup HTTP retries mechanism
retry = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[403, 429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry)
r_session = requests.Session()
r_session.mount('https://', adapter)


def get_swapi_data(url: str) -> None:
    """Utility for retrieving data from Star Wars REST API.
    HTTP GETs data from given URL. Retrieved data are expected
    to be valid JSON."""
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = r_session.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        response.raise_for_status()

    response_data = response.json()
    return response_data.get('next', None), response_data.get('results', [])


def import_character_data(character_id: int, character: dict, session: Session) -> None:
    """Maps Character data and imports them to DB. Also updates corresponding
    many-to-many relationships tables."""
    character_record = Character(
        id = character_id,
        name = character.get('name', NA),
        height = character.get('height', NA),
        mass = character.get('mass', NA),
        hair_color = character.get('hair_color', NA),
        skin_color = character.get('skin_color', NA),
        eye_color = character.get('eye_color', NA),
        birth_year = character.get('birth_year', NA),
        gender = character.get('gender', NA),
    )

    session.add(character_record)

    film_ids = fetch_ids_from_urls(character.get('films', []))
    starship_ids = fetch_ids_from_urls(character.get('starships', []))

    existing_character_film_ids = session.exec(
        select(CharacterFilmLink.film_id).where(CharacterFilmLink.character_id==character_id)).all()
    existing_character_starship_ids = session.exec(
        select(CharacterStarshipLink.starship_id).where(CharacterStarshipLink.character_id==character_id)).all()

    for film_id in remove_common_elements_from_list(film_ids, existing_character_film_ids):
        session.add(CharacterFilmLink(character_id=character_id, film_id=film_id))

    for starship_id in remove_common_elements_from_list(starship_ids, existing_character_starship_ids):
        session.add(CharacterStarshipLink(character_id=character_id, starship_id=starship_id))


def import_film_data(film_id: int, film: dict, session: Session) -> None:
    """Maps Film data and imports them to DB. Also updates corresponding
    many-to-many relationships tables."""
    film_record = Film(
        id = film_id,
        name = film.get('title', NA),
        episode_id = film.get('episode_id', NA),
        opening_crawl = film.get('opening_crawl', NA),
        director = film.get('director', NA),
        producer = film.get('producer', NA),
        release_date = film.get('release_date', NA)
    )

    session.add(film_record)

    character_ids = fetch_ids_from_urls(film.get('characters', []))
    starship_ids = fetch_ids_from_urls(film.get('starships', []))

    existing_film_character_ids = session.exec(
        select(CharacterFilmLink.character_id).where(CharacterFilmLink.film_id==film_id)).all()
    existing_film_starship_ids = session.exec(
        select(StarshipFilmLink.starship_id).where(StarshipFilmLink.film_id==film_id)).all()

    for character_id in remove_common_elements_from_list(character_ids, existing_film_character_ids):
        session.add(CharacterFilmLink(character_id=character_id, film_id=film_id))

    for starship_id in remove_common_elements_from_list(starship_ids, existing_film_starship_ids):
        session.add(StarshipFilmLink(starship_id=starship_id, film_id=film_id))


def import_starship_data(starship_id: int, starship: dict, session: Session) -> None:
    """Maps Starship data and imports them to DB. Also updates corresponding
    many-to-many relationships tables."""
    starship_record = Starship(
        id = starship_id,
        name = starship.get('name', NA),
        model = starship.get('model', NA),
        manufacturer = starship.get('manufacturer', NA),
        cost_in_credits = starship.get('cost_in_credits', NA),
        length = starship.get('length', NA),
        max_atmosphering_speed = starship.get('max_atmosphering_speed', NA),
        crew = starship.get('crew', NA),
        passengers = starship.get('passengers', NA),
        cargo_capacity = starship.get('cargo_capacity', NA),
        consumables = starship.get('consumables', NA),
        hyperdrive_rating = starship.get('hyperdrive_rating', NA),
        MGLT = starship.get('MGLT', NA),
        starship_class = starship.get('starship_class', NA)
    )

    session.add(starship_record)

    film_ids = fetch_ids_from_urls(starship.get('films', []))
    existing_starship_film_ids = session.exec(
        select(StarshipFilmLink.film_id).where(StarshipFilmLink.starship_id==starship_id)).all()

    for film_id in remove_common_elements_from_list(film_ids, existing_starship_film_ids):
        session.add(StarshipFilmLink(starship_id=starship_id, film_id=film_id))


def import_data_from_swapi(kind: str, session: Session) -> int:
    """Imports data from Star Wars API, for given kind.
    kind can be one of the following: People (Characters),
    Films, Starships.
    """
    importers = {
        'people': import_character_data,
        'films': import_film_data,
        'starships': import_starship_data,
    }

    db_models = {
        'people': Character,
        'films': Film,
        'starships': Starship
    }

    importer = importers.get(kind, None)
    if importer is None:
        return

    imports_count = 0

    # All ids already stored in DB for specified db model.
    # Entries already existing in DB (by id) will not be
    # imported again.
    ids = session.exec(select(db_models[kind].id)).all()

    # Iterate Star Wars API pages, until no more pages exist.
    # For each page, import fetched data to DB.
    next_page_url = f'{SWAPI_BASE_URL}/{kind}/?page=1'
    while next_page_url is not None:
        next_page_url, items = get_swapi_data(next_page_url)
        for item in items:
            item_id = int(item.get('url').strip('/').rsplit('/', 1)[-1])

            # Skip this entry, already on DB (by id).
            if item_id in ids:
                continue

            # Use specified importer in order to add record to DB.
            importer(item_id, item, session)
            imports_count += 1

    session.commit()

    return imports_count
