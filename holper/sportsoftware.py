"""Data exchange in Krämer SportSoftware OE/OS/OT csv"""

from io import TextIOWrapper
from contextlib import contextmanager
from datetime import date
import csv

from . import model

def parse_float(string):
    if string:
        return float(string.replace(',', '.'))
    else:
        return None

def parse_sex(string):
    if string in ('W', 'D', 'F'):
        return model.Sex.FEMALE
    elif string in ('M', 'H'):
        return model.Sex.MALE
    else:
        return None

def detect(input_file):
	return bool(_detect_type(input_file))

@contextmanager
def _wrap_binary_stream(input_buffer):
    """Read the given stream with the correct format

    Usually when a `io.TextIOWrapper` is destroyed, the underlying stream is
    closed. We prevent this here, because we do not control the given stream.
    """
    wrapper = TextIOWrapper(input_buffer, encoding = 'latin1', newline = '')
    try:
        yield wrapper
    finally:
        wrapper.detach()
        del wrapper

def _detect_type(input_file):
    with _wrap_binary_stream(input_file) as input_stream:
        try:
            header = next(input_stream)
        except StopIteration:
            return None

        if header.startswith('OE0001;'):
            return 'OE11'
        elif header.startswith('OS0001'):
            return 'OS11'
        elif sum(1 for c in header if c == ';') == 58 and \
                header.startswith('Stnr;Mannschaft;'):
            return 'OT10'
        else:
            return None

def read(input_file):
    file_type = _detect_type(input_file)
    input_file.seek(0)

    event = model.Event()

    csv_reader = CSVReader(event)
    if file_type == 'OE11':
        yield from csv_reader.read_solo_v11(input_file)
    elif file_type == 'OS11':
        yield from csv_reader.read_relay_v11(input_file)
    elif file_type == 'OT10':
        yield from csv_reader.read_team_v10(input_file)
    else:
        raise NotImplementedError

def write(output_file, entries):
    raise NotImplementedError

