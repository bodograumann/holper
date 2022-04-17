"""Data Model

Define the central data types as stored in an event database.
This is based on the data types defined in `IOF XML v3.0`_.
Use SQLAlchemy as database library.

.. _IOF XML v3.0: http://orienteering.org/resources/it/data-standard-3-0/
"""

__all__ = [
    "Base",
    "Country",
    "EventForm",
    "Event",
    "EventXID",
    "Sex",
    "EventCategoryStatus",
    "EventCategory",
    "EventCategoryXID",
    "Race",
    "RaceCategoryStatus",
    "Leg",
    "Control",
    "Course",
    "CourseControl",
    "ControlType",
    "Category",
    "Person",
    "PersonXID",
    "OrganisationType",
    "Organisation",
    "OrganisationXID",
    "Entry",
    "EntryCategoryRequest",
    "StartTimeAllocationRequest",
    "StartTimeAllocationRequestType",
    "PunchingSystem",
    "ControlCard",
    "Competitor",
    "Start",
    "CompetitorStart",
    "Result",
    "CompetitorResult",
    "ResultStatus",
]

import enum

from sqlalchemy import (
    Table,
    Column,
    Sequence,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    Integer,
    Boolean,
    Float,
    Date,
    DateTime,
    Interval,
    Enum,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta

from .tools import camelcase_to_snakecase


def auto_enum(name, members):
    """Automatically generate enum values as UPPER_CASE => lower_case"""
    return enum.Enum(name, ((label, label.lower()) for label in members))


# suggested by Sergey Shubin, http://stackoverflow.com/a/41362392/1534459
class _ExternalObject(DeclarativeMeta):
    @classmethod
    def __prepare__(metacls, name, bases):
        namespace = super().__prepare__(metacls, name, bases)

        if name.endswith("XID"):
            parent_model = name[:-3]
            attr_rel = camelcase_to_snakecase(parent_model)
            attr_id = attr_rel + "_id"

            namespace["issuer"] = Column(String(32), primary_key=True)
            namespace["external_id"] = Column(String(16), primary_key=True)
            namespace[attr_id] = Column(Integer, ForeignKey("%s.%s" % (parent_model, attr_id)))
            namespace[attr_rel] = relationship(parent_model, backref="external_ids")

            namespace["__repr__"] = lambda self: "<%s(%s: %s)>" % (
                self.__class__.__name__,
                self.issuer,
                self.external_id,
            )

        return namespace


class _ModelBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    @property
    def id_column(self):
        return camelcase_to_snakecase(self.__class__.__name__) + "_id"

    def __repr__(self):
        try:
            primary_key = getattr(self, self.id_column)
        except AttributeError:
            primary_key = "No id"

        return "<%s(%s)>" % (self.__class__.__name__, repr(primary_key))


Base = declarative_base(cls=_ModelBase, metaclass=_ExternalObject)


class Country(Base):
    country_id = Column(
        Integer,
        Sequence("country_id_seq"),
        primary_key=True,
        autoincrement=False,
        doc="ISO-3166 numeric code",
    )
    name = Column(String(63), nullable=False)
    iso_alpha_2 = Column(String(2), doc="ISO-3166 alpha-2 code", nullable=False)
    iso_alpha_3 = Column(String(3), doc="ISO-3166 alpha-3 code", nullable=False)
    ioc_code = Column(String(3), doc="International Olympic Committee’s 3-letter code")


# Configuration of teams and legs for an event
#
# Custom types should be added with an X_ prefix.
# E.g. X_CUSTOM = ()
EventForm = auto_enum("EventForm", ["INDIVIDUAL", "TEAM", "RELAY"])


class Event(Base):
    """Largest organisational unit to assign entries to

    An event can consist of one or multiple :py:class:`races <.Race>`.
    This occurs for multi-day events and for events with heats and
    finals. All races of an event must have the same form (e.g.
    individual or relay) and offer the same categories defined by
    :py:class:`~.EventCategory`.
    """

    event_id = Column(Integer, Sequence("event_id_seq"), primary_key=True)
    name = Column(String(255))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    form = Column(Enum(EventForm), default=EventForm.INDIVIDUAL, nullable=False)

    races = relationship("Race", back_populates="event")
    event_categories = relationship("EventCategory", back_populates="event")
    entries = relationship("Entry", back_populates="event")


class EventXID(Base):
    pass


class Sex(enum.Enum):
    FEMALE = "F"
    MALE = "M"


EventCategoryStatus = auto_enum(
    "EventCategoryStatus",
    [
        "NORMAL",
        "DIVIDED",
        "JOINED",
        "INVALIDATED",
        "INVALIDATED_NO_FEE",
    ],
)


class EventCategory(Base):
    """Category in an event

    Here category information specific to an event but common to all
    races is stored.

    For example included are a number of legs. Usually this occurs for
    relay events, but can also be used when each starter must complete
    several courses, such that the total time is used for the final
    ranking.
    """

    event_category_id = Column(Integer, Sequence("event_category_id_seq"), primary_key=True)

    event_id = Column(Integer, ForeignKey(Event.event_id))
    event = relationship(Event, back_populates="event_categories")
    name = Column(String(32), nullable=False)
    short_name = Column(String(8))
    status = Column(Enum(EventCategoryStatus), default=EventCategoryStatus.NORMAL)

    legs = relationship("Leg", back_populates="event_category")
    entry_requests = relationship("EntryCategoryRequest", back_populates="event_category")

    ### restrictions ###

    min_age = Column(SmallInteger)
    max_age = Column(SmallInteger)
    sex = Column(Enum(Sex))

    min_number_of_team_members = Column(SmallInteger, default=1)
    max_number_of_team_members = Column(SmallInteger, default=1)
    min_team_age = Column(SmallInteger)
    max_team_age = Column(SmallInteger)

    max_number_of_competitors = Column(SmallInteger)


class EventCategoryXID(Base):
    pass


class Race(Base):
    """Smallest organisational unit to assign entries to"""

    race_id = Column(Integer, Sequence("race_id_seq"), primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.event_id), nullable=False)
    event = relationship(Event, back_populates="races")

    first_start = Column(TIMESTAMP(timezone=True))

    categories = relationship("Category", back_populates="race")
    controls = relationship("Control", back_populates="race")
    courses = relationship("Course", back_populates="race")

    @property
    def entries(self):
        return self.event.entries


