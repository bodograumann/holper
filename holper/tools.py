"""Miscellaneous helper functions"""

import re
from collections.abc import Callable
from datetime import date
from typing import Any, TypeVar

import sqlalchemy


# Taken from http://stackoverflow.com/a/1176023
def camelcase_to_snakecase(name_camel: str) -> str:
    """Convert CamelCase to snake_case syntax"""
    name_tmp = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name_camel)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name_tmp).lower()


def fix_sqlite_engine(engine: sqlalchemy.Engine) -> None:
    """Fix pysqlite, Cf.:
    `<http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl>`_
    """

    @sqlalchemy.event.listens_for(engine, "connect")
    def do_connect(  #  type: ignore [no-untyped-def]
        dbapi_connection,  # noqa: ANN001 - types are not exposed by sqlalchemy
        _connection_record,  # noqa: ANN001 - types are not exposed by sqlalchemy
    ) -> None:
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    @sqlalchemy.event.listens_for(engine, "begin")
    def do_begin(conn: sqlalchemy.Connection) -> None:
        # emit our own BEGIN
        conn.execute(sqlalchemy.text("BEGIN"))


def normalize_year(year_repr: str) -> int | None:
    """Convert a possible two-digit year into a four-digit year"""

    if year_repr == "":
        return None

    year = int(year_repr)
    current_year = date.today().year
    current_century = int(current_year / 100)
    if year < (current_year % 100):
        year += 100 * current_century
    elif year < 100:
        year += 100 * (current_century - 1)

    return year


T = TypeVar("T")


def disjoin(lst: list[T], key: Callable[[T], Any]) -> None:
    """Disjoin similar elements of a list by reordering the list in a deterministic way."""
    if len(lst) <= 2:
        return

    for _ in range(2):
        for idx in reversed(range(len(lst) - 1)):
            if key(lst[idx]) == key(lst[idx + 1]):
                # found collision
                try:
                    idx2 = next(idx2 for idx2 in reversed(range(idx)) if key(lst[idx]) != key(lst[idx2]))
                    # move
                    lst.insert(idx, lst.pop(idx2))
                except StopIteration:
                    # nothing to move
                    continue
        lst.reverse()
