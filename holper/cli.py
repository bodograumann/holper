#!/usr/bin/env python
"""Command line interface to the holper tool"""

from datetime import datetime, timedelta
from pathlib import Path

import sqlalchemy
import typer
from xdg import xdg_data_home

from holper import core, model, iofxml3

app = typer.Typer()

# Note: This yields pathlib.Path objects, so we should
# use typing.Union[str, pathlib.Path] as type. Union
# types are currently not supported by typer however.
db_file_opt = typer.Option(xdg_data_home() / "holper" / "data.sqlite")


@app.command()
def events(db_file: str = db_file_opt):
    """Show list of all events"""
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    with core.open_session(f"sqlite:///{db_file}") as session:
        event_list = [
            event for (event,) in session.execute(sqlalchemy.select(model.Event))
        ]

        if not event_list:
            typer.echo("There are no existing events.")

        for event in event_list:
            typer.echo(
                f"#{event.event_id} "
                f"{event.start_time} - {event.end_time}: "
                f"{event.name}, "
                f"{len(event.races)} races, {len(event.categories)} categories, {len(event.entries)} entries"
            )


@app.command()
def new_event(name: str, date: datetime, db_file: str = db_file_opt):
    """Create a new single-race solo event"""
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    with core.open_session(f"sqlite:///{db_file}") as session:
        event = model.Event(
            name=name, start_time=date, end_time=date + timedelta(days=1)
        )
        race = model.Race(first_start=date)
        event.races.append(race)

        session.add(event)
        session.commit()

        typer.echo(
            f"A new event “{name}” was created successfully with number #{event.event_id}."
        )


@app.command()
def import_categories(event_id: int, category_file: Path, db_file: str = db_file_opt):
    """Import event categories in IOF XML v3 format"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        try:
            (event,) = next(
                session.execute(
                    sqlalchemy.select(model.Event).where(
                        model.Event.event_id == event_id
                    )
                )
            )
        except StopIteration:
            typer.echo("Event could not be found.")
            return

        if event.categories:
            typer.echo(f"Event #{event_id} already contains categories.")
            return

        with open(category_file) as stream:
            categories = list(iofxml3.read(stream))
        event.categories.extend(categories)
        session.commit()

        typer.echo(f"Imported {len(categories)} categories")


if __name__ == "__main__":
    app()
