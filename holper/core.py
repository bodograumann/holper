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
        return session.execute(
            select(model.Event).where(model.Event.event_id == event_id),
        ).one()[0]
    return None


def get_race(session: orm.Session, race_id: int) -> model.Race | None:
    with suppress(NoResultFound):
        return session.execute(
            select(model.Race).where(model.Race.race_id == race_id),
        ).one()[0]
    return None


def hydrate_country_by_ioc_code(session, entity: model.Organisation | model.Person | None):
    if not entity or not entity.country:
        return

    ioc_code = entity.country.ioc_code
    try:
        country = session.execute(
            select(model.Country).where(model.Country.ioc_code == ioc_code),
        ).one()[0]
    except NoResultFound:
        _logger.warning("Could not find country with ioc_code “%s” — Clearing.", ioc_code)
        entity.country = None
        return

    entity.country = country


def shadow_entity_by_xid(session, entity):
    cls = entity.__class__
    xid_cls = getattr(model, cls.__name__ + "XID")
    for xid in entity.external_ids:
        try:
            saved_xid = session.execute(
                select(xid_cls).where(xid_cls.issuer == xid.issuer).where(xid_cls.external_id == xid.external_id),
            ).one()[0]
        except NoResultFound:
            continue
        return getattr(saved_xid, tools.camelcase_to_snakecase(cls.__name__))
    return entity


def group_courses_by_first_control(race: model.Race) -> dict[str, list[model.Course]]:
    def get_first_control(course: model.Course) -> str:
        return course.controls[1].control.label

    return {
        control_label: list(course_group)
        for control_label, course_group in groupby(sorted(race.courses, key=get_first_control), get_first_control)
    }
