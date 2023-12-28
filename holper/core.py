"""Core functionality"""

import logging
from contextlib import suppress
from itertools import groupby

from sqlalchemy import create_engine, orm, select
from sqlalchemy.exc import NoResultFound

from . import model, tools

_logger = logging.getLogger(__name__)


def open_session(source: str) -> orm.Session:
    engine = create_engine(source, echo=False)
    if source.startswith("sqlite:"):
        tools.fix_sqlite_engine(engine)
    model.Base.metadata.create_all(engine)

    Session = orm.sessionmaker(bind=engine)  # noqa: N806
    return Session(future=True)


def get_event(session: orm.Session, event_id: int) -> model.Event | None:
    with suppress(NoResultFound):
        return session.scalars(
            select(model.Event).where(model.Event.event_id == event_id),
        ).one()
    return None


def get_race(session: orm.Session, race_id: int) -> model.Race | None:
    with suppress(NoResultFound):
        return session.scalars(
            select(model.Race).where(model.Race.race_id == race_id),
        ).one()
    return None


def get_countries(session: orm.Session) -> list[model.Country]:
    return list(session.scalars(select(model.Country)).all())


def group_courses_by_first_control(race: model.Race) -> dict[str, list[model.Course]]:
    def get_first_control(course: model.Course) -> str:
        return course.controls[1].control.label

    return {
        control_label: list(course_group)
        for control_label, course_group in groupby(sorted(race.courses, key=get_first_control), get_first_control)
    }
