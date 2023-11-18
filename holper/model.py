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
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Interval,
    Sequence,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .tools import camelcase_to_snakecase


def auto_enum(name, members):
    """Automatically generate enum values as UPPER_CASE => lower_case"""
    return enum.Enum(name, ((label, label.lower()) for label in members))


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__

    @property
    def id_column(self):
        """Convention for the primary id column"""
        return camelcase_to_snakecase(self.__class__.__name__) + "_id"

    def __repr__(self):
        try:
            primary_key = getattr(self, self.id_column)
        except AttributeError:
            primary_key = "No id"

        return f"<{self.__class__.__name__}({primary_key!r})>"


class ExternalId:
    """Common base class for external id models."""

    @declared_attr
    def issuer(cls) -> Mapped[str]:
        return mapped_column(String(32), primary_key=True, nullable=False)

    @declared_attr
    def external_id(cls) -> Mapped[str]:
        return mapped_column(String(16), primary_key=True, nullable=False)


class HasExternalIds:
    """Back populate list of external ids"""


class Country(Base):
    country_id = mapped_column(
        Integer,
        Sequence("country_id_seq"),
        primary_key=True,
        autoincrement=False,
        doc="ISO-3166 numeric code",
    )
    name = mapped_column(String(63), nullable=False)
    iso_alpha_2 = mapped_column(String(2), doc="ISO-3166 alpha-2 code", nullable=False)
    iso_alpha_3 = mapped_column(String(3), doc="ISO-3166 alpha-3 code", nullable=False)
    ioc_code = mapped_column(String(3), doc="International Olympic Committee’s 3-letter code")


# Configuration of teams and legs for an event
#
# Custom types should be added with an X_ prefix.
EventForm = auto_enum("EventForm", ["INDIVIDUAL", "TEAM", "RELAY"])


class Event(Base, HasExternalIds):
    """Largest organisational unit to assign entries to

    An event can consist of one or multiple :py:class:`races <.Race>`.
    This occurs for multi-day events and for events with heats and
    finals. All races of an event must have the same form (e.g.
    individual or relay) and offer the same categories defined by
    :py:class:`~.EventCategory`.
    """

    event_id = mapped_column(Integer, Sequence("event_id_seq"), primary_key=True)
    external_ids = relationship("EventXID", back_populates="event")

    name = mapped_column(String(255))
    start_time = mapped_column(DateTime)
    end_time = mapped_column(DateTime)
    form = mapped_column(Enum(EventForm), default=EventForm.INDIVIDUAL, nullable=False)

    races = relationship("Race", back_populates="event")
    event_categories = relationship("EventCategory", back_populates="event")
    entries = relationship("Entry", back_populates="event")


class EventXID(Base, ExternalId):
    event_id = mapped_column(Integer, ForeignKey("Event.event_id"), nullable=False)
    event = relationship(Event, back_populates="external_ids")


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


class EventCategory(Base, HasExternalIds):
    """Category in an event

    Here category information specific to an event but common to all
    races is stored.

    For example included are a number of legs. Usually this occurs for
    relay events, but can also be used when each starter must complete
    several courses, such that the total time is used for the final
    ranking.
    """

    event_category_id = mapped_column(Integer, Sequence("event_category_id_seq"), primary_key=True)
    external_ids = relationship("EventCategoryXID", back_populates="event_category")

    event_id = mapped_column(Integer, ForeignKey(Event.event_id))
    event = relationship(Event, back_populates="event_categories")
    name = mapped_column(String(32), nullable=False)
    short_name = mapped_column(String(8))
    status = mapped_column(Enum(EventCategoryStatus), default=EventCategoryStatus.NORMAL)

    legs = relationship("Leg", back_populates="event_category")
    entry_requests = relationship("EntryCategoryRequest", back_populates="event_category")

    ### restrictions ###

    min_age = mapped_column(SmallInteger)
    max_age = mapped_column(SmallInteger)
    sex = mapped_column(Enum(Sex))

    min_number_of_team_members = mapped_column(SmallInteger, default=1)
    max_number_of_team_members = mapped_column(SmallInteger, default=1)
    min_team_age = mapped_column(SmallInteger)
    max_team_age = mapped_column(SmallInteger)

    # In IOF XMLv3 this is called maxNumberOfCompetitors
    starter_limit = mapped_column(SmallInteger)


