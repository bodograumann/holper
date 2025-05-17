"""Data exchange in Krämer SportSoftware OE/OS/OT csv"""

import csv
from collections.abc import Generator
from contextlib import contextmanager, suppress
from datetime import MINYEAR, date, datetime, timedelta
from io import TextIOWrapper
from typing import IO

from . import model, tools

_csv_header_oe_de = (
    "OE0001",
    "Stnr",
    "XStnr",
    "Chipnr",
    "Datenbank Id",
    "Nachname",
    "Vorname",
    "Jg",
    "G",
    "Block",
    "AK",
    "Start",
    "Ziel",
    "Zeit",
    "Wertung",
    "Gutschrift -",
    "Zuschlag +",
    "Kommentar",
    "Club-Nr.",
    "Abk",
    "Ort",
    "Nat",
    "Sitz",
    "Region",
    "Katnr",
    "Kurz",
    "Lang",
    "MeldeKat. Nr",
    "MeldeKat. (kurz)",
    "MeldeKat. (lang)",
    "Rang",
    "Ranglistenpunkte",
    "Num1",
    "Num2",
    "Num3",
    "Text1",
    "Text2",
    "Text3",
    "Adr. Nachname",
    "Adr. Vorname",
    "Straße",
    "Zeile2",
    "PLZ",
    "Adr. Ort",
    "Tel",
    "Mobil",
    "Fax",
    "EMail",
    "Gemietet",
    "Startgeld",
    "Bezahlt",
    "Mannschaft",
    "Bahnnummer",
    "Bahn",
    "km",
    "Hm",
    "Bahn Posten",
    "Platz",
)
_csv_header_os_de = (
    "OS0012",
    "Stnr",
    "Melde Id",
    "Bez",
    "Block",
    "AK",
    "Start",
    "Zeit",
    "Wertung",
    "Pl",
    "Gutschrift -",
    "Zuschlag +",
    "Kommentar",
    "Club-Nr.",
    "Abk",
    "Ort",
    "Nat",
    "Sitz",
    "Region",
    "Katnr",
    "Kurz",
    "Lang",
    "Läufer",
    "Num1",
    "Num2",
    "Num3",
    "Text1",
    "Text2",
    "Text3",
    "Startgeld",
    "Bezahlt",
    "Xtra1",
    "Lnr1",
    "Xtranr1",
    "Nachname1",
    "Vorname1",
    "Jg1",
    "G1",
    "Start1",
    "Ziel1",
    "Zeit1",
    "Wertung1",
    "Chipnr1",
    "Gemietet1",
    "Datenbank Id1",
    "Xtra2",
    "Lnr2",
    "Xtranr2",
    "Nachname2",
    "Vorname2",
    "Jg2",
    "G2",
    "Start2",
    "Ziel2",
    "Zeit2",
    "Wertung2",
    "Chipnr2",
    "Gemietet2",
    "Datenbank Id2",
    "Xtra3",
    "Lnr3",
    "Xtranr3",
    "Nachname3",
    "Vorname3",
    "Jg3",
    "G3",
    "Start3",
    "Ziel3",
    "Zeit3",
    "Wertung3",
    "Chipnr3",
    "Gemietet3",
    "Datenbank Id3",
    "Xtra4",
    "Lnr4",
    "Xtranr4",
    "Nachname4",
    "Vorname4",
    "Jg4",
    "G4",
    "Start4",
    "Ziel4",
    "Zeit4",
    "Wertung4",
    "Chipnr4",
    "Gemietet4",
    "Datenbank Id4",
    "Xtra5",
    "Lnr5",
    "Xtranr5",
    "Nachname5",
    "Vorname5",
    "Jg5",
    "G5",
    "Start5",
    "Ziel5",
    "Zeit5",
    "Wertung5",
    "Chipnr5",
    "Gemietet5",
    "Datenbank Id5",
    "Xtra6",
    "Lnr6",
    "Xtranr6",
    "Nachname6",
    "Vorname6",
    "Jg6",
    "G6",
    "Start6",
    "Ziel6",
    "Zeit6",
    "Wertung6",
    "Chipnr6",
    "Gemietet6",
    "Datenbank Id6",
    "Xtra7",
    "Lnr7",
    "Xtranr7",
    "Nachname7",
    "Vorname7",
    "Jg7",
    "G7",
    "Start7",
    "Ziel7",
    "Zeit7",
    "Wertung7",
    "Chipnr7",
    "Gemietet7",
    "Datenbank Id7",
    "Xtra8",
    "Lnr8",
    "Xtranr8",
    "Nachname8",
    "Vorname8",
    "Jg8",
    "G8",
    "Start8",
    "Ziel8",
    "Zeit8",
    "Wertung8",
    "Chipnr8",
    "Gemietet8",
    "Datenbank Id8",
    "Xtra9",
    "Lnr9",
    "Xtranr9",
    "Nachname9",
    "Vorname9",
    "Jg9",
    "G9",
    "Start9",
    "Ziel9",
    "Zeit9",
    "Wertung9",
    "Chipnr9",
    "Gemietet9",
    "Datenbank Id9",
    "Xtra10",
    "Lnr10",
    "Xtranr10",
    "Nachname10",
    "Vorname10",
    "Jg10",
    "G10",
    "Start10",
    "Ziel10",
    "Zeit10",
    "Wertung10",
    "Chipnr10",
    "Gemietet10",
    "Datenbank Id10",
    "Xtra11",
    "Lnr11",
    "Xtranr11",
    "Nachname11",
    "Vorname11",
    "Jg11",
    "G11",
    "Start11",
    "Ziel11",
    "Zeit11",
    "Wertung11",
    "Chipnr11",
    "Gemietet11",
    "Datenbank Id11",
    "Xtra12",
    "Lnr12",
    "Xtranr12",
    "Nachname12",
    "Vorname12",
    "Jg12",
    "G12",
    "Start12",
    "Ziel12",
    "Zeit12",
    "Wertung12",
    "Chipnr12",
    "Gemietet12",
    "Datenbank Id12",
    "Xtra13",
    "Lnr13",
    "Xtranr13",
    "Nachname13",
    "Vorname13",
    "Jg13",
    "G13",
    "Start13",
    "Ziel13",
    "Zeit13",
    "Wertung13",
    "Chipnr13",
    "Gemietet13",
    "Datenbank Id13",
    "Xtra14",
    "Lnr14",
    "Xtranr14",
    "Nachname14",
    "Vorname14",
    "Jg14",
    "G14",
    "Start14",
    "Ziel14",
    "Zeit14",
    "Wertung14",
    "Chipnr14",
    "Gemietet14",
    "Datenbank Id14",
    "Xtra15",
    "Lnr15",
    "Xtranr15",
    "Nachname15",
    "Vorname15",
    "Jg15",
    "G15",
    "Start15",
    "Ziel15",
    "Zeit15",
    "Wertung15",
    "Chipnr15",
    "Gemietet15",
    "Datenbank Id15",
    "Xtra16",
    "Lnr16",
    "Xtranr16",
    "Nachname16",
    "Vorname16",
    "Jg16",
    "G16",
    "Start16",
    "Ziel16",
    "Zeit16",
    "Wertung16",
    "Chipnr16",
    "Gemietet16",
    "Datenbank Id16",
    "Xtra17",
    "Lnr17",
    "Xtranr17",
    "Nachname17",
    "Vorname17",
    "Jg17",
    "G17",
    "Start17",
    "Ziel17",
    "Zeit17",
    "Wertung17",
    "Chipnr17",
    "Gemietet17",
    "Datenbank Id17",
    "Xtra18",
    "Lnr18",
    "Xtranr18",
    "Nachname18",
    "Vorname18",
    "Jg18",
    "G18",
    "Start18",
    "Ziel18",
    "Zeit18",
    "Wertung18",
    "Chipnr18",
    "Gemietet18",
    "Datenbank Id18",
    "Xtra19",
    "Lnr19",
    "Xtranr19",
    "Nachname19",
    "Vorname19",
    "Jg19",
    "G19",
    "Start19",
    "Ziel19",
    "Zeit19",
    "Wertung19",
    "Chipnr19",
    "Gemietet19",
    "Datenbank Id19",
    "Xtra20",
    "Lnr20",
    "Xtranr20",
    "Nachname20",
    "Vorname20",
    "Jg20",
    "G20",
    "Start20",
    "Ziel20",
    "Zeit20",
    "Wertung20",
    "Chipnr20",
    "Gemietet20",
    "Datenbank Id20",
    "Platz",
    "",
)
_csv_header_ot_de = (
    "Stnr",
    "Mannschaft",
    "Block",
    "AK",
    "Start",
    "Ziel",
    "Zeit",
    "Wertung",
    "Club-Nr.",
    "Abk",
    "Ort",
    "Nat",
    "Katnr",
    "Kurz",
    "Lang",
    "Läufer",
    "Num1",
    "Num2",
    "Num3",
    "Text1",
    "Text2",
    "Text3",
    "Startgeld",
    "Bezahlt",
    "Nachname",
    "Vorname",
    "Jg",
    "G",
    "SI-Karte",
    "Gemietet",
    "Datenbank Id",
    "Nachname",
    "Vorname",
    "Jg",
    "G",
    "SI-Karte",
    "Gemietet",
    "Datenbank Id",
    "Nachname",
    "Vorname",
    "Jg",
    "G",
    "SI-Karte",
    "Gemietet",
    "Datenbank Id",
    "Nachname",
    "Vorname",
    "Jg",
    "G",
    "SI-Karte",
    "Gemietet",
    "Datenbank Id",
    "Nachname",
    "Vorname",
    "Jg",
    "G",
    "SI-Karte",
    "Gemietet",
    "Datenbank Id",
)


