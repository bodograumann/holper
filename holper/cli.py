#!/usr/bin/env python
"""Command line interface to the holper tool"""

from datetime import datetime, timedelta
from pathlib import Path

import sqlalchemy
import typer
from xdg import xdg_data_home

from holper import core, iof, iofxml3, model, sportsoftware, start

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
                f"{len(evt.races)} races, {len(evt.event_categories)} categories, {len(evt.entries)} entries",
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
            typer.echo(f"{len(evt.races)} Races: " + ", ".join(f"{race.first_start}" for race in evt.races))
        else:
            typer.echo("No races yet")

        if evt.event_categories:
            typer.echo(
                f"{len(evt.event_categories)} Categories: "
                + ", ".join(category.short_name for category in evt.event_categories),
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

        typer.echo(f"A new event “{name}” was created successfully with number #{evt.event_id}.")


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

        with category_file.open(encoding="utf-8") as stream:
            event_categories = list(iofxml3.read(stream))

        evt.event_categories.extend(event_categories)
        # Create race categories
        for race in evt.races:
            race.categories = [model.Category(event_category=event_category) for event_category in evt.event_categories]

        session.commit()

        typer.echo(f"Imported {len(event_categories)} categories")


@app.command()
def courses(race_id: int, db_file: str = db_file_opt):
    """Show courses for a race"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            return

        for course in race.courses:
            typer.echo(f"{course.name}: ", nl=False)
            typer.echo(
                sum(
                    (len(assignment.category.event_category.entry_requests) for assignment in course.categories),
                    0,
                ),
                nl=False,
            )
            typer.echo(
                " = "
                + " + ".join(
                    f"{len(cat.entry_requests)}·{cat.short_name}"
                    for cat in (assignment.category.event_category for assignment in course.categories)
                ),
            )

        courses_by_first_control = core.group_courses_by_first_control(race)

        typer.echo("\nFirst controls:")
        for control in sorted(courses_by_first_control):
            typer.echo(f"{control}: " + ", ".join(course.name for course in courses_by_first_control[control]))


@app.command()
def import_courses(
    race_id: int,
    course_file: Path,
    short_category_name: bool = typer.Option(
        False,
        "-s",
        help="Use the short category name to match category assignments.",
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

        with course_file.open(encoding="utf-8") as stream:
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
                        if category.name == name or short_category_name and category.short_name == name
                    )
                except StopIteration:
                    typer.echo(f"Could not find category {name}.")
                    continue
                category.courses = update_category.courses

        session.commit()

        typer.echo(f"Imported {len(race.courses)} courses")


@app.command()
def entries(event_id: int, db_file: str = db_file_opt):
    """Show all entries of an event"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            return

        for entry in evt.entries:
            person = entry.competitors[0].person
            typer.echo(
                f"{person.given_name} {person.family_name}: {entry.category_requests[0].event_category.short_name}",
            )


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

        with entry_file.open(encoding="utf-8") as stream:
            _, *entries = iofxml3.read(stream)

        with session.no_autoflush:
            for entry in entries:
                core.hydrate_country_by_ioc_code(session, entry.organisation)
                for competitor in entry.competitors:
                    core.hydrate_country_by_ioc_code(session, competitor.person)
                    core.hydrate_country_by_ioc_code(session, competitor.organisation)
                for request in entry.category_requests:
                    request.event_category = core.shadow_entity_by_xid(session, request.event_category)

            evt.entries = entries

        session.commit()

        typer.echo(f"Imported {len(entries)} entries")


@app.command()
def startlist(
    race_id: int,
    interval: int,
    parallel_max: int | None = None,
    greedy: bool = False,
    db_file: str = db_file_opt,
):
    """Assign start times for all starters"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            return

        # generate starts in race
        for category in race.categories:
            for request in category.event_category.entry_requests:
                entry_start = model.Start(
                    category=category,
                    entry=request.entry,
                    competitive=True,
                )
                session.add(entry_start)

                for competitor in request.entry.competitors:
                    name = f"{competitor.person.given_name} {competitor.person.family_name}"
                    competitor_start = model.CompetitorStart(
                        start=entry_start,
                        competitor=competitor,
                    )
                    session.add(competitor_start)
                    if competitor.control_cards:
                        competitor_start.control_card = competitor.control_cards[0]
                    else:
                        typer.echo(
                            f"Competitor {name} has not provided a control card",
                        )

        courses_by_first_control = core.group_courses_by_first_control(race)
        constraints = start.StartConstraints(
            interval=interval,
            parallel_max=parallel_max,
            conflicts=[
                [course.course_id for course in course_group] for course_group in courses_by_first_control.values()
            ],
        )
        constraints.add_race_courses(race)

        if greedy:
            start_scheme = start.generate_slots_greedily(constraints)
        else:
            typer.echo("Finding optimal start list. This can take some time...")
            start_scheme = start.generate_slots_optimal(constraints, 60)

        start_slots = {course_id: iter(seq) for course_id, seq in start_scheme.items()}
        start.fill_slots(race, constraints, start_slots)

        session.commit()

        for course_id in sorted(start_scheme):
            course = next(course for course in race.courses if course.course_id == course_id)
            categories = ", ".join(category.short_name for category in constraints.get_categories(course))
            typer.echo(
                f"Course {course_id} ({categories}):\n  {start_scheme[course_id].pretty()} {list(start_scheme[course_id])}",
            )

        stats = start.statistics(race)
        typer.echo(f"Starter number: {stats['entries_total']}")
        typer.echo(f"Last start: {stats['last_start']}")
        typer.echo(f"Starters per start time: {stats['entries_per_slot_avg']:.2f} ±{stats['entries_per_slot_var']:.2f}")
        for count in sorted(stats["entries_per_slot"]):
            typer.echo(f"{count} parallel starters: {stats['entries_per_slot'][count]} times")


@app.command()
def export(
    race_id: int,
    target: Path,
    db_file: str = db_file_opt,
):
    """Export entries as SportSoftware csv file"""
    with core.open_session(f"sqlite:///{db_file}") as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            return

        # Make sure clubs have ids
        club_id = 1
        for entry in race.entries:
            if entry.organisation is not None and not any(
                external_id.issuer == "SportSoftware" for external_id in entry.organisation.external_ids
            ):
                entry.organisation.external_ids.append(
                    model.OrganisationXID(external_id=club_id, issuer="SportSoftware"),
                )
                club_id += 1

        with target.open("wb") as output_file:
            sportsoftware.write(output_file, race)


@app.command()
def filter_unused_courses(file: typer.FileBinaryRead):
    original = file.read()
    course_data = iof.CourseData.from_xml(original)
    course_data.race_course_data.delete_unused_courses()
    typer.echo(
        course_data.to_xml(
            skip_empty=True,
            pretty_print=True,
            encoding="UTF-8",
            standalone=True,
        ).decode("UTF-8"),
    )


if __name__ == "__main__":
    app()
