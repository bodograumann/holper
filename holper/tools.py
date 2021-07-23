"""Miscellaneous helper functions"""
from datetime import date
import re
import sqlalchemy

# Taken from http://stackoverflow.com/a/1176023
def camelcase_to_snakecase(name_camel):
    name_tmp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name_camel)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name_tmp).lower()


def fix_sqlite_engine(engine):
    ### Fix pysqlite
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
    @sqlalchemy.event.listens_for(engine, 'connect')
    def do_connect(dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    @sqlalchemy.event.listens_for(engine, 'begin')
    def do_begin(conn):
        # emit our own BEGIN
        conn.execute(sqlalchemy.text('BEGIN'))

    ###


def normalize_year(year):
    """Convert a possible two-digit year into a four-digit year"""

    if year == '':
        return None

    year = int(year)
    current_year = date.today().year
    current_century = int(current_year / 100)
    if year < (current_year % 100):
        year += 100 * current_century
    elif year < 100:
        year += 100 * (current_century - 1)

    return year


def disjoin(lst, key):
    """Disjoin similar elements of a list by reordering the list in a deterministic way."""
    if len(lst) <= 2:
        return

    for _ in range(2):
        for idx in reversed(range(len(lst) - 1)):
            if key(lst[idx]) == key(lst[idx + 1]):
                # found collision
                for idx2 in reversed(range(0, idx)):
                    if key(lst[idx]) != key(lst[idx2]):
                        break
                else:
                    # nothing to move
                    continue
                # move
                lst.insert(idx, lst.pop(idx2))
        lst.reverse()
