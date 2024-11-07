"""DB models/tables"""
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine

DB_FILE = 'db.sqlite3'
engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)


class StarshipFilmLink(SQLModel, table=True):
    """Starship-Film many-to-many relationship table."""
    starship_id: int | None = Field(default=None, foreign_key="starship.id", primary_key=True)
    film_id: int | None = Field(default=None, foreign_key="film.id", primary_key=True)

    starship: "Starship" = Relationship(back_populates="film_links")
    film: "Film" = Relationship(back_populates="starship_links")


class CharacterFilmLink(SQLModel, table=True):
    """Character-Film many-to-many relationship table."""
    character_id: int | None = Field(default=None, foreign_key="character.id", primary_key=True)
    film_id: int | None = Field(default=None, foreign_key="film.id", primary_key=True)

    character: "Character" = Relationship(back_populates="film_links")
    film: "Film" = Relationship(back_populates="character_links")


class CharacterStarshipLink(SQLModel, table=True):
    """Character-Starship many-to-many relationship table."""
    character_id: int | None = Field(default=None, foreign_key="character.id", primary_key=True)
    starship_id: int | None = Field(default=None, foreign_key="starship.id", primary_key=True)

    character: "Character" = Relationship(back_populates="starship_links")


class Character(SQLModel, table=True):
    """Character model/table."""
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    height: Optional[str]
    mass: Optional[str]
    hair_color: Optional[str]
    skin_color: Optional[str]
    eye_color: Optional[str]
    birth_year: Optional[str]
    gender: Optional[str]
    film_links: list[CharacterFilmLink] = Relationship(back_populates='character')
    starship_links: list[CharacterStarshipLink] = Relationship(back_populates='character')


class Film(SQLModel, table=True):
    """Film model/table."""
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    episode_id: Optional[str]
    opening_crawl: Optional[str]
    director: Optional[str]
    producer: Optional[str]
    release_date: Optional[str]
    character_links: list[CharacterFilmLink] = Relationship(back_populates='film')
    starship_links: list[StarshipFilmLink] = Relationship(back_populates='film')


class Starship(SQLModel, table=True):
    """Starship model/table."""
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    model: Optional[str]
    manufacturer: Optional[str]
    cost_in_credits: Optional[str]
    length: Optional[str]
    max_atmosphering_speed: Optional[str]
    crew: Optional[str]
    passengers: Optional[str]
    cargo_capacity: Optional[str]
    consumables: Optional[str]
    hyperdrive_rating: Optional[str]
    MGLT: Optional[str]
    starship_class: Optional[str]
    film_links: list[StarshipFilmLink] = Relationship(back_populates='starship')


def create_db_and_tables():
    """Creates all DB tables described by models, if they
    don't exist already"""
    SQLModel.metadata.create_all(engine)
