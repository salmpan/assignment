"""Unit tests for REST API endpoints"""
import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session
from models import Character, Film, Starship


@pytest.fixture(name="session")
def session_fixture():
    """Mocks a DB session"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Mocks our client"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def add_characters(session):
    """Utility function for adding characters to test DB"""
    session.add(Character(id=1, name='Character1'))
    session.add(Character(id=2, name='Character2'))
    session.add(Character(id=3, name='Character3'))
    session.commit()


def add_films(session):
    """Utility function for adding films to test DB"""
    session.add(Film(id=1, name='Film1'))
    session.add(Film(id=2, name='Film2'))
    session.add(Film(id=3, name='Film3'))
    session.commit()


def add_starships(session):
    """Utility function for adding starships to test DB"""
    session.add(Starship(id=1, name='Starship1'))
    session.add(Starship(id=2, name='Starship2'))
    session.add(Starship(id=3, name='Starship3'))
    session.commit()


def test_character1(client: TestClient):
    """Should return 404 because DB is empty."""
    client = TestClient(app)

    response = client.get('/character/100')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_character2(session: Session, client: TestClient):
    """Should return 404 because no such character id in DB."""
    add_characters(session)

    response = client.get("/characters/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_character3(session: Session, client: TestClient):
    """Should return 200 because there is a character with given id in DB."""
    add_characters(session)

    response = client.get("/characters/1")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['name'] == 'Character1'


def test_characters1(session: Session, client: TestClient):
    """Should return 200 and a list of characters"""
    add_characters(session)

    response = client.get('/characters')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 3

    # Data should be returned ordered by name
    assert data[0]['name'] == 'Character1'
    assert data[1]['name'] == 'Character2'
    assert data[2]['name'] == 'Character3'


def test_film1(client: TestClient):
    """Should return 404 because DB is empty."""
    client = TestClient(app)

    response = client.get('/film/100')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_film2(session: Session, client: TestClient):
    """Should return 404 because no such character id in DB."""
    add_films(session)

    response = client.get("/films/100")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_film3(session: Session, client: TestClient):
    """Should return 200 because there is a film with given id in DB."""
    add_films(session)

    response = client.get("/films/1")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['name'] == 'Film1'


def test_films1(session: Session, client: TestClient):
    """Should return 200 and a list of films"""
    add_films(session)

    response = client.get('/films')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 3

    # Data should be returned ordered by name
    assert data[0]['name'] == 'Film1'
    assert data[1]['name'] == 'Film2'
    assert data[2]['name'] == 'Film3'


def test_starship1(client: TestClient):
    """Should return 404 because DB is empty."""
    client = TestClient(app)

    response = client.get('/starship/100')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_starship2(session: Session, client: TestClient):
    """Should return 404 because no such character id in DB."""
    add_starships(session)

    response = client.get("/starship/100")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_starship3(session: Session, client: TestClient):
    """Should return 200 because there is a starship with given id in DB."""
    add_starships(session)

    response = client.get("/starships/1")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['name'] == 'Starship1'


def test_starships1(session: Session, client: TestClient):
    """Should return 200 and a list of starships"""
    add_starships(session)

    response = client.get('/starships')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 3

    # Data should be returned ordered by name
    assert data[0]['name'] == 'Starship1'
    assert data[1]['name'] == 'Starship2'
    assert data[2]['name'] == 'Starship3'