class EventCategoryXID(Base, ExternalId):
    event_category_id = mapped_column(Integer, ForeignKey("EventCategory.event_category_id"), nullable=False)
    event_category = relationship(EventCategory, back_populates="external_ids")


class Race(Base):
    """Smallest organisational unit to assign entries to"""

    race_id = mapped_column(Integer, Sequence("race_id_seq"), primary_key=True)
    event_id = mapped_column(Integer, ForeignKey(Event.event_id), nullable=False)
    event = relationship(Event, back_populates="races")

    first_start = mapped_column(TIMESTAMP(timezone=True))

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
    leg_id = mapped_column(Integer, Sequence("leg_id_seq"), primary_key=True)
    event_category_id = mapped_column(Integer, ForeignKey(EventCategory.event_category_id), nullable=False)
    event_category = relationship(EventCategory, back_populates="legs")

    leg_number = mapped_column(SmallInteger)

    # Number of competitors of each team that compete together in this leg
    min_number_of_competitors = mapped_column(SmallInteger, default=1)
    max_number_of_competitors = mapped_column(SmallInteger, default=1)


class Control(Base):
    control_id = mapped_column(Integer, Sequence("control_id_seq"), primary_key=True)
    race_id = mapped_column(Integer, ForeignKey(Race.race_id), nullable=False)
    race = relationship(Race, back_populates="controls")
    label = mapped_column(String(16), nullable=False)

    UniqueConstraint("race_id", "label")


class Course(Base):
    course_id = mapped_column(Integer, Sequence("course_id_seq"), primary_key=True)
    race_id = mapped_column(Integer, ForeignKey(Race.race_id), nullable=False)
    race = relationship(Race, back_populates="courses")

    name = mapped_column(String(16))
    length = mapped_column(Float, doc="Course length in kilometers")
    climb = mapped_column(Float, doc="Course climb in meters")

    controls = relationship("CourseControl", back_populates="course")
    categories = relationship("CategoryCourseAssignment", back_populates="course")


ControlType = auto_enum(
    "ControlType",
    ["CONTROL", "START", "FINISH", "CROSSING_POINT", "END_OF_MARKED_ROUTE"],
)


class CourseControl(Base):
    course_control_id = mapped_column(Integer, Sequence("course_control_id_seq"), primary_key=True)
    course_id = mapped_column(Integer, ForeignKey(Course.course_id), nullable=False)
    course = relationship(Course, back_populates="controls")
    control_id = mapped_column(Integer, ForeignKey(Control.control_id), nullable=False)
    control = relationship(Control)

    leg_length = mapped_column(Float, doc="Leg length in kilometers")
    leg_climb = mapped_column(Float, doc="Leg climb in meters")

    type = mapped_column(Enum(ControlType), default=ControlType.CONTROL, nullable=False)
    score = mapped_column(Float)
    order = mapped_column(
        Integer,
        doc="If a course control has a higher `order` than another, \
            it has to be punched after it.",
    )
    after_course_control_id = mapped_column(Integer, ForeignKey("CourseControl.course_control_id"))
    after = relationship(
        "CourseControl",
        foreign_keys=[after_course_control_id],
        remote_side=course_control_id,
        doc="Control must be punched after this other control.",
    )
    before_course_control_id = mapped_column(Integer, ForeignKey("CourseControl.course_control_id"))
    before = relationship(
        "CourseControl",
        foreign_keys=[before_course_control_id],
        remote_side=course_control_id,
        doc="Control must be punched before this other control.",
    )


