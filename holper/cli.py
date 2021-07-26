"""Command line interface to the holper tool"""

from datetime import datetime, timedelta
import sqlalchemy
import typer

from holper import core, model

app = typer.Typer()


@app.command()
def events(file: str):
    session = core.open_session("sqlite:///" + file)

    for (event,) in session.execute(sqlalchemy.select(model.Event)):
        print(
            f"{event.start_time} - {event.end_time}: "
            f"{event.name}, {len(event.races)} races, {len(event.categories)} categories, {len(event.entries)} entries"
        )

    session.close()


@app.command()
def new_event(file: str, name: str, date: datetime):
    """Create a new single-race solo event"""
    session = core.open_session("sqlite:///" + file)
    event = model.Event(name=name, start_time=date, end_time=date + timedelta(days=1))
    race = model.Race(first_start=date)
    event.races.append(race)

    print(event)

    session.add(event)
    session.commit()

    session.close()


if __name__ == "__main__":
    app()
