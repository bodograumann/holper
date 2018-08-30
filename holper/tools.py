"""Miscellaneous helper functions"""

# Taken from http://stackoverflow.com/a/1176023
def camelcase_to_snakecase(name_camel):
    import re
    name_tmp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name_camel)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name_tmp).lower()

def fix_sqlite_engine(engine):
    import sqlalchemy
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
        conn.execute('BEGIN')
    ###

def normalize_year(year):
    """Convert a possible two-digit year into a four-digit year"""
    from datetime import date

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
