"""Core functionality"""

from typing import Optional
import sqlalchemy
from . import tools, model


def open_session(source: str) -> sqlalchemy.orm.Session:
    engine = sqlalchemy.create_engine(source, echo=False)
    if source.startswith("sqlite:"):
        tools.fix_sqlite_engine(engine)
    model.Base.metadata.create_all(engine)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()


def get_event(session: sqlalchemy.orm.Session, event_id: int) -> Optional[model.Event]:
    try:
        (event,) = next(
            session.execute(
                sqlalchemy.select(model.Event).where(model.Event.event_id == event_id)
            )
        )
        return event
    except StopIteration:
        return None