def parse_float(string: str) -> float | None:
    if not string:
        return None
    return float(string.replace(",", "."))


def parse_sex(string: str) -> model.Sex | None:
    if string in ("W", "D", "F"):
        return model.Sex.FEMALE
    if string in ("M", "H"):
        return model.Sex.MALE
    return None


def parse_time(string: str, *, with_seconds: bool = True) -> timedelta | None:
    if string == "":
        return None
    values = list(map(int, string.split(":")))
    seconds = values.pop() if with_seconds else 0
    minutes = values.pop() if values else 0
    hours = values.pop() if values else 0
    return timedelta(seconds=seconds, minutes=minutes, hours=hours)


def format_time(value: timedelta, *, with_seconds: bool = True) -> str:
    if value is None:
        return ""
    if value.microseconds:
        value = timedelta(seconds=value.total_seconds())
    string = str(value)
    if not with_seconds:
        string = string[:-3]
    return string


def detect(input_file: IO[bytes]) -> bool:
    return bool(_detect_type(input_file))


@contextmanager
def _wrap_binary_stream(io_buffer: IO[bytes], encoding: str = "latin1") -> Generator[TextIOWrapper]:
    """Access the given stream with the correct format

    Usually when a `io.TextIOWrapper` is destroyed, the underlying stream is
    closed. We prevent this here, because we do not control the given stream.
    """
    wrapper = TextIOWrapper(io_buffer, encoding=encoding, newline="")
    try:
        yield wrapper
    finally:
        wrapper.detach()
        del wrapper