class CSVReader:
    def __init__(self, event):
        self.event = event
        self.clubs = {}
        self.categories = {}
        self.courses = {}

    def read_solo_v11(self, input_file, with_seconds = False):
        """Read a SportSoftware OE2010 csv export file"""
        self.event.form = model.EventForm.INDIVIDUAL

        with _wrap_binary_stream(input_file) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter = ';', doublequote = False)
            #skip header:
            next(csv_reader)

            # Currently unmapped fields:
            # 0: OE0001
            # 2: XStnr
            # 4: Datenbank Id
            # 9: Block
            # 10: AK
            # 11: Start
            # 12: Ziel
            # 13: Zeit
            # 14: Wertung
            # 15: Gutschrift -
            # 16: Zuschlag +
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
            # 56: Bahn Posten

            for (row_nr, row) in enumerate(csv_reader):
                entry = model.Entry(event=self.event)

                try:
                    entry.number = int(row[1])
                except ValueError:
                    pass

                entry.competitors.append(self.read_competitor(*row[5:9], row[3]))

    #            solo['times'] = {
    #                    'start':   parse_time(row[11], with_seconds),
    #                    'finish':  parse_time(row[12], with_seconds),
    #                    'adjust_plus': parse_time(row[16], with_seconds),
    #                    'adjust_minus': parse_time(row[15], with_seconds)
    #            }
    #            solo['times']['elapsed'] = calculate_elapsed_time(
    #                    compare_to=parse_time(row[13], with_seconds),
    #                    label=solo['given_name'] + ' ' + solo['family_name'],
    #                    **solo['times']
    #            )

                # entry.result.disqualified = model.ResultStatus.DISQUALIFIED if int(row[14]) > 0 else model.ResultStatus.OK

                #entry.non_competitive = row[10].upper() == 'X'

                if row[18]:
                    entry.organisation = self.read_club(*row[18:24])

                if row[24]:
                    entry.category_requests.append(model.EntryCategoryRequest(category=self.read_category(*row[24:27])))

                #solo['fee'] = parse_float(row[49])

                if row[52]:
                    course_id = int(row[52])
                    try:
                        course = self.courses[course_id]
                    except KeyError:
                        course = model.Course(
                                name=row[53],
                                length=parse_float(row[54]),
                                climb=parse_float(row[55])
                                )
                        self.courses[course_id] = course
                    entry.course = course

                yield entry

    def read_relay_v11(self, input_file, with_seconds = False):
        """Read a SportSoftware OS2010 csv export file"""
        self.event.form = model.EventForm.RELAY

        with _wrap_binary_stream(input_file) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter = ';', doublequote = False)
            #skip header:
            next(csv_reader)
            for (row_nr, row) in enumerate(csv_reader):
                entry = model.Entry(event=self.event)

                try:
                    entry.number = int(row[1])
                except ValueError:
                    pass

                #relay['disqualified'] = int(row[8]) > 0
                #relay['nc'] = row[5].upper() == 'X'

                if row[13]:
                    entry.organisation = self.read_club(*row[13:19])

                    entry.name = ' '.join((entry.organisation.name, row[3]))

                entry.category_requests.append(self.read_category(*row[19:23]))

                #relay['fee'] = parse_float(row[29]) or 0)

                for competitor_nr in range(entry.category_requests[0].maxNumberOfTeamMembers):
                    offset = 31 + competitor_nr * 14
                    entry.competitors.append(self.read_competitor(*row[offset+3:offset+7], row[offset+11]))

                #relay['times'] = {
                #        'start':   parse_time(row[6], with_seconds),
                #        'finish':  parse_time(row[31 + runner_count * 14 - 6], with_seconds),
                #        'adjust_plus': parse_time(row[11], with_seconds),
                #        'adjust_minus': parse_time(row[10], with_seconds)
                #}

                #relay['times']['elapsed'] = calculate_elapsed_time(
                #        compare_to=parse_time(row[7], with_seconds),
                #        label=' '.join((
                #            str(relay['number']),
                #            relay['club']['short'],
                #            relay['club']['name'],
                #            relay['category']['short'],
                #            relay['name']
                #        )),
                #        **relay['times']
                #)

                yield entry

    def read_team_v10(self, input_file):
        """Read a SportSoftware OT2003 csv export file"""
        self.event.form = model.EventForm.TEAM

        with _wrap_binary_stream(input_file) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter = ';', doublequote = False)
            #skip header:
            next(csv_reader)
            for (row_nr, row) in enumerate(csv_reader):
                entry = model.Entry(event=self.event)

                try:
                    entry.number = int(row[1])
                except ValueError:
                    pass

                entry.name = row[1]
                #team['nc'] = row[3].upper() == 'X'
                if row[8]:
                    entry.organisation = self.read_club(*row[8:12])

                entry.category_requests.append(self.read_category(*row[12:16]))

                #team['fee'] = parse_float(row[22].replace(',', '.') or 0)

                for competitor_nr in range(entry.category_requests[0].maxNumberOfTeamMembers):
                    offset = 24 + competitor_nr * 7
                    entry.competitors.append(self.read_competitor(*row[offset:offset+5]))

                yield entry

    def read_club(self, club_id, abbreviation, city, country, seat=None, region=None):
        club_id = int(club_id)
        try:
            return self.clubs[club_id]
        except KeyError:
            club = model.Organisation(
                    name=abbreviation + ' ' + city,
                    short_name=abbreviation,
                    type=model.OrganisationType.CLUB
                    )
            if len(country) == 2:
                club.country = model.Country(iso_alpha_2=country)
            elif len(country) == 3:
                club.country = model.Country(ioc_code=country)

            self.clubs[club_id] = club
            return club

    def read_category(self, category_id, short_name, name, team_size=1):
        category_id = int(category_id)
        team_size = int(team_size)
        try:
            return self.categories[category_id]
        except KeyError:
            category = model.EventCategory(
                    event=self.event,
                    name=name,
                    short_name=short_name,
                    status=model.EventCategoryStatus.NORMAL,
                    sex=parse_sex(short_name[0]),
                    maxNumberOfTeamMembers=team_size
                    )
            for leg_number in range(1, team_size+1):
                category.legs.append(model.Leg(leg_number=leg_number))

            self.categories[category_id] = category
            return category

    def read_competitor(self, family_name, given_name, birth_year, sex, control_card_label):
        person = model.Person(
                family_name=family_name,
                given_name=given_name,
                birth_date=date(year=int(birth_year), month=1, day=1) if birth_year else None,
                sex=parse_sex(sex)
                )
        competitor = model.Competitor(person=person)
        if control_card_label:
            competitor.control_cards.append(model.ControlCard(
                system=model.PunchingSystem.SportIdent,
                label=control_card_label
                ))
        return competitor