class Category(Base):
    """Realize an EventCategory for one specific race of that event"""

    category_id = mapped_column(Integer, Sequence("category_id_seq"), primary_key=True)
    race_id = mapped_column(Integer, ForeignKey(Race.race_id), nullable=False)
    race = relationship(Race, back_populates="categories")

    event_category_id = mapped_column(Integer, ForeignKey(EventCategory.event_category_id), nullable=False)
    event_category = relationship(EventCategory)

    status = mapped_column(Enum(RaceCategoryStatus), default=RaceCategoryStatus.START_TIMES_NOT_ALLOCATED)

    courses = relationship("CategoryCourseAssignment", back_populates="category")

    time_offset = mapped_column(Interval, doc="Start time offset from race start time")
    starts = relationship("Start", back_populates="category")
    vacancies_before = mapped_column(SmallInteger, default=0, nullable=False)
    vacancies_after = mapped_column(SmallInteger, default=0, nullable=False)

    # In IOF XMLv3 this is called maxNumberOfCompetitors
    starter_limit = mapped_column(SmallInteger)

    @property
    def name(self):
        return self.event_category.name

    @property
    def short_name(self):
        return self.event_category.short_name


class CategoryCourseAssignment(Base):
    category_id = mapped_column(Integer, ForeignKey(Category.category_id), primary_key=True)
    category = relationship(Category, back_populates="courses")
    leg = mapped_column(SmallInteger, default=1, primary_key=True)
    course_id = mapped_column(Integer, ForeignKey(Course.course_id), nullable=False)
    course = relationship(Course, back_populates="categories")


### Entries ###


class Person(Base, HasExternalIds):
    person_id = mapped_column(Integer, Sequence("person_id_seq"), primary_key=True)
    external_ids = relationship("PersonXID", back_populates="person")

    title = mapped_column(String(31))
    family_name = mapped_column(String(64))
    given_name = mapped_column(String(160))
    birth_date = mapped_column(Date)
    country_id = mapped_column(Integer, ForeignKey(Country.country_id))
    country = relationship(Country)
    sex = mapped_column(Enum(Sex))


class PersonXID(Base, ExternalId):
    person_id = mapped_column(Integer, ForeignKey("Person.person_id"), nullable=False)
    person = relationship(Person, back_populates="external_ids")


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


class Organisation(Base, HasExternalIds):
    organisation_id = mapped_column(Integer, Sequence("organisation_id_seq"), primary_key=True)
    external_ids = relationship("OrganisationXID", back_populates="organisation")

    name = mapped_column(String(255), nullable=False)
    short_name = mapped_column(String(32))
    country_id = mapped_column(Integer, ForeignKey(Country.country_id))
    country = relationship(Country)
    type = mapped_column(Enum(OrganisationType))


class OrganisationXID(Base, ExternalId):
    organisation_id = mapped_column(Integer, ForeignKey("Organisation.organisation_id"), nullable=False)
    organisation = relationship(Organisation, back_populates="external_ids")


class Entry(Base, HasExternalIds):
    entry_id = mapped_column(Integer, Sequence("entry_id_seq"), primary_key=True)
    external_ids = relationship("EntryXID", back_populates="entry")

    event_id = mapped_column(Integer, ForeignKey(Event.event_id), nullable=False)
    event = relationship(Event, back_populates="entries")

    number = mapped_column(Integer, nullable=True)
    name = mapped_column(String(255))
    competitors = relationship("Competitor", back_populates="entry")

    organisation_id = mapped_column(Integer, ForeignKey(Organisation.organisation_id))
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


class EntryXID(Base, ExternalId):
    entry_id = mapped_column(Integer, ForeignKey("Entry.entry_id"), nullable=False)
    entry = relationship(Entry, back_populates="external_ids")


class EntryCategoryRequest(Base):
    entry_id = mapped_column(Integer, ForeignKey(Entry.entry_id), primary_key=True)
    entry = relationship(Entry)
    preference = mapped_column(
        SmallInteger,
        primary_key=True,
        default=0,
        doc="Lower number means higher preference",
    )
    event_category_id = mapped_column(Integer, ForeignKey(EventCategory.event_category_id), nullable=False)
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
    start_time_allocation_request_id = mapped_column(
        Integer,
        Sequence("start_time_allocation_request_id_seq"),
        primary_key=True,
    )
    entry_id = mapped_column(Integer, ForeignKey(Entry.entry_id), nullable=False)
    entry = relationship(Entry, back_populates="start_time_allocation_requests")

    type = mapped_column(
        Enum(StartTimeAllocationRequestType),
        default=StartTimeAllocationRequestType.NORMAL,
    )
    organisation_id = mapped_column(Integer, ForeignKey(Organisation.organisation_id))
    organisation = relationship(Organisation)
    person_id = mapped_column(Integer, ForeignKey(Person.person_id))
    person = relationship(Person)


