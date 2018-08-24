"""Data exchange in Krämer SportSoftware OE/OS/OT csv"""

from io import TextIOWrapper
from contextlib import contextmanager
from datetime import date

from . import model

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
    raise NotImplementedError

def write(output_file, entries):
    raise NotImplementedError

def read_solo_v11(input_file, with_seconds = False):
    """Read a SportSoftware OE2010 csv export file"""
    with _wrap_binary_stream(input_file) as csvfile:
        solo_reader = csv.reader(csvfile, delimiter = ';', doublequote = False)
        #skip header:
        next(solo_reader)

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
        # 52: Bahnnummer
        # 53: Bahn
        # 54: km
        # 55: Hm
        # 56: Bahn Posten

        clubs = {}
        categories = {}
        courses = {}
        for (row_nr, row) in enumerate(solo_reader):
            team = model.Team()

            try:
                team.number = int(row[1])
            except ValueError:
                pass

            person = model.Person(
                family_name=row[5],
                given_name=row[6],
                birth_date=date(year=int(row[7])) if row[7] else None,
                sex=model.Sex(row[8])
                )

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
                try:
                    club = clubs[int(row[18])]
                except KeyError:
                    club = model.Organisation(
                            name=row[19] + ' ' + row[20],
                            short_name=row[19],
                            type=model.OrganisationType.CLUB
                            )
                    if len(row[21]) == 2:
                        club.country = model.Country(iso_alpha_2=row[21])
                    elif len(row[21]) == 3:
                        club.country = model.Country(ioc_code=row[21])

                    clubs[int(row[18])] = club
                entry.organisation = club

            if row[24]:
                try:
                    category = categories[int(row[24])]
                except KeyError:
                    category = model.EventCategory(
                            name=row[26],
                            short_name=row[25],
                            status=model.EventCategoryStatus.NORMAL,
                            legs=model.Leg(leg_number=1),
                            sex=model.Sex.FEMALE if row[26].startswith('D') else model.Sex.MALE,
                            maxNumberOfTeamMembers=1
                            )
                    categories[int(row[24])] = category
                entry.categories.append(model.EntryCategoryRequest(category=category))

            #solo['fee'] = float(row[49].replace(',', '.') or 0)

            if row[52]:
                try:
                    course = courses[int(row[52])]
                except KeyError:
                    course = model.Course(
                            name=row[53],
                            length=float(row[54]),
                            climb=float(row[55])
                            )
                entry.course = course

            competitor = Competitor(entry=entry, person=person)
            if row[3]:
                competitor.control_cards.append(model.ControlCard(
                    system=model.PunchingSystem.SportIdent,
                    label=row[3]
                    ))
            yield competitor


def read_relay_v11(input_file, with_seconds = False):
    """Read a SportSoftware OS2010 csv export file"""
    with _wrap_binary_stream(input_file) as csvfile:
        relay_reader = csv.reader(csvfile, delimiter = ';', doublequote = False)
        #skip header:
        next(relay_reader)
        for (row_nr, row) in enumerate(relay_reader):
            try:
                relay = {}
                relay['raw'] = row
                try:
                    relay['number'] = int(row[1])
                except ValueError:
                    relay['number'] = None

                relay['disqualified'] = int(row[8]) > 0

                relay['nc'] = row[5].upper() == 'X'
                relay['club'] = {
                        'id': int(row[13]),
                        'short': row[14],
                        'name': row[15],
                        'country': row[16]
                        }
                relay['name'] = ' '.join((relay['club']['short'], relay['club']['name'], row[3]))

                relay['category'] = {
                        'id': int(row[19]),
                        'short': row[20],
                        'name': row[21]
                        }

                relay['fee'] = float(row[29].replace(',', '.') or 0)
                runner_count = int(row[22])
                relay['runners'] = []
                for runner in range(runner_count):
                    offset = 31 + runner * 14
                    relay['runners'].append({
                        'chip_id': int(row[offset+11]) if len(row[offset+11]) else None,
                        'family_name': row[offset+3],
                        'given_name': row[offset+4],
                        'birth_year': row[offset+5],
                    })

                relay['times'] = {
                        'start':   parse_time(row[6], with_seconds),
                        'finish':  parse_time(row[31 + runner_count * 14 - 6], with_seconds),
                        'adjust_plus': parse_time(row[11], with_seconds),
                        'adjust_minus': parse_time(row[10], with_seconds)
                }

                relay['times']['elapsed'] = calculate_elapsed_time(
                        compare_to=parse_time(row[7], with_seconds),
                        label=' '.join((
                            str(relay['number']),
                            relay['club']['short'],
                            relay['club']['name'],
                            relay['category']['short'],
                            relay['name']
                        )),
                        **relay['times']
                )

                yield relay
            except Exception as e:
                print("Error in entry #{}: {}".format(row_nr, str(e)))
                raise e

def read_team_v10(input_file):
    """Read a SportSoftware OT2003 csv export file"""
    with _wrap_binary_stream(input_file) as csvfile:
        team_reader = csv.reader(csvfile, delimiter = ';', doublequote = False)
        #skip header:
        next(team_reader)
        for (row_nr, row) in enumerate(team_reader):
            try:
                team = {}
                team['raw'] = row
                try:
                    team['number'] = int(row[0])
                except ValueError:
                    team['number'] = None
                team['name'] = row[1]
                team['nc'] = row[3].upper() == 'X'
                team['club'] = {
                        'id': int(row[8]),
                        'short': row[9],
                        'name': row[10],
                        'country': row[11]
                        }
                team['category'] = {
                        'id': int(row[12]),
                        'short': row[13],
                        'name': row[14]
                        }
                team['fee'] = float(row[22].replace(',', '.') or 0)
                team['runners'] = []
                for offset in range(24, len(row)-1, 7):
                    team['runners'].append((
                        int(row[offset+4]) if len(row[offset+4]) else None,
                        row[offset+1] + " " + row[offset]))

                yield team
            except Exception as e:
                print("Error in entry #{}: {}".format(row_nr, str(e)))
