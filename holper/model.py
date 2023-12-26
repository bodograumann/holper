"""Data Model

Define the central data types as stored in an event database.
This is based on the data types defined in `IOF XML v3.0`_.
Use SQLAlchemy as database library.

.. _IOF XML v3.0: http://orienteering.org/resources/it/data-standard-3-0/
"""

from __future__ import annotations

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
from abc import abstractmethod
from datetime import date, datetime, timedelta
from typing import Any, Self

from sqlalchemy import (
    TIMESTAMP,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Sequence,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .tools import camelcase_to_snakecase


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__

    @property
    def id_column(self) -> str:
        """Convention for the primary id column"""
        return camelcase_to_snakecase(self.__class__.__name__) + "_id"

    def __repr__(self) -> str:
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

    @property
    @abstractmethod
    def external_ids(self) -> Mapped[Any]:
        ...


class Country(Base):
    country_id: Mapped[int] = mapped_column(
        Sequence("country_id_seq"),
        primary_key=True,
        autoincrement=False,
        doc="ISO-3166 numeric code",
    )
    name: Mapped[str] = mapped_column(String(63))
    iso_alpha_2: Mapped[str] = mapped_column(String(2), doc="ISO-3166 alpha-2 code")
    iso_alpha_3: Mapped[str] = mapped_column(String(3), doc="ISO-3166 alpha-3 code")
    ioc_code: Mapped[str | None] = mapped_column(String(3), doc="International Olympic Committee’s 3-letter code")


# Configuration of teams and legs for an event
#
# Custom types should be added with an X_ prefix.
EventForm = enum.StrEnum("EventForm", ["INDIVIDUAL", "TEAM", "RELAY"])


class Event(Base, HasExternalIds):
    """Largest organisational unit to assign entries to

    An event can consist of one or multiple :py:class:`races <.Race>`.
    This occurs for multi-day events and for events with heats and
    finals. All races of an event must have the same form (e.g.
    individual or relay) and offer the same categories defined by
    :py:class:`~.EventCategory`.
    """

    event_id: Mapped[int] = mapped_column(Sequence("event_id_seq"), primary_key=True)
    external_ids: Mapped[list[EventXID]] = relationship("EventXID", back_populates="event")

    name: Mapped[str | None] = mapped_column(String(255))
    start_time: Mapped[datetime | None]
    end_time: Mapped[datetime | None]
    form: Mapped[EventForm] = mapped_column(Enum(EventForm), default=EventForm.INDIVIDUAL)

    races: Mapped[list[Race]] = relationship("Race", back_populates="event")
    event_categories: Mapped[list[EventCategory]] = relationship("EventCategory", back_populates="event")
    entries: Mapped[list[Entry]] = relationship("Entry", back_populates="event")


class EventXID(Base, ExternalId):
    event_id: Mapped[int] = mapped_column(ForeignKey("Event.event_id"))
    event: Mapped[Event] = relationship(Event, back_populates="external_ids")


Sex = enum.StrEnum("Sex", ["FEMALE", "MALE"])


EventCategoryStatus = enum.StrEnum(
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

    event_category_id: Mapped[int] = mapped_column(Sequence("event_category_id_seq"), primary_key=True)
    external_ids: Mapped[list[EventCategoryXID]] = relationship("EventCategoryXID", back_populates="event_category")

    event_id: Mapped[int | None] = mapped_column(ForeignKey(Event.event_id))
    event: Mapped[Event | None] = relationship(Event, back_populates="event_categories")
    name: Mapped[str] = mapped_column(String(32))
    short_name: Mapped[str | None] = mapped_column(String(8))
    status: Mapped[EventCategoryStatus] = mapped_column(
        Enum(EventCategoryStatus),
        default=EventCategoryStatus.NORMAL,
    )

    legs: Mapped[list[Leg]] = relationship("Leg", back_populates="event_category")
    entry_requests: Mapped[list[EntryCategoryRequest]] = relationship(
        "EntryCategoryRequest",
        back_populates="event_category",
    )

    ### restrictions ###

    min_age: Mapped[int | None] = mapped_column(SmallInteger)
    max_age: Mapped[int | None] = mapped_column(SmallInteger)
    sex: Mapped[Sex | None] = mapped_column(Enum(Sex))

    min_number_of_team_members: Mapped[int] = mapped_column(SmallInteger, default=1)
    max_number_of_team_members: Mapped[int] = mapped_column(SmallInteger, default=1)
    min_team_age: Mapped[int | None] = mapped_column(SmallInteger)
    max_team_age: Mapped[int | None] = mapped_column(SmallInteger)

    # In IOF XMLv3 this is called maxNumberOfCompetitors
    starter_limit: Mapped[int | None] = mapped_column(SmallInteger)


class EventCategoryXID(Base, ExternalId):
    event_category_id: Mapped[int] = mapped_column(
        ForeignKey("EventCategory.event_category_id"),
    )
    event_category: Mapped[EventCategory] = relationship(EventCategory, back_populates="external_ids")


class Race(Base):
    """Smallest organisational unit to assign entries to"""

    race_id: Mapped[int] = mapped_column(Sequence("race_id_seq"), primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(Event.event_id))
    event: Mapped[Event] = relationship(Event, back_populates="races")

    first_start: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    categories: Mapped[list[Category]] = relationship("Category", back_populates="race")
    controls: Mapped[list[Control]] = relationship("Control", back_populates="race")
    courses: Mapped[list[Course]] = relationship("Course", back_populates="race")

    @property
    def entries(self) -> list[Entry]:
        return self.event.entries


RaceCategoryStatus = enum.StrEnum(
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
    leg_id: Mapped[int] = mapped_column(Sequence("leg_id_seq"), primary_key=True)
    event_category_id: Mapped[int] = mapped_column(ForeignKey(EventCategory.event_category_id))
    event_category: Mapped[EventCategory] = relationship(EventCategory, back_populates="legs")

    leg_number: Mapped[int | None] = mapped_column(SmallInteger)

    # Number of competitors of each team that compete together in this leg
    min_number_of_competitors: Mapped[int] = mapped_column(SmallInteger, default=1)
    max_number_of_competitors: Mapped[int] = mapped_column(SmallInteger, default=1)


class Control(Base):
    control_id: Mapped[int] = mapped_column(Sequence("control_id_seq"), primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey(Race.race_id))
    race: Mapped[Race] = relationship(Race, back_populates="controls")
    label: Mapped[str] = mapped_column(String(16))

    UniqueConstraint("race_id", "label")


class Course(Base):
    course_id: Mapped[int] = mapped_column(Sequence("course_id_seq"), primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey(Race.race_id))
    race: Mapped[Race] = relationship(Race, back_populates="courses")

    name: Mapped[str] = mapped_column(String(16))
    length: Mapped[float | None] = mapped_column(doc="Course length in kilometers")
    climb: Mapped[float | None] = mapped_column(doc="Course climb in meters")

    controls: Mapped[list[CourseControl]] = relationship("CourseControl", back_populates="course")
    categories: Mapped[list[CategoryCourseAssignment]] = relationship(
        "CategoryCourseAssignment",
        back_populates="course",
    )


ControlType = enum.StrEnum(
    "ControlType",
    ["CONTROL", "START", "FINISH", "CROSSING_POINT", "END_OF_MARKED_ROUTE"],
)


class CourseControl(Base):
    course_control_id: Mapped[int] = mapped_column(Sequence("course_control_id_seq"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey(Course.course_id))
    course: Mapped[Course] = relationship(Course, back_populates="controls")
    control_id: Mapped[int] = mapped_column(ForeignKey(Control.control_id))
    control: Mapped[Control] = relationship(Control)

    leg_length: Mapped[float | None] = mapped_column(doc="Leg length in kilometers")

    type: Mapped[ControlType] = mapped_column(Enum(ControlType), default=ControlType.CONTROL)
    score: Mapped[float | None]
    order: Mapped[int | None] = mapped_column(
        doc="If a course control has a higher `order` than another, \
            it has to be punched after it.",
    )
    after_course_control_id: Mapped[int | None] = mapped_column(ForeignKey("CourseControl.course_control_id"))
    after: Mapped[Self | None] = relationship(
        "CourseControl",
        foreign_keys=[after_course_control_id],
        remote_side=course_control_id,
        doc="Control must be punched after this other control.",
    )
    before_course_control_id: Mapped[int | None] = mapped_column(ForeignKey("CourseControl.course_control_id"))
    before: Mapped[Self | None] = relationship(
        "CourseControl",
        foreign_keys=[before_course_control_id],
        remote_side=course_control_id,
        doc="Control must be punched before this other control.",
    )


class Category(Base):
    """Realize an EventCategory for one specific race of that event"""

    category_id: Mapped[int] = mapped_column(Sequence("category_id_seq"), primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey(Race.race_id))
    race: Mapped[Race] = relationship(Race, back_populates="categories")

    event_category_id: Mapped[int] = mapped_column(ForeignKey(EventCategory.event_category_id))
    event_category: Mapped[EventCategory] = relationship(EventCategory)

    status: Mapped[RaceCategoryStatus] = mapped_column(
        Enum(RaceCategoryStatus),
        default=RaceCategoryStatus.START_TIMES_NOT_ALLOCATED,
    )

    courses: Mapped[list[CategoryCourseAssignment]] = relationship(
        "CategoryCourseAssignment",
        back_populates="category",
    )

    time_offset: Mapped[timedelta | None] = mapped_column(doc="Start time offset from race start time")
    starts: Mapped[list[Start]] = relationship("Start", back_populates="category")
    vacancies_before: Mapped[int] = mapped_column(SmallInteger, default=0)
    vacancies_after: Mapped[int] = mapped_column(SmallInteger, default=0)

    # In IOF XMLv3 this is called maxNumberOfCompetitors
    starter_limit: Mapped[int | None] = mapped_column(SmallInteger)

    @property
    def name(self) -> str:
        return self.event_category.name

    @property
    def short_name(self) -> str:
        return self.event_category.short_name or self.event_category.name


class CategoryCourseAssignment(Base):
    category_id: Mapped[int] = mapped_column(ForeignKey(Category.category_id), primary_key=True)
    category: Mapped[Category] = relationship(Category, back_populates="courses")
    leg: Mapped[int] = mapped_column(SmallInteger, default=1, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey(Course.course_id))
    course: Mapped[Course] = relationship(Course, back_populates="categories")


### Entries ###


class Person(Base, HasExternalIds):
    person_id: Mapped[int] = mapped_column(Sequence("person_id_seq"), primary_key=True)
    external_ids: Mapped[list[PersonXID]] = relationship("PersonXID", back_populates="person")

    title: Mapped[str | None] = mapped_column(String(31))
    family_name: Mapped[str | None] = mapped_column(String(64))
    given_name: Mapped[str | None] = mapped_column(String(160))
    birth_date: Mapped[date | None]
    country_id: Mapped[int | None] = mapped_column(ForeignKey(Country.country_id))
    country: Mapped[Country | None] = relationship(Country)
    sex: Mapped[Sex | None] = mapped_column(Enum(Sex))


class PersonXID(Base, ExternalId):
    person_id: Mapped[int] = mapped_column(ForeignKey("Person.person_id"))
    person: Mapped[Person] = relationship(Person, back_populates="external_ids")


OrganisationType = enum.StrEnum(
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
    organisation_id: Mapped[int] = mapped_column(Sequence("organisation_id_seq"), primary_key=True)
    external_ids: Mapped[list[OrganisationXID]] = relationship("OrganisationXID", back_populates="organisation")

    name: Mapped[str] = mapped_column(String(255))
    short_name: Mapped[str | None] = mapped_column(String(32))
    country_id: Mapped[int | None] = mapped_column(ForeignKey(Country.country_id))
    country: Mapped[Country | None] = relationship(Country)
    type: Mapped[OrganisationType | None] = mapped_column(Enum(OrganisationType))


class OrganisationXID(Base, ExternalId):
    organisation_id: Mapped[int] = mapped_column(ForeignKey("Organisation.organisation_id"))
    organisation: Mapped[Organisation] = relationship(Organisation, back_populates="external_ids")


class Entry(Base, HasExternalIds):
    entry_id: Mapped[int] = mapped_column(Sequence("entry_id_seq"), primary_key=True)
    external_ids: Mapped[list[EntryXID]] = relationship("EntryXID", back_populates="entry")

    event_id: Mapped[int] = mapped_column(ForeignKey(Event.event_id))
    event: Mapped[Event] = relationship(Event, back_populates="entries")

    number: Mapped[int | None]
    name: Mapped[str | None] = mapped_column(String(255))
    competitors: Mapped[list[Competitor]] = relationship("Competitor", back_populates="entry")

    organisation_id: Mapped[int | None] = mapped_column(ForeignKey(Organisation.organisation_id))
    organisation: Mapped[Organisation | None] = relationship(Organisation)

    category_requests: Mapped[list[EntryCategoryRequest]] = relationship(
        "EntryCategoryRequest",
        back_populates="entry",
        doc="Requested categories with preference",
    )
    start_time_allocation_requests: Mapped[list[StartTimeAllocationRequest]] = relationship(
        "StartTimeAllocationRequest",
    )
    starts: Mapped[list[Start]] = relationship("Start", back_populates="entry")

    @property
    def races(self) -> list[Race]:
        # TODO: Allow participation in only some of the events races.
        return self.event.races


class EntryXID(Base, ExternalId):
    entry_id: Mapped[int] = mapped_column(ForeignKey("Entry.entry_id"))
    entry: Mapped[Entry] = relationship(Entry, back_populates="external_ids")


class EntryCategoryRequest(Base):
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id), primary_key=True)
    entry: Mapped[Entry] = relationship(Entry)
    preference: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        default=0,
        doc="Lower number means higher preference",
    )
    event_category_id: Mapped[int] = mapped_column(ForeignKey(EventCategory.event_category_id))
    event_category: Mapped[EventCategory] = relationship(EventCategory, back_populates="entry_requests")


StartTimeAllocationRequestType = enum.StrEnum(
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
    start_time_allocation_request_id: Mapped[int] = mapped_column(
        Sequence("start_time_allocation_request_id_seq"),
        primary_key=True,
    )
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id))
    entry: Mapped[Entry] = relationship(Entry, back_populates="start_time_allocation_requests")

    type: Mapped[StartTimeAllocationRequestType] = mapped_column(
        Enum(StartTimeAllocationRequestType),
        default=StartTimeAllocationRequestType.NORMAL,
    )
    organisation_id: Mapped[int | None] = mapped_column(ForeignKey(Organisation.organisation_id))
    organisation: Mapped[Organisation | None] = relationship(Organisation)
    person_id: Mapped[int | None] = mapped_column(ForeignKey(Person.person_id))
    person: Mapped[Person | None] = relationship(Person)


PunchingSystem = enum.StrEnum("PunchingSystem", ["SPORT_IDENT", "EMIT"])


class ControlCard(Base):
    control_card_id: Mapped[int] = mapped_column(Sequence("control_card_id_seq"), primary_key=True)
    system: Mapped[PunchingSystem | None] = mapped_column(Enum(PunchingSystem))
    label: Mapped[str | None] = mapped_column(String(16))


class Competitor(Base, HasExternalIds):
    competitor_id: Mapped[int] = mapped_column(Sequence("competitor_id_seq"), primary_key=True)
    external_ids: Mapped[list[CompetitorXID]] = relationship("CompetitorXID", back_populates="competitor")

    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id))
    entry: Mapped[Entry] = relationship(Entry, back_populates="competitors")

    entry_sequence: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        doc="1-based position of the competitor in the team",
    )
    leg_number: Mapped[int | None] = mapped_column(SmallInteger)
    leg_order: Mapped[int | None] = mapped_column(SmallInteger)

    person_id: Mapped[int] = mapped_column(ForeignKey(Person.person_id))
    person: Mapped[Person] = relationship(Person)

    organisation_id: Mapped[int | None] = mapped_column(ForeignKey(Organisation.organisation_id))
    organisation: Mapped[Organisation | None] = relationship(Organisation)

    control_cards: Mapped[list[ControlCard]] = relationship(
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

    starts: Mapped[list[CompetitorStart]] = relationship("CompetitorStart", back_populates="competitor")


class CompetitorXID(Base, ExternalId):
    competitor_id: Mapped[int] = mapped_column(ForeignKey("Competitor.competitor_id"))
    competitor: Mapped[Competitor] = relationship(Competitor, back_populates="external_ids")


### Starts ###


class Start(Base):
    start_id: Mapped[int] = mapped_column(Sequence("start_id_seq"), primary_key=True)
    result: Mapped[Result] = relationship("Result", uselist=False, back_populates="start")

    category_id: Mapped[int] = mapped_column(ForeignKey(Category.category_id))
    category: Mapped[Category] = relationship(Category, back_populates="starts")
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id))
    entry: Mapped[Entry] = relationship(Entry, back_populates="starts")

    competitive: Mapped[bool] = mapped_column(
        default=True,
        doc="Whether the starter is to be considered for the official ranking. \
        This can be set to `False` for example if the starter does not fulfill some entry requirement.",
    )
    time_offset: Mapped[timedelta | None] = mapped_column(doc="Start time offset from category start time")

    competitor_starts: Mapped[list[CompetitorStart]] = relationship("CompetitorStart", back_populates="start")