PunchingSystem = auto_enum("PunchingSystem", ["SportIdent", "Emit"])


class ControlCard(Base):
    control_card_id = mapped_column(Integer, Sequence("control_card_id_seq"), primary_key=True)
    system = mapped_column(Enum(PunchingSystem))
    label = mapped_column(String(16))


class Competitor(Base, HasExternalIds):
    competitor_id = mapped_column(Integer, Sequence("competitor_id_seq"), primary_key=True)
    external_ids = relationship("CompetitorXID", back_populates="competitor")

    entry_id = mapped_column(Integer, ForeignKey(Entry.entry_id), nullable=False)
    entry = relationship(Entry, back_populates="competitors")

    entry_sequence = mapped_column(SmallInteger, default=1, doc="1-based position of the competitor in the team")
    leg_number = mapped_column(SmallInteger)
    leg_order = mapped_column(SmallInteger)

    person_id = mapped_column(Integer, ForeignKey(Person.person_id), nullable=False)
    person = relationship(Person)

    organisation_id = mapped_column(Integer, ForeignKey(Organisation.organisation_id))
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


class CompetitorXID(Base, ExternalId):
    competitor_id = mapped_column(Integer, ForeignKey("Competitor.competitor_id"), nullable=False)
    competitor = relationship(Competitor, back_populates="external_ids")


### Starts ###


class Start(Base):
    start_id = mapped_column(Integer, Sequence("start_id_seq"), primary_key=True)
    result = relationship("Result", uselist=False, back_populates="start")

    category_id = mapped_column(Integer, ForeignKey(Category.category_id), nullable=False)
    category = relationship(Category, back_populates="starts")
    entry_id = mapped_column(Integer, ForeignKey(Entry.entry_id), nullable=False)
    entry = relationship(Entry, back_populates="starts")

    competitive = mapped_column(
        Boolean,
        default=True,
        doc="Whether the starter is to be considered for the official ranking. \
        This can be set to `False` for example if the starter does not fulfill some entry requirement.",
    )
    time_offset = mapped_column(Interval, doc="Start time offset from category start time")

    competitor_starts = relationship("CompetitorStart", back_populates="start")


class CompetitorStart(Base):
    competitor_start_id = mapped_column(Integer, Sequence("competitor_start_id_seq"), primary_key=True)
    competitor_result = relationship("CompetitorResult", uselist=False, back_populates="competitor_start")

    start_id = mapped_column(Integer, ForeignKey(Start.start_id), nullable=False)
    start = relationship(Start, back_populates="competitor_starts")
    competitor_id = mapped_column(Integer, ForeignKey(Competitor.competitor_id), nullable=False)
    competitor = relationship(Competitor, back_populates="starts")

    time_offset = mapped_column(Interval, doc="Start time offset from entry start time")
    control_card_id = mapped_column(Integer, ForeignKey(ControlCard.control_card_id))
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
    result_id = mapped_column(Integer, ForeignKey(Start.start_id), primary_key=True)
    start = relationship(Start, back_populates="result")

    start_time = mapped_column(DateTime, doc="Actual start time used for placement")
    finish_time = mapped_column(DateTime, doc="Actual finish time used for placement")

    time_adjustment = mapped_column(Interval, doc="Time bonus or penalty", nullable=False)
    time = mapped_column(Interval)

    status = mapped_column(Enum(ResultStatus))
    position = mapped_column(Integer, doc="Position in the category")


class CompetitorResult(Base):
    competitor_result_id = mapped_column(Integer, ForeignKey(CompetitorStart.competitor_start_id), primary_key=True)
    competitor_start = relationship(CompetitorStart, back_populates="competitor_result")

    start_time = mapped_column(DateTime, doc="Actual start time used for placement")
    finish_time = mapped_column(DateTime, doc="Actual finish time used for placement")

    time_adjustment = mapped_column(Interval, doc="Time bonus or penalty", nullable=False)
    time = mapped_column(Interval)

    status = mapped_column(Enum(ResultStatus))


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
