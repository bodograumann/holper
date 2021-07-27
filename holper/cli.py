#!/usr/bin/env python
"""Command line interface to the holper tool"""

from datetime import datetime, timedelta
from pathlib import Path

import sqlalchemy
import typer
from xdg import xdg_data_home

from holper import core, model

app = typer.Typer()

# Note: This yields pathlib.Path objects, so we should
# use typing.Union[str, pathlib.Path] as type. Union
# types are currently not supported by typer however.
db_file_opt = typer.Option(xdg_data_home() / "holper" / "data.sqlite")


@app.command()
def events(file: str = db_file_opt):
    """Show list of all events"""
    Path(file).parent.mkdir(parents=True, exist_ok=True)
    session = core.open_session(f"sqlite:///{file}")

    for (event,) in session.execute(sqlalchemy.select(model.Event)):
        print(
            f"{event.start_time} - {event.end_time}: "
            f"{event.name}, {len(event.races)} races, {len(event.categories)} categories, {len(event.entries)} entries"
        )

    session.close()


@app.command()
def new_event(name: str, date: datetime, file: str = db_file_opt):
    """Create a new single-race solo event"""
    Path(file).parent.mkdir(parents=True, exist_ok=True)
    session = core.open_session(f"sqlite:///{file}")
    event = model.Event(name=name, start_time=date, end_time=date + timedelta(days=1))
    race = model.Race(first_start=date)
    event.races.append(race)

    print(event)

    session.add(event)
    session.commit()

    session.close()


if __name__ == "__main__":
    app()