RaceCategoryStatus = auto_enum(
    "RaceCategoryStatus",
    [
        "START_TIMES_NOT_ALLOCATED",
        "START_TIMES_ALLOCATED",
        "NOT_USED",
        "COMPLETED",
        "INVALIDATED",
        "INVALIDATED_NO_FEE",
    ],
)


class Leg(Base):
    leg_id = Column(Integer, Sequence("leg_id_seq"), primary_key=True)
    event_category_id = Column(Integer, ForeignKey(EventCategory.event_category_id), nullable=False)
    event_category = relationship(EventCategory, back_populates="legs")

    leg_number = Column(SmallInteger)

    min_number_of_competitors = Column(SmallInteger, default=1)
    max_number_of_competitors = Column(SmallInteger, default=1)


class Control(Base):
    control_id = Column(Integer, Sequence("control_id_seq"), primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.race_id), nullable=False)
    race = relationship(Race, back_populates="controls")
    label = Column(String(16), nullable=False)

    UniqueConstraint("race_id", "label")


class Course(Base):
    course_id = Column(Integer, Sequence("course_id_seq"), primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.race_id), nullable=False)
    race = relationship(Race, back_populates="courses")

    name = Column(String(16))
    length = Column(Float, doc="Course length in kilometers")
    climb = Column(Float, doc="Course climb in meters")

    controls = relationship("CourseControl", back_populates="course")
    categories = relationship("CategoryCourseAssignment", back_populates="course")


ControlType = auto_enum(
    "ControlType",
    ["CONTROL", "START", "FINISH", "CROSSING_POINT", "END_OF_MARKED_ROUTE"],
)