def _detect_type(input_file: IO[bytes], encoding: str = "latin1") -> str | None:
    with _wrap_binary_stream(input_file, encoding=encoding) as input_stream:
        try:
            header = next(input_stream)
        except StopIteration:
            return None

        if header.startswith(("OE0001;", "OE0012;")):
            return "OE11"
        if header.startswith("OS0012;"):
            return "OS11"
        if sum(1 for c in header if c == ";") == 58 and header.startswith("Stnr;Mannschaft;"):
            return "OT10"
        return None


def read(input_file: IO[bytes], encoding: str = "latin1") -> Generator[model.Entry]:
    file_type = _detect_type(input_file, encoding=encoding)
    input_file.seek(0)

    event = model.Event()
    race = model.Race(event=event)

    csv_reader = CSVReader(race)
    if file_type == "OE11":
        yield from csv_reader.read_solo_v11(input_file, encoding=encoding)
    elif file_type == "OS11":
        yield from csv_reader.read_relay_v11(input_file, encoding=encoding)
    elif file_type == "OT10":
        yield from csv_reader.read_team_v10(input_file, encoding=encoding)
    else:
        raise NotImplementedError


def write(output_file: IO[bytes], race: model.Race, encoding: str = "latin1") -> None:
    csv_writer = CSVWriter(race)

    if race.event.form is model.EventForm.INDIVIDUAL:
        csv_writer.write_solo_v11(output_file, encoding=encoding)
    elif race.event.form is model.EventForm.RELAY:
        csv_writer.write_relay_v11(output_file, encoding=encoding)
    elif race.event.form is model.EventForm.TEAM:
        csv_writer.write_team_v10(output_file, encoding=encoding)
    else:
        msg = "Unsupported event form"
        raise ValueError(msg)


