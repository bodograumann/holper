"""Core functionality"""

import sqlalchemy
from . import tools, model


def open_session(source):
    engine = sqlalchemy.create_engine(source, echo=False)
    if source.startswith("sqlite:"):
        tools.fix_sqlite_engine(engine)
    model.Base.metadata.create_all(engine)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()
