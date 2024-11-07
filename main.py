"""REST API endpoints and entry point"""
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from models import Character, Film, Starship, engine, create_db_and_tables
from importer import import_data_from_swapi


def get_session():
    """Yields a DB session"""
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(api: FastAPI):
    """Handles API startup tasks, before it starts
    getting requests."""
    create_db_and_tables()  # Create DB tables, if they don't exist.
    yield

app = FastAPI(lifespan=lifespan)


@app.exception_handler(404)
async def handler_404(_, __):
    """Handler for HTTP 404 errors"""
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({
        'message': 'Page not found!',
    }))


@app.exception_handler(500)
async def internal_exception_handler(_, __):
    """Handler for HTTP 500 errors"""
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
        'message': 'Internal Server Error',
    }))


@app.get('/characters', response_model=List[Character], status_code=status.HTTP_200_OK)
async def characters(offset: int=0, limit: int=Query(default=100, le=100),
                     session: Session = Depends(get_session)):
    """Retrieves all characters from db. Returns results in pages up to
    100 entries long."""
    q = select(Character).order_by('name').offset(offset).limit(limit)
    return session.exec(q).all()


@app.get('/characters/{character_id}/', response_model=Character, status_code=status.HTTP_200_OK)
def character(character_id: int, session: Session = Depends(get_session)):
    """Retrieves a specific Character from DB, by id. Returns HTTP 404 if
    no such Character in DB."""
    entry = session.get(Character, character_id)
    if entry is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({'message': 'Entry not found!'}))

    return entry


@app.get('/films', response_model=List[Film], status_code=status.HTTP_200_OK)
async def films(offset: int = 0, limit: int = Query(default=100, le=100),
                session: Session = Depends(get_session)):
    """Retrieves all Films from DB. Returns results to pages up to
    100 entries long."""
    q = select(Film).order_by('name').offset(offset).limit(limit)
    return session.exec(q).all()


@app.get('/films/{film_id}/', response_model=Film, status_code=status.HTTP_200_OK)
def film(film_id: int, session: Session = Depends(get_session)):
    """Retrieves a specific Film from DB, by id. Returns HTTP 404 if
    no such Film in DB."""
    entry = session.get(Film, film_id)
    if entry is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({'message': 'Entry not found!'}))

    return entry


@app.get('/starships', response_model=List[Starship], status_code=status.HTTP_200_OK)
async def starships(offset: int = 0, limit: int = Query(default=100, le=100),
                    session: Session = Depends(get_session)):
    """Retrieves all starships from DB. Returns results in pages up to
    100 entries long."""

    q = select(Starship).order_by('name').offset(offset).limit(limit)
    return session.exec(q).all()


@app.get('/starships/{starship_id}/', response_model=Starship, status_code=status.HTTP_200_OK)
def starship(starship_id: int, response: Response, session: Session = Depends(get_session)):
    """Retrieves a specific Starship from DB, by id. Returns HTTP 404 if
    no such Film in DB."""

    entry = session.get(Starship, starship_id)
    if entry is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({'message': 'Entry not found!'}))

    return entry


@app.get('/import', status_code=status.HTTP_200_OK)
async def import_data(session: Session = Depends(get_session)):
    """Imports data from Starwars API to local DB."""
    results = {}
    for kind in ['people', 'films', 'starships']:
        results[kind] = import_data_from_swapi(kind, session)

    return results

@app.get('/search', status_code=status.HTTP_200_OK)
async def search(term: str, session: Session = Depends(get_session)):
    """Searches for Characters, Films and Starships in local DB,
    by name."""
    results = []
    for model in [Character, Film, Starship]:
        results.extend(session.exec(select(model).where(model.name.contains(term))).all())

    return results
