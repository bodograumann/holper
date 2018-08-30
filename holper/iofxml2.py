"""Data exchange in IOF XML v2.0.3

Countries
---------

Version 2.0.3 only supports a subset of all countries by ID.
Furthermore there is *ROM*, which will be interpreted as *ROU* for Romania,
and *YOG*, which should have been *YUG*, but is now discarded anyway.

OrganisationIDs
---------------

For Clubs, in addition to an id type, an id manager may be specified.
This will regarded as type *idManager / type*.
"""

from contextlib import contextmanager
from collections import defaultdict
from pkg_resources import resource_stream

from lxml import etree

from . import model

_data_dtd = etree.DTD(resource_stream('holper.resources.IOF', 'IOFdata_2.0.3.dtd'))

_top_level_elements = ('PersonList', 'CompetitorList', 'RankList', 'ClubList', 'EventList', 'ServiceRequestList', 'EntryList', 'StartList', 'ResultList', 'ClassData', 'CourseData')


@contextmanager
def element_iterator(stream, events=['start']):
    def _iter(stream, parser):
        while True:
            line = stream.read(256)
            if line is None:
                return
            parser.feed(line)
            for event in parser.read_events():
                yield event

    parser = etree.XMLPullParser(events)
    try:
        yield _iter(stream, parser)
    finally:
        del parser


def detect_fast(input_file):
    with element_iterator(input_file) as iterator:
        try:
            _, first_element = next(iterator)
            _, second_element = next(iterator)
        except StopIteration:
            return False
        return (first_element.tag in _top_level_elements and
                second_element.tag == 'IOFVersion' and
                second_element.get('version') == '2.0.3')


def detect(input_file):
    try:
        document = etree.parse(input_file)
    except etree.ParseError:
        return False
    return _data_dtd.validate(document)


def read(input_file):
    tree = etree.parse(input_file)
    root = tree.getroot()

    if root.tag == 'EntryList':
        yield from _iterEntryList(root)
    else:
        raise NotImplementedError


def _iterEntryList(element):
    for child in element:
        if child.tag == 'IOFVersion':
            pass
        elif child.tag == 'ClubEntry':
            yield from _iterClubEntry(child)


def _readClub(element):
    obj = model.Organisation(type=model.OrganisationType.CLUB)

    for child in element:
        if child.tag == 'ClubId':
            obj.external_ids.append(_readClubID(child))
        elif child.tag == 'Name':
            obj.name = child.text
        elif child.tag == 'ShortName':
            obj.short_name = child.text
        elif child.tag in {'CountryId', 'Country'}:
            obj.country = _readCountry(child)
        else:
            # OrganisationId, CountryId|Country, Address, Tele, WebURL, Account, Contact, ModifyDate
            raise NotImplementedError(child.tag)

    return obj

def _iterClubEntry(element):
    for child in element:
        if child.tag in {'ClubId', 'Club'}:
            club = _readClub(child)
            yield club
        elif child.tag == 'Contact':
            raise NotImplementedError
        elif child.tag == 'Entry':
            entry = _readEntry(child)
            entry.club = club

def _readClubID(element):
    id_type = [value for value in map(element.get, ['idManager', 'type']) if value is not None]
    return model.OrganisationID(
            id_type='/'.join(id_type) if len(id_type) > 0 else None,
            external_id=element.text
            )

def _readCountry(element):
    country = model.Country()
    if element.tag == 'CountryID':
        country.ioc_code = _readIOCCode(element)
    else: # element.tag == 'Country':
        for child in element:
            if child.tag == 'CountryId':
                country.ioc_code = _readIOCCode(element)
            elif child.tag == 'Name':
                if country.ioc_code is None and country.name is None:
                    country.name = child.text
                else:
                    pass # ignore given country name
            elif child.tag == 'ModifyDate':
                raise NotImplementedError

def _readIOCCode(element):
    value = element.get('value')
    if value == 'ROM':
        return 'ROU'
    elif value == 'YOG':
        raise ValueError('CountryCode YOG is unsupported')
    elif value == 'other':
        return None
    else:
        return value

def _readEntry(element):
    entry = model.Entry()
    if element.get('nonCompetitor', 'N') == 'Y':
        raise NotImplementedError

    for child in element:
        if child.tag == 'EntryId':
            raise NotImplementedError
        elif child.tag == 'TeamName':
            entry.name = child.text
        elif child.tag in {'PersonID', 'Person'}:
            competitor = model.Competitor(person = _readPerson(child))
            entry.competitors.append(competitor)
        elif child.tag == 'CCard':
            raise NotImplementedError
        elif child.tag == 'Rank':
            raise NotImplementedError
        elif child.tag in {'ClubID', 'Club'}:
            entry.organization = _readClub(child)
        elif child.tag == 'TeamSequence':
            entry.entry_sequence = int(child.text)
        elif child.tag == 'EntryClass':
            raise NotImplementedError
        elif child.tag == 'AllocationControl':
            raise NotImplementedError
        elif child.tag == 'EntryDate':
            raise NotImplementedError
        elif child.tag == 'ModifyDate':
            raise NotImplementedError

    return entry
