import datetime
import io
from importlib.resources import files
from pathlib import Path

import pytest

from holper import model, sportsoftware

from . import SportSoftware


class TestIndividual:
    def test_recognize_file_format(self, subtests):
        for idx in range(1, 3):
            with subtests.test(idx=idx), (files(SportSoftware) / f"OE_11.0_EntryList{idx}.csv").open("rb") as file:
                assert sportsoftware.detect(file)
                assert not file.closed

    def test_read_oe_entries(self):
        with Path("tests/SportSoftware/OE_11.0_EntryList1.csv").open("rb") as file:
            generator = sportsoftware.read(file)
            entries = list(generator)
            for entry in entries:
                assert isinstance(entry, model.Entry)
                assert len(entry.competitors) == 1

            person = entries[0].competitors[0].person
            assert person.given_name == "Martin"
            assert person.family_name == "Ahlburg"
            assert person.birth_date.year == 1988

            start = entries[0].starts[0]
            assert start.time_offset + (start.category.time_offset or datetime.timedelta(0)) == datetime.timedelta(
                hours=1,
                minutes=36,
            )

    def test_write_oe_entries(self):
        event = model.Event(form=model.EventForm.INDIVIDUAL)
        race = model.Race(event=event)

        buffer = io.BytesIO()
        sportsoftware.write(buffer, race)

        buffer.seek(0)
        assert sportsoftware._detect_type(buffer) == "OE11"


class TestRelay:
    def test_recognize_file_format(self, subtests):
        for idx in range(1, 4):
            with subtests.test(idx=idx), (files(SportSoftware) / f"OS_11.0_EntryList{idx}.csv").open("rb") as file:
                assert sportsoftware.detect(file)
                assert not file.closed

    def test_read_os_entries(self):
        with Path("tests/SportSoftware/OS_11.0_EntryList1.csv").open("rb") as file:
            generator = sportsoftware.read(file)
            entries = list(generator)
            for entry in entries:
                assert isinstance(entry, model.Entry)

            assert len(entries[0].competitors) == 3
            assert entries[0].competitors[0].starts[0].control_card.label == "850705"

            assert (
                entries[0].starts[0].result.start_time
                == entries[0].competitors[0].starts[0].competitor_result.start_time
            )
            assert entries[0].starts[0].result.time == sum(
                (entries[0].competitors[idx].starts[0].competitor_result.time for idx in range(3)),
                datetime.timedelta(),
            )
            for idx in (0, 1):
                assert (
                    entries[0].competitors[idx].starts[0].competitor_result.finish_time
                    == entries[0].competitors[idx + 1].starts[0].competitor_result.start_time
                )

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_write_os_entries(self):
        event = model.Event(form=model.EventForm.RELAY)
        race = model.Race(event=event)

        buffer = io.BytesIO()
        sportsoftware.write(buffer, race)

        buffer.seek(0)
        assert sportsoftware._detect_type(buffer) == "OS11"


class TestTeam:
    def test_recognize_file_format(self):
        with (files(SportSoftware) / "OT_10.2_EntryList.csv").open("rb") as file:
            assert sportsoftware.detect(file)
            assert not file.closed

    def test_read_ot_entries(self):
        with Path("tests/SportSoftware/OT_10.2_EntryList.csv").open("rb") as file:
            generator = sportsoftware.read(file)
            entries = list(generator)
            for entry in entries:
                assert isinstance(entry, model.Entry)

            assert len(entries[0].competitors) == 3

    def test_sportsoftware_ot_entries(self):
        event = model.Event(form=model.EventForm.TEAM)
        race = model.Race(event=event)

        buffer = io.BytesIO()
        sportsoftware.write(buffer, race)

        buffer.seek(0)
        assert sportsoftware._detect_type(buffer) == "OT10"
