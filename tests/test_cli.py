from importlib.resources import as_file, files
from tempfile import NamedTemporaryFile

import pytest
from typer.testing import CliRunner

from holper import cli

from . import events

runner = CliRunner()


@pytest.fixture()
def db_file_opt():
    with NamedTemporaryFile() as db_file:
        yield ("--db-file", db_file.name)


@pytest.fixture()
def cli_snapshot(db_file_opt, snapshot):
    def _cli_snapshot(*args, exit_code=0):
        result = runner.invoke(cli.app, [*db_file_opt, *args])
        assert result.exit_code == exit_code, f"Unexpected exit code. Output: \n{result.stdout}"
        assert result.stdout == snapshot
        return result

    return _cli_snapshot


def test_create_event(cli_snapshot):
    cli_snapshot("init")
    cli_snapshot("new-event", "event.test-name.1", "2024-02-29 10:00:00")
    cli_snapshot("events")


@pytest.mark.parametrize("event", files(events).iterdir())
def test_imports_and_startlist(event, cli_snapshot):
    with as_file(event) as event_dir:
        cli_snapshot("init")
        cli_snapshot("new-event", event.name, "2024-02-29 10:00:00")
        cli_snapshot("import-categories", "1", str(event_dir / "ClassList.xml"))
        cli_snapshot("import-courses", "-s", "1", str(event_dir / "CourseData.xml"))
        cli_snapshot("import-entries", "1", str(event_dir / "EntryList.xml"))

        cli_snapshot("events")
        cli_snapshot("event", "1")
        cli_snapshot("entries", "1")

        cli_snapshot("startlist", "1", "3", "--parallel-max", "6", "--greedy")
