"""Unit tests for importer endpoints"""
from unittest.mock import patch
import pytest
from sqlmodel.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from models import Character, Film, Starship

from importer import get_swapi_data, import_character_data, import_film_data, import_starship_data


mock_response1 = {
    "count": 37, 
    "next": "https://swapi.py4e.com/api/starships/?page=3", 
    "previous": "https://swapi.py4e.com/api/starships/?page=1", 
    "results": [
        {
            "name": "Slave 1",
            "url": "https://swapi.py4e.com/api/starships/1/"
        },
        {
            "name": "Imperial shuttle",
            "url": "https://swapi.py4e.com/api/starships/2/"
        },
    ]
}

@pytest.fixture(name="session")
def session_fixture():
    """Mocks a DB session"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def mock_response():
    """Mocks requests.session HTTP get"""
    with patch('requests.Session.get') as mock_get:
        yield mock_get

def test_get_swapi_data(mock_response):
    """Should fetch data from Star Wars API."""
    mock_response.return_value.json.return_value = mock_response1
    mock_response.return_value.status_code = 200

    url = 'https://swapi.py4e.com/api/starships/?page=1'
    next_url, data = get_swapi_data(url)

    mock_response.assert_called_once_with(url,
        headers={'accept': 'application/json', 'Content-Type': 'application/json'}, timeout=30)
    assert next_url == 'https://swapi.py4e.com/api/starships/?page=3'
    assert len(data) == 2


def test_import_character_data1(session: Session):
    """Should store a new Character record to DB."""
    character_id = 1
    character = {
        "birth_year": "19 BBY",
        "eye_color": "Blue",
        "films": [
            "https://swapi.py4e.com/api/films/1/",
        ],
        "gender": "Male",
        "hair_color": "Blond",
        "height": "172",
        "homeworld": "https://swapi.py4e.com/api/planets/1/",
        "mass": "77",
        "name": "Luke Skywalker",
        "skin_color": "Fair",
        "created": "2014-12-09T13:50:51.644000Z",
        "edited": "2014-12-10T13:52:43.172000Z",
        "species": [
            "https://swapi.py4e.com/api/species/1/"
        ],
        "starships": [
            "https://swapi.py4e.com/api/starships/12/",
        ],
        "url": "https://swapi.py4e.com/api/people/1/",
        "vehicles": [
            "https://swapi.py4e.com/api/vehicles/14/"
        ]
    }

    import_character_data(character_id, character, session)
    entry = session.get(Character, character_id)

    assert entry.id == 1
    assert entry.name == 'Luke Skywalker'
    assert entry.gender == 'Male'


def test_import_film_data1(session: Session):
    """Should store a new Film record to DB."""
    film_id = 1
    film = {
        "characters": [
            "https://swapi.py4e.com/api/people/1/",
        ],
        "created": "2014-12-10T14:23:31.880000Z",
        "director": "George Lucas",
        "edited": "2014-12-12T11:24:39.858000Z",
        "episode_id": 4,
        "planets": [
            "https://swapi.py4e.com/api/planets/1/",
        ],
        "producer": "Gary Kurtz, Rick McCallum",
        "release_date": "1977-05-25",
        "species": [
            "https://swapi.py4e.com/api/species/1/",
        ],
        "starships": [
            "https://swapi.py4e.com/api/starships/2/",
        ],
        "title": "A New Hope",
        "url": "https://swapi.py4e.com/api/films/1/",
        "vehicles": [
            "https://swapi.py4e.com/api/vehicles/4/",
        ]
    }

    import_film_data(film_id, film, session)
    entry = session.get(Film, film_id)

    assert entry.id == 1
    assert entry.name == 'A New Hope'
    assert entry.director == 'George Lucas'


def test_import_starship_data1(session: Session):
    """Should store a new Starship record to DB."""
    starship_id = 9
    starship = {
        "MGLT": "10 MGLT",
        "cargo_capacity": "1000000000000",
        "consumables": "3 years",
        "cost_in_credits": "1000000000000",
        "created": "2014-12-10T16:36:50.509000Z",
        "crew": "342953",
        "edited": "2014-12-10T16:36:50.509000Z",
        "hyperdrive_rating": "4.0",
        "length": "120000",
        "manufacturer": "Imperial Department of Military Research, Sienar Fleet Systems",
        "max_atmosphering_speed": "n/a",
        "model": "DS-1 Orbital Battle Station",
        "name": "Death Star",
        "passengers": "843342",
        "films": [
            "https://swapi.py4e.com/api/films/1/"
        ],
        "pilots": [],
        "starship_class": "Deep Space Mobile Battlestation",
        "url": "https://swapi.py4e.com/api/starships/9/"
    }

    import_starship_data(starship_id, starship, session)
    entry = session.get(Starship, starship_id)

    assert entry.id == 9
    assert entry.name == 'Death Star'
    assert entry.model == 'DS-1 Orbital Battle Station'
