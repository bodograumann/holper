"""Core functionality"""

from itertools import groupby
from typing import Callable, Optional
import logging
import sqlalchemy
from . import tools, model

_logger = logging.getLogger(__name__)


def open_session(source: str) -> sqlalchemy.orm.Session:
    engine = sqlalchemy.create_engine(source, echo=False)
    if source.startswith("sqlite:"):
        tools.fix_sqlite_engine(engine)
    model.Base.metadata.create_all(engine)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session(future=True)


def get_event(session: sqlalchemy.orm.Session, event_id: int) -> Optional[model.Event]:
    try:
        (event,) = next(session.execute(sqlalchemy.select(model.Event).where(model.Event.event_id == event_id)))
        return event
    except StopIteration:
        return None


def get_race(session: sqlalchemy.orm.Session, race_id: int) -> Optional[model.Race]:
    try:
        (race,) = next(session.execute(sqlalchemy.select(model.Race).where(model.Race.race_id == race_id)))
        return race
    except StopIteration:
        return None


def hydrate_country_by_ioc_code(session, entity):
    if not entity or not entity.country:
        return

    ioc_code = entity.country.ioc_code
    result = session.execute(sqlalchemy.select(model.Country).where(model.Country.ioc_code == ioc_code))
    try:
        (country,) = next(result)
    except StopIteration:
        _logger.warning("Could not find country with ioc_code “%s” — Clearing.", ioc_code)
        entity.country = None
        return

    entity.country = country


def shadow_entity_by_xid(session, entity):
    cls = entity.__class__
    xid_cls = getattr(model, cls.__name__ + "XID")
    for xid in entity.external_ids:
        result = session.execute(
            sqlalchemy.select(xid_cls).where(xid_cls.issuer == xid.issuer).where(xid_cls.external_id == xid.external_id)
        )
        try:
            (saved_xid,) = next(result)
        except StopIteration:
            continue
        return getattr(saved_xid, tools.camelcase_to_snakecase(cls.__name__))
    return entity


def group_courses_by_first_control(race: model.Race) -> dict[str, list[model.Course]]:
    get_first_control: Callable[[model.Course], str] = lambda course: course.controls[1].control.label

    return {
        control_label: list(course_group)
        for control_label, course_group in groupby(sorted(race.courses, key=get_first_control), get_first_control)
    }
