"""Data exchange in IOF XML v3.0

See `IOF XML v3.0`_ on orienteering.org.

While we considered using a code generator like generateDS, it did not
seem worthwhile. The code generated would be 12000 lines and it would
not unburden us from building a sensible data model or doing necessary
post-processing steps on import. Furthermore etree already provides an
object model for the XML, which can be handled quite efficiently.

.. _IOF XML v3.0: http://orienteering.org/resources/it/data-standard-3-0/
"""

from collections import defaultdict
import datetime
from pkg_resources import resource_stream

import iso8601
from lxml import etree

from . import model
from .tools import camelcase_to_snakecase

_schema = etree.XMLSchema(etree.parse(resource_stream('holper.resources.IOF', 'IOF_3.0.xsd')))
_ns = 'http://www.orienteering.org/datastandard/3.0'


def detect(input_file):
    try:
        document = etree.parse(input_file)
    except etree.ParseError:
        return False
    return _schema.validate(document)


def read(input_file):
    parser = etree.XMLParser(remove_comments=True, remove_pis=True, collect_ids=False)
    document = etree.parse(input_file, parser)

    reader = _XMLReader(_ns)
    yield from reader.read_document(document)


class IDRegistry:
    """Store encountered objects with an <Id> according to their id type

    The following IOF XML v3.0 elements have Ids:

    * Person
    * Organisation
    * Event
    * Class
    * ClassType
    * Fee
    * PersonEntry
    * TeamEntry
    * Control
    * Map
    * Course
    * SimpleCourse
    * Service
    * ServiceRequest

    These Ids are used to identify entities defined elsewhere in the
    same document, defined in some database or issued by an official
    body.

    We do not support all of these though.
    """

    def __init__(self):
        self.objects = defaultdict(dict)

    def get(self, id_type, id_value):
        try:
            return self.objects[id_type][id_value]
        except KeyError:
            return None

    def put(self, issuer, id_type, id_value, obj):
        existing = self.get(id_type, id_value)
        if existing is not None and existing is not obj:
            raise KeyError('There is already a different element registered under this Id')

        self.objects[id_type][id_value] = obj

        if existing is None:
            obj.external_ids.append(
                    getattr(model, id_type + 'XID')(
                        issuer=issuer,
                        external_id=id_value
                    )
            )