class CSVReader:
    def __init__(self, race: model.Race) -> None:
        self.race = race
        self.clubs: dict[int, model.Organisation] = {}
        self.categories: dict[int, model.Category] = {}
        self.courses: dict[int, model.Course] = {}

    def read_solo_v11(
        self,
        input_file: IO[bytes],
        *,
        with_seconds: bool = True,
        encoding: str = "latin1",
    ) -> Generator[model.Entry]:
        """Read a SportSoftware OE2010 csv export file"""
        self.race.event.form = model.EventForm.INDIVIDUAL

        with _wrap_binary_stream(input_file, encoding=encoding) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";", doublequote=False)
            # skip header:
            next(csv_reader, None)

            # Currently unmapped fields:
            # 0: OE0001
            # 2: XStnr
            # 4: Datenbank Id
            # 9: Block
            # 17: Kommentar
            # 22: Sitz
            # 23: Region
            # 27: MeldeKat. Nr
            # 28: MeldeKat. (kurz)
            # 29: MeldeKat. (lang)
            # 30: Rang
            # 31: Ranglistenpunkte
            # 32: Num1
            # 33: Num2
            # 34: Num3
            # 35: Text1
            # 36: Text2
            # 37: Text3
            # 38: Adr. Nachname
            # 39: Adr. Vorname
            # 40: Straße
            # 41: Zeile2
            # 42: PLZ
            # 43: Adr. Ort
            # 44: Tel
            # 45: Mobil
            # 46: Fax
            # 47: EMail
            # 48: Gemietet
            # 49: Startgeld
            # 50: Bezahlt
            # 51: Mannschaft

            for row in csv_reader:
                entry = model.Entry(event=self.race.event)

                with suppress(ValueError):
                    entry.number = int(row[1])

                entry.competitors.append(self.read_competitor(*(*row[5:9], row[3])))

                start = self.read_start_and_result(*row[10:17], with_seconds=with_seconds)
                start.entry = entry

                if start.result is not None and row[57]:
                    start.result.position = int(row[57])

                if row[18]:
                    entry.organisation = self.read_club(*row[18:24])

                if row[24]:
                    category = self.read_category(*row[24:27])
                    entry.category_requests.append(model.EntryCategoryRequest(event_category=category.event_category))
                    start.category = category

                # Note: we can only assing courses to categories
                if row[52] and start.category:
                    course_id = int(row[52])
                    try:
                        course = self.courses[course_id]
                    except KeyError:
                        course = model.Course(
                            name=row[53],
                            length=parse_float(row[54]),
                            climb=parse_float(row[55]),
                        )
                        self.courses[course_id] = course
                    # TODO: This fails: start.category.courses = [course]

                yield entry

    def read_relay_v11(
        self,
        input_file: IO[bytes],
        *,
        with_seconds: bool = True,
        encoding: str = "latin1",
    ) -> Generator[model.Entry]:
        """Read a SportSoftware OS2010 csv export file"""
        self.race.event.form = model.EventForm.RELAY

        with _wrap_binary_stream(input_file, encoding=encoding) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";", doublequote=False)
            # skip header:
            next(csv_reader, None)
            for row in csv_reader:
                entry = model.Entry(event=self.race.event)

                with suppress(ValueError):
                    entry.number = int(row[1])

                if row[13]:
                    entry.organisation = self.read_club(*row[13:19])

                    entry.name = row[3]

                category = self.read_category(*row[19:23])
                entry.category_requests.append(model.EntryCategoryRequest(event_category=category.event_category))

                # relay['fee'] = parse_float(row[29]) or 0)

                start = self.read_start_and_result(*(*row[5:7], "", *row[7:9], *row[10:12]), with_seconds=with_seconds)
                start.entry = entry
                start.category = category

                if start.result is not None and row[-2]:
                    start.result.position = int(row[-2])

                for competitor_nr in range(category.event_category.max_number_of_team_members):
                    offset = 31 + competitor_nr * 14
                    competitor = self.read_competitor(*(*row[offset + 3 : offset + 7], row[offset + 11]))
                    entry.competitors.append(competitor)

                    if row[offset + 7]:
                        competitor_start = model.CompetitorStart(
                            start=start,
                            competitor=competitor,
                            time_offset=parse_time(row[offset + 7], with_seconds=with_seconds),
                        )
                        if competitor.control_cards:
                            competitor_start.control_card = competitor.control_cards[0]

                    if any(row[offset + 8 : offset + 11]):
                        start_offset = parse_time(row[offset + 7], with_seconds=with_seconds)
                        finish_offset = parse_time(row[offset + 8], with_seconds=with_seconds)
                        competitor_start.competitor_result = model.CompetitorResult(
                            start_time=datetime(MINYEAR, 1, 1) + start_offset if start_offset else None,
                            finish_time=datetime(MINYEAR, 1, 1) + finish_offset if finish_offset else None,
                            time=parse_time(row[offset + 9], with_seconds=with_seconds),
                            status=self.read_result_status(row[offset + 10]),
                        )

                yield entry

    def read_team_v10(
        self,
        input_file: IO[bytes],
        *,
        with_seconds: bool = True,
        encoding: str = "latin1",
    ) -> Generator[model.Entry]:
        """Read a SportSoftware OT2003 csv export file"""
        self.race.event.form = model.EventForm.TEAM

        with _wrap_binary_stream(input_file, encoding=encoding) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";", doublequote=False)
            # skip header:
            next(csv_reader, None)
            for row in csv_reader:
                entry = model.Entry(event=self.race.event)

                with suppress(ValueError):
                    entry.number = int(row[0])

                entry.name = row[1]

                if row[8]:
                    entry.organisation = self.read_club(*row[8:12])

                category = self.read_category(*row[12:16])
                entry.category_requests.append(model.EntryCategoryRequest(event_category=category.event_category))

                start = self.read_start_and_result(*row[3:8], with_seconds=with_seconds)
                start.entry = entry
                start.category = category

                for competitor_nr in range(entry.category_requests[0].event_category.max_number_of_team_members):
                    offset = 24 + competitor_nr * 7
                    entry.competitors.append(self.read_competitor(*row[offset : offset + 5]))

                yield entry

    def read_club(
        self,
        club_id_repr: str,
        abbreviation: str,
        city: str,
        country: str,
        _seat: str | None = None,
        _region: str | None = None,
    ) -> model.Organisation:
        club_id = int(club_id_repr)
        try:
            return self.clubs[club_id]
        except KeyError:
            club = model.Organisation(
                name=(abbreviation + " " + city).strip(),
                short_name=abbreviation,
                type=model.OrganisationType.CLUB,
            )
            club.external_ids.append(
                model.OrganisationXID(organisation=club, issuer="SportSoftware", external_id=str(club_id)),
            )

            if len(country) == 2:
                club.country = model.Country(iso_alpha_2=country)
            elif len(country) == 3:
                club.country = model.Country(ioc_code=country)

            self.clubs[club_id] = club
            return club

    def read_category(
        self,
        category_id_repr: str,
        short_name: str,
        name: str,
        team_size_repr: str = "",
    ) -> model.Category:
        category_id = int(category_id_repr)
        team_size = int(team_size_repr) if team_size_repr else 1
        try:
            return self.categories[category_id]
        except KeyError:
            event_category = model.EventCategory(
                event=self.race.event,
                name=name,
                short_name=short_name,
                status=model.EventCategoryStatus.NORMAL,
                sex=parse_sex(short_name[0]),
                max_number_of_team_members=team_size,
            )
            event_category.external_ids.append(
                model.EventCategoryXID(
                    event_category=event_category,
                    issuer="SportSoftware",
                    external_id=str(category_id),
                ),
            )
            category = model.Category(race=self.race, event_category=event_category)
            for leg_number in range(1, team_size + 1):
                event_category.legs.append(model.Leg(leg_number=leg_number))

            self.categories[category_id] = category
            return category

    def read_competitor(
        self,
        family_name: str,
        given_name: str,
        birth_year_repr: str,
        sex: str,
        control_card_label: str,
    ) -> model.Competitor:
        birth_year = tools.normalize_year(birth_year_repr)

        person = model.Person(
            family_name=family_name,
            given_name=given_name,
            birth_date=date(year=birth_year, month=1, day=1) if birth_year else None,
            sex=parse_sex(sex),
        )
        competitor = model.Competitor(person=person)
        if control_card_label:
            competitor.control_cards.append(
                model.ControlCard(system=model.PunchingSystem.SPORT_IDENT, label=control_card_label),
            )
        return competitor

    def read_start_and_result(
        self,
        non_competitive: str,
        start_offset_repr: str,
        finish_offset_repr: str = "",
        result_time: str = "",
        status: str = "",
        time_bonus: str = "",
        time_penalty: str = "",
        *,
        with_seconds: bool = True,
    ) -> model.Start:
        """Read start and result columns

        Note: The export data only contains relative time values, while
        the model expects start and finish time to be proper `DateTime`
        values. As a work-around, here we store these as `DateTime`
        types, which still need to be shifted to the proper race start
        time.
        """
        start_offset = parse_time(start_offset_repr, with_seconds=with_seconds)
        start = model.Start(
            competitive=non_competitive.upper() != "X",
            time_offset=start_offset,
        )

        if finish_offset_repr or result_time or status:
            finish_offset = parse_time(finish_offset_repr, with_seconds=with_seconds)
            result = model.Result(
                start=start,
                start_time=datetime(MINYEAR, 1, 1) + start_offset if start_offset else None,
                finish_time=datetime(MINYEAR, 1, 1) + finish_offset if finish_offset else None,
                time_adjustment=(parse_time(time_penalty, with_seconds=with_seconds) or timedelta())
                - (parse_time(time_bonus, with_seconds=with_seconds) or timedelta()),
                time=parse_time(result_time, with_seconds=with_seconds),
            )

            if status:
                result.status = self.read_result_status(status)

        return start

    def read_result_status(self, status: str) -> model.ResultStatus:
        if int(status) == 0:
            return model.ResultStatus.OK
        if int(status) == 1:
            return model.ResultStatus.DID_NOT_START
        if int(status) == 2:
            return model.ResultStatus.DID_NOT_FINISH
        if int(status) == 3:
            return model.ResultStatus.MISSING_PUNCH
        if int(status) == 4:
            return model.ResultStatus.DISQUALIFIED
        if int(status) == 5:
            return model.ResultStatus.OVER_TIME
        msg = f"SportSoftware Wertung={status}"
        raise NotImplementedError(msg)