class CourseControl(Base):
    course_control_id = Column(Integer, Sequence("course_control_id_seq"), primary_key=True)
    course_id = Column(Integer, ForeignKey(Course.course_id), nullable=False)
    course = relationship(Course, back_populates="controls")
    control_id = Column(Integer, ForeignKey(Control.control_id), nullable=False)
    control = relationship(Control)

    leg_length = Column(Float, doc="Leg length in kilometers")
    leg_climb = Column(Float, doc="Leg climb in meters")

    type = Column(Enum(ControlType), default=ControlType.CONTROL, nullable=False)
    score = Column(Float)
    order = Column(
        Integer,
        doc="If a course control has a higher `order` than another, \
            it has to be punched after it.",
    )
    after_course_control_id = Column(Integer, ForeignKey("CourseControl.course_control_id"))
    after = relationship(
        "CourseControl",
        foreign_keys=[after_course_control_id],
        remote_side=course_control_id,
        doc="Control must be punched after this other control.",
    )
    before_course_control_id = Column(Integer, ForeignKey("CourseControl.course_control_id"))
    before = relationship(
        "CourseControl",
        foreign_keys=[before_course_control_id],
        remote_side=course_control_id,
        doc="Control must be punched before this other control.",
    )


class Category(Base):
    """Realize an EventCategory for one specific race of that event"""

    category_id = Column(Integer, Sequence("category_id_seq"), primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.race_id), nullable=False)
    race = relationship(Race, back_populates="categories")

    event_category_id = Column(Integer, ForeignKey(EventCategory.event_category_id), nullable=False)
    event_category = relationship(EventCategory)

    status = Column(Enum(RaceCategoryStatus), default=RaceCategoryStatus.START_TIMES_NOT_ALLOCATED)

    courses = relationship("CategoryCourseAssignment", back_populates="category")

    time_offset = Column(Interval, doc="Start time offset from race start time")
    starts = relationship("Start", back_populates="category")
    vacancies_before = Column(SmallInteger, default=0, nullable=False)
    vacancies_after = Column(SmallInteger, default=0, nullable=False)

    @property
    def name(self):
        return self.event_category.name

    @property
    def short_name(self):
        return self.event_category.short_name


class CategoryCourseAssignment(Base):
    category_id = Column(Integer, ForeignKey(Category.category_id), primary_key=True)
    category = relationship(Category, back_populates="courses")
    leg = Column(SmallInteger, default=1, primary_key=True)
    course_id = Column(Integer, ForeignKey(Course.course_id), nullable=False)
    course = relationship(Course, back_populates="categories")


### Entries ###


class Person(Base):
    person_id = Column(Integer, Sequence("person_id_seq"), primary_key=True)
    title = Column(String(31))
    family_name = Column(String(64))
    given_name = Column(String(160))
    birth_date = Column(Date)
    country_id = Column(Integer, ForeignKey(Country.country_id))
    country = relationship(Country)
    sex = Column(Enum(Sex))


class PersonXID(Base):
    pass


OrganisationType = auto_enum(
    "OrganisationType",
    [
        "IOF",
        "IOF_REGION",
        "NATIONAL_FEDERATION",
        "NATIONAL_REGION",
        "CLUB",
        "SCHOOL",
        "COMPANY",
        "MILITARY",
        "OTHER",
    ],
)


