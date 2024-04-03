#!/usr/bin/env python
"""Command line interface to the holper tool"""

from datetime import datetime, timedelta
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Optional

import sqlalchemy
import typer
from xdg_base_dirs import xdg_data_home

from holper import core, iof, model, resources, sportsoftware, start

app = typer.Typer()

default_db = xdg_data_home() / "holper" / "data.sqlite"
cli_ctx = {
    "db_file": default_db,
}


def db_session() -> sqlalchemy.orm.Session:
    return core.open_session(f"sqlite:///{cli_ctx['db_file']}")


ImportFileOpt = Annotated[
    Path,
    typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True, allow_dash=True),
]
ExportFileOpt = Annotated[Path, typer.Argument(dir_okay=False, readable=True, allow_dash=True)]


@app.callback()
def main(*, db_file: Annotated[Path, typer.Option()] = default_db) -> None:
    cli_ctx["db_file"] = db_file


@app.command()
def init() -> None:
    """Initialize database with country data."""
    Path(cli_ctx["db_file"]).parent.mkdir(parents=True, exist_ok=True)

    with db_session() as session:
        session.execute(sqlalchemy.text((files(resources) / "Country.sql").read_text()))
        session.commit()

    typer.echo("Initialized hOLper database.")


@app.command()
def events() -> None:
    """Show list of all events"""
    with db_session() as session:
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
def event(event_id: int) -> None:
    """Show details of an event"""
    with db_session() as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            raise typer.Abort

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
                + ", ".join(category.short_name or category.name for category in evt.event_categories),
            )
        else:
            typer.echo("No categories yet")

        if evt.entries:
            typer.echo(f"{len(evt.entries)} Entries")
        else:
            typer.echo("No entries yet")


@app.command()
def new_event(name: str, date: datetime) -> None:
    """Create a new single-race solo event"""
    with db_session() as session:
        evt = model.Event(name=name, start_time=date, end_time=date + timedelta(days=1))
        race = model.Race(first_start=date)
        evt.races.append(race)

        session.add(evt)
        session.commit()

        typer.echo(f"A new event “{name}” was created successfully with number #{evt.event_id}.")


@app.command()
def import_categories(event_id: int, category_file: ImportFileOpt) -> None:
    """Import event categories in IOF XML v3 format"""
    with db_session() as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            raise typer.Abort

        if evt.event_categories:
            typer.echo(f"Event #{event_id} already contains categories.")
            raise typer.Abort

        xml_data = category_file.read_bytes()
        class_list = iof.ClassList.from_xml(xml_data)
        importer = iof.Importer(class_list, core.get_countries(session))
        event_categories = [importer.import_class(class_) for class_ in class_list.classes]

        evt.event_categories.extend(event_categories)
        # Create race categories
        for race in evt.races:
            race.categories = [model.Category(event_category=event_category) for event_category in evt.event_categories]

        session.commit()

        typer.echo(f"Imported {len(event_categories)} categories")


@app.command()
def courses(race_id: int) -> None:
    """Show courses for a race"""
    with db_session() as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            raise typer.Abort

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
    event_id: int,
    course_file: ImportFileOpt,
    *,
    short_category_name: Annotated[
        bool,
        typer.Option(
            "-s",
            help="Use the short category name to match category assignments.",
        ),
    ] = False,
) -> None:
    """Import event courses in IOF XML v3 format"""
    with db_session() as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            raise typer.Abort

        course_data = iof.CourseData.from_xml(course_file.read_bytes())
        importer = iof.Importer(course_data, core.get_countries(session))

        ordered_data = course_data.ordered_race_course_data
        if len(ordered_data) > len(evt.races):
            typer.echo("Import file contains course data for more races than exist in this event.")
            raise typer.Abort

        for race, race_course_data in zip(evt.races, ordered_data, strict=False):
            if race_course_data is None:
                typer.echo(f"No course data included for race #{race.race_id}. Skipping!")
                continue
            if race.courses:
                typer.echo(f"Race #{race.race_id} already contains courses. Skipping!")
                continue

            race.controls = [importer.import_control(control) for control in race_course_data.controls]
            race.courses = [importer.import_course(course, race.controls) for course in race_course_data.courses]

            # Link courses with existing categories
            for class_course_assignment in race_course_data.class_course_assignments:
                assignment = importer.import_class_course_assignment(
                    class_course_assignment,
                    race.courses,
                    race.categories,
                    use_short_category_name=short_category_name,
                )
                if assignment is not None:
                    session.add(assignment)

            session.commit()

            typer.echo(f"Imported {len(race.courses)} courses")


@app.command()
def entries(event_id: int) -> None:
    """Show all entries of an event"""
    with db_session() as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            raise typer.Abort

        for entry in evt.entries:
            person = entry.competitors[0].person
            typer.echo(
                f"{person.given_name} {person.family_name}: {entry.category_requests[0].event_category.short_name}",
            )


@app.command()
def import_entries(event_id: int, entry_file: ImportFileOpt) -> None:
    """Import race entries in IOF XML v3 format"""
    with db_session() as session:
        evt = core.get_event(session, event_id)
        if not evt:
            typer.echo("Event could not be found.")
            raise typer.Abort

        if evt.entries:
            typer.echo(f"Event #{event_id} already contains entries.")
            raise typer.Abort

        entry_list = iof.EntryList.from_xml(entry_file.read_bytes())
        importer = iof.Importer(entry_list, core.get_countries(session))

        with session.no_autoflush:
            if evt.form == model.EventForm.INDIVIDUAL:
                entries = [
                    importer.import_person_entry(entry, evt.event_categories) for entry in entry_list.person_entries
                ]
            else:
                entries = [importer.import_team_entry(entry, evt.event_categories) for entry in entry_list.team_entries]

            evt.entries = entries

        session.commit()

        typer.echo(f"Imported {len(entries)} entries")


@app.command()
def startlist(
    race_id: int,
    interval: int,
    parallel_max: Optional[int] = None,
    *,
    greedy: bool = False,
) -> None:
    """Assign start times for all starters"""
    with db_session() as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            raise typer.Abort

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
                f"Course {course_id} ({categories}):\n"
                f"{start_scheme[course_id].pretty()} {list(start_scheme[course_id])}",
            )

        stats = start.Statistics(race)
        typer.echo(f"Starter number: {stats.entries_total}")
        typer.echo(f"Last start: {stats.last_start}")
        typer.echo(f"Starters per start time: {stats.entries_per_slot_avg:.2f} ±{stats.entries_per_slot_var:.2f}")
        for count in sorted(stats.entries_per_slot):
            typer.echo(f"{count} parallel starters: {stats.entries_per_slot[count]} times")


@app.command()
def export(
    race_id: int,
    target: ExportFileOpt,
) -> None:
    """Export entries as SportSoftware csv file"""
    with db_session() as session:
        race = core.get_race(session, race_id)
        if not race:
            typer.echo("Race could not be found.")
            raise typer.Abort

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
def filter_unused_courses(file: typer.FileBinaryRead) -> None:
    original = file.read()
    course_data = iof.course_data.CourseData.from_xml(original)
    course_data.delete_unused_courses()
    typer.echo(
        course_data.to_xml(
            skip_empty=True,
            pretty_print=True,
            encoding="UTF-8",
            standalone=True,
        ),
    )


if __name__ == "__main__":
    app()
