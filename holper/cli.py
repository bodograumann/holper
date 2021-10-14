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
        event_list = [evt for (evt,) in session.execute(sqlalchemy.select(model.Event))]

        if not event_list:
            typer.echo("There are no existing events.")

        for evt in event_list:
            typer.echo(
                f"#{evt.event_id} "
                f"{evt.start_time} - {evt.end_time}: "
                f"{evt.name}, "
                f"{len(evt.races)} races, {len(evt.event_categories)} categories, {len(evt.entries)} entries"
            )


@app.command()
def event(event_id: int, db_file: str = db_file_opt):
    """Show details of an event"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            return

        typer.echo(f"Name: {evt.name}")
        typer.echo(f"Period: {evt.start_time} - {evt.end_time}")
        typer.echo(f"Form: {evt.form}")
        if evt.races:
            typer.echo(
                f"{len(evt.races)} Races: "
                + ", ".join(f"{race.first_start}" for race in evt.races)
            )
        else:
            typer.echo("No races yet")

        if evt.event_categories:
            typer.echo(
                f"{len(evt.event_categories)} Categories: "
                + ", ".join(category.short_name for category in evt.event_categories)
            )
        else:
            typer.echo("No categories yet")

        if evt.entries:
            typer.echo(f"{len(evt.entries)} Entries")
        else:
            typer.echo("No entries yet")


@app.command()
def new_event(name: str, date: datetime, db_file: str = db_file_opt):
    """Create a new single-race solo event"""
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    with core.open_session(f"sqlite:///{db_file}") as session:
        evt = model.Event(name=name, start_time=date, end_time=date + timedelta(days=1))
        race = model.Race(first_start=date)
        evt.races.append(race)

        session.add(evt)
        session.commit()

        typer.echo(
            f"A new event “{name}” was created successfully with number #{evt.event_id}."
        )


@app.command()
def import_categories(event_id: int, category_file: Path, db_file: str = db_file_opt):
    """Import event categories in IOF XML v3 format"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            return

        if evt.event_categories:
            typer.echo(f"Event #{event_id} already contains categories.")
            return

        with open(category_file) as stream:
            event_categories = list(iofxml3.read(stream))

        evt.event_categories.extend(event_categories)
        # Create race categories
        for race in evt.races:
            race.categories = [
                model.Category(event_category=event_category)
                for event_category in evt.event_categories
            ]

        session.commit()

        typer.echo(f"Imported {len(event_categories)} categories")


@app.command()
def import_courses(
    race_id: int,
    course_file: Path,
    short_category_name: bool = typer.Option(
        False, "-s", help="Use the short category name to match category assignments."
    ),
    db_file: str = db_file_opt,
):
    """Import race courses in IOF XML v3 format"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            return

        if race.courses:
            typer.echo(f"Race #{race_id} already contains courses.")
            return

        with open(course_file) as stream:
            _evt, race_update = list(iofxml3.read(stream))

        with session.no_autoflush:
            race.courses = race_update.courses
            race.controls = race_update.controls

            # Link courses with existing categories
            for update_category in race_update.categories:
                name = update_category.name
                try:
                    category = next(
                        category
                        for category in race.categories
                        if category.name == name
                        or short_category_name
                        and category.short_name == name
                    )
                except StopIteration:
                    typer.echo(f"Could not find category {name}.")
                    continue
                category.courses = update_category.courses

        session.commit()

        typer.echo(f"Imported {len(race.courses)} courses")


@app.command()
def import_entries(event_id: int, entry_file: Path, db_file: str = db_file_opt):
    """Import race entries in IOF XML v3 format"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            return

        if evt.entries:
            typer.echo(f"Event #{event_id} already contains entries.")
            return

        with open(entry_file) as stream:
            _, *entries = iofxml3.read(stream)

        with session.no_autoflush:
            for entry in entries:
                core.hydrate_country_by_ioc_code(session, entry.organisation)
                for competitor in entry.competitors:
                    core.hydrate_country_by_ioc_code(session, competitor.person)
                    core.hydrate_country_by_ioc_code(session, competitor.organisation)
                for request in entry.category_requests:
                    request.event_category = core.shadow_entity_by_xid(
                        session, request.event_category
                    )

            evt.entries = entries

        session.commit()

        typer.echo(f"Imported {len(entries)} entries")


if __name__ == "__main__":
    app()