class Organisation(Base):
    organisation_id = Column(Integer, Sequence("organisation_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(32))
    country_id = Column(Integer, ForeignKey(Country.country_id))
    country = relationship(Country)
    type = Column(Enum(OrganisationType))


class OrganisationXID(Base):
    pass


class Entry(Base):
    entry_id = Column(Integer, Sequence("entry_id_seq"), primary_key=True)

    event_id = Column(Integer, ForeignKey(Event.event_id), nullable=False)
    event = relationship(Event, back_populates="entries")

    number = Column(Integer, nullable=True)
    name = Column(String(255))
    competitors = relationship("Competitor", back_populates="entry")

    organisation_id = Column(Integer, ForeignKey(Organisation.organisation_id))
    organisation = relationship(Organisation)

    category_requests = relationship(
        "EntryCategoryRequest",
        back_populates="entry",
        doc="Requested categories with preference",
    )
    start_time_allocation_requests = relationship("StartTimeAllocationRequest")
    starts = relationship("Start", back_populates="entry")

    @property
    def races(self):
        # TODO: Allow participation in only some of the events races.
        return self.event.races


class EntryXID(Base):
    pass


class EntryCategoryRequest(Base):
    entry_id = Column(Integer, ForeignKey(Entry.entry_id), primary_key=True)
    entry = relationship(Entry)
    preference = Column(
        SmallInteger,
        primary_key=True,
        default=0,
        doc="Lower number means higher preference",
    )
    event_category_id = Column(Integer, ForeignKey(EventCategory.event_category_id), nullable=False)
    event_category = relationship(EventCategory, back_populates="entry_requests")


StartTimeAllocationRequestType = auto_enum(
    "StartTimeAllocationRequestType",
    [
        "NORMAL",
        "EARLY_START",
        "LATE_START",
        "SEPARATED_FROM",
        "GROUPED_WITH",
    ],
)


class StartTimeAllocationRequest(Base):
    start_time_allocation_request_id = Column(
        Integer, Sequence("start_time_allocation_request_id_seq"), primary_key=True
    )
    entry_id = Column(Integer, ForeignKey(Entry.entry_id), nullable=False)
    entry = relationship(Entry, back_populates="start_time_allocation_requests")

    type = Column(
        Enum(StartTimeAllocationRequestType),
        default=StartTimeAllocationRequestType.NORMAL,
    )
    organisation_id = Column(Integer, ForeignKey(Organisation.organisation_id))
    organisation = relationship(Organisation)
    person_id = Column(Integer, ForeignKey(Person.person_id))
    person = relationship(Person)


PunchingSystem = auto_enum("PunchingSystem", ["SportIdent", "Emit"])


class ControlCard(Base):
    control_card_id = Column(Integer, Sequence("control_card_id_seq"), primary_key=True)
    system = Column(Enum(PunchingSystem))
    label = Column(String(16))


class Competitor(Base):
    competitor_id = Column(Integer, Sequence("competitor_id_seq"), primary_key=True)

    entry_id = Column(Integer, ForeignKey(Entry.entry_id), nullable=False)
    entry = relationship(Entry, back_populates="competitors")

    entry_sequence = Column(SmallInteger, default=1, doc="1-based position of the competitor in the team")
    leg_number = Column(SmallInteger)
    leg_order = Column(SmallInteger)

    person_id = Column(Integer, ForeignKey(Person.person_id), nullable=False)
    person = relationship(Person)

    organisation_id = Column(Integer, ForeignKey(Organisation.organisation_id))
    organisation = relationship(Organisation)

    control_cards = relationship(
        "ControlCard",
        secondary=Table(
            "CompetitorControlCards",
            Base.metadata,
            Column(
                "competitor_id",
                Integer,
                ForeignKey("Competitor.competitor_id"),
                nullable=False,
            ),
            Column(
                "control_card_id",
                Integer,
                ForeignKey(ControlCard.control_card_id),
                nullable=False,
            ),
        ),
    )

    starts = relationship("CompetitorStart", back_populates="competitor")


class CompetitorXID(Base):
    pass


### Starts ###


class Start(Base):
    start_id = Column(Integer, Sequence("start_id_seq"), primary_key=True)
    result = relationship("Result", uselist=False, back_populates="start")

    category_id = Column(Integer, ForeignKey(Category.category_id), nullable=False)
    category = relationship(Category, back_populates="starts")
    entry_id = Column(Integer, ForeignKey(Entry.entry_id), nullable=False)
    entry = relationship(Entry, back_populates="starts")

    competitive = Column(
        Boolean,
        default=True,
        doc="Whether the starter is to be considered for the official ranking. \
        This can be set to `False` for example if the starter does not fulfill some entry requirement.",
    )
    time_offset = Column(Interval, doc="Start time offset from category start time")

    competitor_starts = relationship("CompetitorStart", back_populates="start")


class CompetitorStart(Base):
    competitor_start_id = Column(Integer, Sequence("competitor_start_id_seq"), primary_key=True)
    competitor_result = relationship("CompetitorResult", uselist=False, back_populates="competitor_start")

    start_id = Column(Integer, ForeignKey(Start.start_id), nullable=False)
    start = relationship(Start, back_populates="competitor_starts")
    competitor_id = Column(Integer, ForeignKey(Competitor.competitor_id), nullable=False)
    competitor = relationship(Competitor, back_populates="starts")

    time_offset = Column(Interval, doc="Start time offset from entry start time")
    control_card_id = Column(Integer, ForeignKey(ControlCard.control_card_id))
    control_card = relationship(ControlCard)


### Results ###

ResultStatus = auto_enum(
    "ResultStatus",
    [
        "OK",
        "FINISHED",
        "MISSING_PUNCH",
        "DISQUALIFIED",
        "DID_NOT_FINISH",
        "ACTIVE",
        "INACTIVE",
        "OVER_TIME",
        "SPORTING_WITHDRAWAL",
        "NOT_COMPETING",
        "MOVED",
        "MOVED_UP",
        "DID_NOT_START",
        "DID_NOT_ENTER",
        "CANCELLED",
    ],
)


class Result(Base):
    result_id = Column(Integer, ForeignKey(Start.start_id), primary_key=True)
    start = relationship(Start, back_populates="result")

    start_time = Column(DateTime, doc="Actual start time used for placement")
    finish_time = Column(DateTime, doc="Actual finish time used for placement")

    time_adjustment = Column(Interval, doc="Time bonus or penalty", nullable=False)
    time = Column(Interval)

    status = Column(Enum(ResultStatus))


class CompetitorResult(Base):
    competitor_result_id = Column(Integer, ForeignKey(CompetitorStart.competitor_start_id), primary_key=True)
    competitor_start = relationship(CompetitorStart, back_populates="competitor_result")

    start_time = Column(DateTime, doc="Actual start time used for placement")
    finish_time = Column(DateTime, doc="Actual finish time used for placement")

    time_adjustment = Column(Interval, doc="Time bonus or penalty", nullable=False)
    time = Column(Interval)

    status = Column(Enum(ResultStatus))


# additional types in IOF XML:
# * Id → <Table>XID
# * PersonName → merged into Person
# * Score
# * Role
# * EntryReceiver
# * EventURL
# * Schedule
# * InformationItem
# * Class → EventCategory
# * ClassType
# * RaceClass → Category
# * Fee
# * AssignedFee
# * Amount
# * PersonEntry → Competitor / Entry
# * TeamEntry → Entry
# * TeamEntryPerson → Competitor
# * ClassStart
# * StartName
# * PersonStart → Competitor / Entry
# * PersonRaceStart → Start
# * TeamStart → Entry
# * TeamMemberStart → Competitor
# * TeamMemberRaceStart → CompetitorStart
# * ClassResult
# * PersonResult
# * PersonRaceResult → Result
# * TeamResult
# * TeamMemberResult
# * TeamMemberRaceResult → CompetitorResult
# * OverallResult
# * ControlAnswer
# * SplitTime
# * Route
# * GeoPosition
# * Map
# * Image
# * MapPosition
# * RaceCourseData
# * ClassCourseAssignment → CategoryCourseAssignment
# * PersonCourseAssignment
# * TeamCourseAssignment
# * TeamMemberCourseAssignment
# * SimpleCourse
# * SimpleRaceCourse
# * Service
# * OrganisationServiceRequest
# * PersonServiceRequest
# * ServiceRequest
# * Account
# * Address
# * Contact
# * DateAndOptionalTime → DateTime type
# * LanguageString
# * Extensions