class _XMLReader:
    def __init__(self, namespace):
        self.namespace = namespace
        self.id_registries = defaultdict(IDRegistry)

    def tags(self, element, tags, ns=None):
        if ns is None:
            ns = self.namespace
        name = etree.QName(element.tag)
        return name.namespace == ns and name.localname in tags

    def tag(self, element, tag, ns=None):
        return self.tags(element, {tag}, ns)

    """Factory method for model objects

    If the element has Id-tags, those will be used to register and later
    lookup the object in the :py:class:`~.IDRegistry` of the associated
    Id issuer.

    Some elements like <Class> might occur multiple times in a document
    instead of only being referenced through an Id.
    """
    def createObj(self, element, cls):
        obj = None
        for child in element:
            if not self.tag(child, 'Id') or not child.text:
                break

            issuer = child.get('type')
            registry = self.id_registries[issuer]
            obj = registry.get(cls.__name__, child.text)
            if obj:
                break

        if not obj:
            obj = cls()

        for child in element:
            if not self.tag(child, 'Id') or not child.text:
                break

            issuer = child.get('type')
            registry = self.id_registries[issuer]
            registry.put(issuer, cls.__name__, child.text, obj)

        return obj

    def createObjFromId(self, id_element, cls):
        issuer = id_element.get('type')
        obj = self.id_registries[issuer].get(cls.__name__, id_element.text)
        if not obj:
            obj = cls()
            registry = self.id_registries[issuer]
            registry.put(issuer, cls.__name__, id_element.text, obj)


    def read_document(self, document):
        root = document.getroot()

        if self.tag(root, 'EntryList'):
            yield from self._read_entry_list(root)
        elif self.tag(root, 'CourseData'):
            yield from self._read_course_data(root)
        elif self.tag(root, 'ClassList'):
            yield from self._read_class_list(root)
        else:
            raise NotImplementedError(root.tag)

    def _read_entry_list(self, element):
        event = None
        for child in element:
            if self.tag(child, 'Event'):
                event = self._read_event(child)
                yield event
            elif self.tag(child, 'TeamEntry'):
                entry = self._read_team_entry(child)
                entry.event = event
                yield entry
            elif self.tag(child, 'PersonEntry'):
                entry = self._read_person_entry(child)
                entry.event = event
                yield entry

    def _read_course_data(self, element):
        event = None
        for child in element:
            if self.tag(child, 'Event'):
                event = self._read_event(child)
                yield event
            elif self.tag(child, 'RaceCourseData'):
                race = self._read_race_course_data(child)
                race.event = event
                for category in race.categories:
                    category.event_category.event = race.event
                yield race

    def _read_event(self, element):
        event = self.createObj(element, model.Event)
        for child in element:
            if self.tag(child, 'Id'):
                pass
            elif self.tag(child, 'Name'):
                event.name = child.text
            elif self.tag(child, 'StartTime'):
                event.start_time = self._read_date_and_optional_time(child)
            elif self.tag(child, 'EndTime'):
                event.end_time = self._read_date_and_optional_time(child)
            elif self.tag(child, 'Form'):
                event.form = child.text
            elif self.tag(child, 'Class'):
                event.categories.append(self._read_class(child))
            elif self.tag(child, {'Status', 'Race'}):
                raise NotImplementedError(child.tag)
        return event

    def _read_date_and_optional_time(self, element):
        try:
            time = element[1].text
        except IndexError:
            time = '00:00:00'
        return iso8601.parse_date(element[0].text + 'T' + time)

    def _read_team_entry(self, element):
        entry = self.createObj(element, model.Entry)
        entry_count = 0

        for child in element:
            if self.tag(child, 'Id'):
                pass
            elif self.tag(child, 'Name'):
                entry.name = child.text
            elif self.tag(child, 'Organisation'):
                entry.organisation = self._read_organisation(child)
            elif self.tag(child, 'TeamEntryPerson'):
                entry_count += 1
                competitor = self._read_team_entry_person(child)
                competitor.entry_sequence = entry_count
                entry.competitors.append(competitor)
            elif self.tag(child, 'Class'):
                entry.category_requests.append(model.EntryCategoryRequest(
                    category=self._read_class(child)
                    ))
            elif self.tags(child, {
                'Race', 'AssignedFee', 'ServiceRequest',
                'StartTimeAllocationRequest', 'ContactInformation'
                }):
                raise NotImplementedError(child.tag)

        return entry

    def _read_team_entry_person(self, element):
        competitor = model.Competitor()

        for child in element:
            if self.tag(child, 'Person'):
                competitor.person = self._read_person(child)
            elif self.tag(child, 'Organisation'):
                competitor.organisation = self._read_organisation(child)
            elif self.tag(child, 'ControlCard'):
                competitor.control_cards.append(self._read_control_card(child))
            elif self.tag(child, 'Leg'):
                competitor.leg_number = int(child.text)
            elif self.tag(child, 'LegOrder'):
                competitor.leg_order = int(child.text)
            elif self.tags(child, {
                'Score', 'AssignedFee'
                }):
                raise NotImplementedError(child.tag)

        return competitor

    def _read_person_entry(self, element):
        competitor = self.createObj(element, model.Competitor)
        if competitor.entry is None:
            entry = model.Entry()
            competitor.entry = entry
        competitor.entry_sequence = 1

        for child in element:
            if self.tag(child, 'Person'):
                competitor.person = self._read_person(child)
            elif self.tag(child, 'Organisation'):
                competitor.organisation = self._read_organisation(child)
            elif self.tag(child, 'ControlCard'):
                competitor.control_cards.append(self._read_control_card(child))
            elif self.tag(child, 'Class'):
                entry.category_requests.append(model.EntryCategoryRequest(
                    category=self._read_class(child)
                    ))
            elif self.tags(child, {
                'Score', 'RaceNumber', 'AssignedFee', 'ServiceRequest',
                'StartTimeAllocationRequest'
                }):
                raise NotImplementedError(child.tag)

        return entry

    def _read_person(self, element):
        person = self.createObj(element, model.Person)

        sex = element.get('sex')
        if sex is not None:
            person.sex = model.Sex(sex)

        for child in element:
            if self.tag(child, 'Name'):
                for name_part in child:
                    if self.tag(name_part, 'Family'):
                        person.family_name = name_part.text
                    elif self.tag(name_part, 'Given'):
                        person.given_name = name_part.text
            elif self.tag(child, 'BirthDate'):
                person.birth_date = iso8601.parse_date(child.text)
            elif self.tag(child, 'Nationality'):
                person.nationality = self._read_country(child)

        return person

    def _read_country(self, element):
        return model.Country(ioc_code=element.get('code'))

    def _read_organisation(self, element):
        organisation = self.createObj(element, model.Organisation)

        type = element.get('type')
        if type is not None:
            organisation.type = model.OrganisationType(camelcase_to_snakecase(type))

        for child in element:
            if self.tag(child, 'Name'):
                organisation.name = child.text
            elif self.tag(child, 'ShortName'):
                organisation.short_name = child.text
            elif self.tag(child, 'Country'):
                organisation.country = self._read_country(child)
            elif self.tag(child, 'Address'):
                raise NotImplementedError(child.tag)

        return organisation

    def _read_control_card(self, element):
        card = model.ControlCard(label=element.text)

        system = element.get('system')
        if system is not None:
            if system.lower() in {'si', 'sportident'}:
                card.system = model.PunchingSystem.SportIdent
            elif system.lower() == 'emit':
                card.system = model.PunchingSystem.Emit
            else:
                raise NotImplementedError(system)

        return card

    def _read_class(self, element):
        event_category = self.createObj(element, model.EventCategory)

        for child in element:
            leg_count = 0
            if self.tag(child, 'Id'):
                pass
            elif self.tag(child, 'Name'):
                event_category.name = child.text
            elif self.tag(child, 'ShortName'):
                event_category.short_name = child.text
            elif self.tag(child, 'Leg'):
                leg_count += 1
                leg = model.Leg(
                        leg_number = leg_count,
                        min_number_of_competitors=child.get('minNumberOfCompetitors', 1),
                        max_number_of_competitors=child.get('maxNumberOfCompetitors', 1)
                )
                event_category.legs.append(leg)
            elif self.tags(child, {
                'TeamFee', 'Fee', 'Status', 'RaceClass',
                'TooFewEntriesSubstituteClass',
                'TooManyEntriesSubstituteClass'
                }):
                raise NotImplementedError(child.tag)

        return event_category

    def _read_race_course_data(self, element):
        race = model.Race()
        if element.get('raceNumber'):
            raise NotImplementedError('raceNumber')

        for child in element:
            if self.tag(child, 'Course'):
                race.courses.append(self._read_course(child))
            elif self.tag(child, 'ClassCourseAssignment'):
                race.categories.append(
                        self._read_class_course_assignment(child).category
                        )
            elif self.tags(child, {
                'PersonCourseAssignment', 'TeamCourseAssignment',
                }):
                raise NotImplementedError(child.tag)

        return race

    def _read_course(self, element):
        course = self.createObj(element, model.Course)

        random_order = False
        control_order = 0

        for child in element:
            if self.tag(child, 'Name'):
                course.name = child.text
            elif self.tag(child, 'Length'):
                course.length = float(child.text)
            elif self.tag(child, 'Climb'):
                course.climb = float(child.text)
            elif self.tag(child, 'CourseControl'):
                course_control = self._read_course_control(child)
                course_control.order = control_order
                course.controls.append(course_control)

                if not child.get('randomOrder') or not random_order:
                    control_order += 1
                random_order = child.get('randomOrder')
            elif self.tag(child, 'Family'):
                raise NotImplementedError(child.tag)

        return course

    def _read_course_control(self, element):
        course_control = model.CourseControl()

        type = element.get('type')
        if type is not None:
            course_control.type = model.ControlType(camelcase_to_snakecase(type))

        for child in element:
            if self.tag(child, 'Control'):
                if course_control.control:
                    raise NotImplementedError('Only one code per control allowed')
                course_control.control = model.Control(label=child.text)
            elif self.tag(child, 'LegLength'):
                course_control.length = float(child.text)
            elif self.tag(child, 'Score'):
                course_control.score = float(child.text)

        return course_control

    def _read_class_course_assignment(self, element):
        event_category = None
        assignment = model.CategoryCourseAssignment()

        for child in element:
            if self.tag(child, 'ClassId'):
                event_category = self.createObjFromId(child, model.EventCategory)
            elif self.tag(child, 'ClassName'):
                if not event_category:
                    event_category = model.EventCategory()
                if not event_category.name:
                    event_category.name = child.text
            elif self.tag(child, 'CourseName'):
                assignment.course = model.Course(name=child.text)
            elif self.tag(child, 'CourseFamily') \
                    and not assignment.course \
                    or self.tag(child, 'AllowedOnLeg'):
                raise NotImplementedError(child.tag)

        assignment.category = model.Category(event_category=event_category)
        return assignment

    def _read_class_list(self, element):
        for child in element:
            if self.tag(child, 'Class'):
                category = self._read_class(child)
                yield category
