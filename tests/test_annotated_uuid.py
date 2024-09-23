import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Session, SQLModel, create_engine, select

from tests.conftest import needs_pydanticv2


@needs_pydanticv2
def test_annotated_optional_types(clear_sqlmodel) -> None:
    from pydantic import UUID4

    class BaseHero(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: Optional[UUID4]

    blob = BaseHero(id=uuid.uuid4()).model_dump_json()
    assert isinstance(BaseHero.model_validate_json(blob).id, uuid.UUID)

    class Hero(SQLModel, table=True):
        # Pydantic UUID4 is: Annotated[UUID, UuidVersion(4)]
        id: Optional[UUID4] = Field(default_factory=uuid.uuid4, primary_key=True)

    blob = Hero(id=uuid.uuid4()).model_dump_json()
    assert isinstance(Hero.model_validate_json(blob).id, uuid.UUID)

    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        hero = Hero()
        db.add(hero)
        db.commit()
        statement = select(Hero)
        result = db.exec(statement).all()
    assert len(result) == 1
    assert isinstance(hero.id, uuid.UUID)