class CompetitorStart(Base):
    competitor_start_id: Mapped[int] = mapped_column(Sequence("competitor_start_id_seq"), primary_key=True)
    competitor_result: Mapped[CompetitorResult] = relationship(
        "CompetitorResult",
        uselist=False,
        back_populates="competitor_start",
    )

    start_id: Mapped[int] = mapped_column(ForeignKey(Start.start_id))
    start: Mapped[Start] = relationship(Start, back_populates="competitor_starts")
    competitor_id: Mapped[int] = mapped_column(ForeignKey(Competitor.competitor_id))
    competitor: Mapped[Competitor] = relationship(Competitor, back_populates="starts")

    time_offset: Mapped[timedelta | None] = mapped_column(doc="Start time offset from entry start time")
    control_card_id: Mapped[int | None] = mapped_column(ForeignKey(ControlCard.control_card_id))
    control_card: Mapped[ControlCard | None] = relationship(ControlCard)


### Results ###

ResultStatus = enum.StrEnum(
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
    result_id: Mapped[int] = mapped_column(ForeignKey(Start.start_id), primary_key=True)
    start: Mapped[Start] = relationship(Start, back_populates="result")

    start_time: Mapped[datetime | None] = mapped_column(doc="Actual start time used for placement")
    finish_time: Mapped[datetime | None] = mapped_column(doc="Actual finish time used for placement")

    time_adjustment: Mapped[timedelta] = mapped_column(doc="Time bonus or penalty")
    time: Mapped[timedelta | None]

    status: Mapped[ResultStatus | None] = mapped_column(Enum(ResultStatus))
    position: Mapped[int | None] = mapped_column(doc="Position in the category")


class CompetitorResult(Base):
    competitor_result_id: Mapped[int] = mapped_column(
        ForeignKey(CompetitorStart.competitor_start_id),
        primary_key=True,
    )
    competitor_start: Mapped[CompetitorStart] = relationship(CompetitorStart, back_populates="competitor_result")

    start_time: Mapped[datetime | None] = mapped_column(doc="Actual start time used for placement")
    finish_time: Mapped[datetime | None] = mapped_column(doc="Actual finish time used for placement")

    time_adjustment: Mapped[timedelta] = mapped_column(doc="Time bonus or penalty")
    time: Mapped[timedelta | None]

    status: Mapped[ResultStatus | None] = mapped_column(Enum(ResultStatus))


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