class CSVWriter:
    def __init__(self, race: model.Race) -> None:
        self.race = race

    def write_solo_v11(self, output_file: IO[bytes], encoding: str = "latin1") -> None:
        with _wrap_binary_stream(output_file, encoding=encoding) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=";", doublequote=False)

            csv_writer.writerow(_csv_header_oe_de)

            for entry in self.race.entries:
                row = [""] * len(_csv_header_oe_de)

                if entry.number:
                    row[1] = str(entry.number)

                *row[5:9], row[3] = self.write_competitor(entry.competitors[0])

                if entry.starts:
                    row[10:17] = self.write_start_and_result(entry.starts[0])[:7]

                if entry.organisation and entry.organisation.type == model.OrganisationType.CLUB:
                    row[18:24] = self.write_club(entry.organisation)[:6]

                if entry.category_requests:
                    row[24:27] = self.write_category(entry.category_requests[0].event_category)[:3]

                csv_writer.writerow(row)

    def write_relay_v11(self, output_file: IO[bytes], encoding: str = "latin1") -> None:
        raise NotImplementedError

    def write_team_v10(self, output_file: IO[bytes], encoding: str = "latin1") -> None:
        with _wrap_binary_stream(output_file, encoding=encoding) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=";", doublequote=False)

            csv_writer.writerow(_csv_header_ot_de)

            for entry in self.race.entries:
                row = [""] * len(_csv_header_ot_de)

                if entry.number:
                    row[0] = str(entry.number)
                row[1] = entry.name or ""

                try:
                    if entry.starts[0].time_offset is not None:
                        row[4] = self.write_start_and_result(entry.starts[0])[1]
                except IndexError:
                    pass

                if entry.organisation and entry.organisation.type == model.OrganisationType.CLUB:
                    row[8:12] = self.write_club(entry.organisation)[:4]

                if entry.category_requests:
                    row[12:16] = self.write_category(entry.category_requests[0].event_category)[:4]

                for competitor_nr, competitor in enumerate(entry.competitors):
                    offset = 24 + competitor_nr * 7
                    row[offset : offset + 5] = self.write_competitor(competitor)[:5]

                    # Only use the last two digits of the birth year
                    row[offset + 3] = row[offset + 3][-2:]

                csv_writer.writerow(row)

    def write_club(self, club: model.Organisation) -> list[str]:
        """Convert club to cells

        A club id and name is required.
        """
        return [
            next(external_id.external_id for external_id in club.external_ids if external_id.issuer == "SportSoftware"),
            club.short_name or "",
            (
                club.name[len(club.short_name) + 1 :]
                if club.short_name and club.name.startswith(club.short_name + " ")
                else club.name
            ),
            (club.country.ioc_code or "") if club.country else "",
            "",
            "",
        ]

    def write_category(self, category: model.EventCategory) -> list[str]:
        return [
            str(
                next(
                    (
                        external_id.external_id
                        for external_id in category.external_ids
                        if external_id.issuer == "SportSoftware"
                    ),
                    next(
                        (external_id.external_id for external_id in category.external_ids),
                        category.event_category_id,
                    ),
                ),
            ),
            category.short_name or category.name,
            category.name,
            str(category.max_number_of_team_members),
        ]

    def write_competitor(self, competitor: model.Competitor) -> list[str]:
        person = competitor.person
        competitor_row = [
            person.family_name or "",
            person.given_name or "",
            str(person.birth_date.year) if person.birth_date else "",
            "F" if person.sex is model.Sex.FEMALE else "M",
        ]
        if competitor.control_cards:
            competitor_row.append(competitor.control_cards[0].label or "")
        else:
            competitor_row.append("")
        return competitor_row

    def write_start_and_result(self, start: model.Start) -> list[str]:
        return [
            "" if start.competitive else "X",
            (
                format_time((start.category.time_offset or timedelta()) + start.time_offset)
                if start.time_offset is not None
                else ""
            ),
            "",
            "",
            "",
            "",
            "",
        ]
