import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import constr
from pydantic_xml import BaseXmlModel, attr, element
from typing_extensions import Doc

nsmap = {
    "": "http://www.orienteering.org/datastandard/3.0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


class IOFBaseModel(BaseXmlModel, nsmap=nsmap, search_mode="ordered"):
    """Config for all pydantic-xml model classes."""


class BaseMessageElement(IOFBaseModel):
    """The base message element that all message elements extend."""

    iof_version: Annotated[
        Literal["3.0"],
        attr(name="iofVersion"),
        Doc("The version of the IOF Interface Standard that the file conforms to."),
    ]
    create_time: Annotated[
        datetime.datetime | None,
        attr(name="createTime"),
        Doc("The time when the file was created."),
    ] = None
    creator: Annotated[str | None, attr(name="creator"), Doc("The name of the software that created the file.")] = None


class Id(IOFBaseModel):
    """Identifier element, used extensively. The id should be known and common for both systems taking part in the data exchange."""

    text: Annotated[str, constr(strip_whitespace=True)]
    type: Annotated[str | None, attr(name="type"), Doc("The issuer of the identity, e.g. World Ranking List.")] = None


class PersonName(IOFBaseModel):
    family: Annotated[str, element(tag="Family")]
    given: Annotated[str, element(tag="Given")]


class Country(IOFBaseModel):
    """Defines the name of the country."""

    text: Annotated[str, constr(strip_whitespace=True)]
    code: Annotated[
        str,
        attr(name="code"),
        Doc(
            "The International Olympic Committee's 3-letter code of the country as stated in http://en.wikipedia.org/wiki/List_of_IOC_country_codes. Note that several of the IOC codes are different from the standard ISO 3166-1 alpha-3 codes.",
        ),
    ]


class Address(IOFBaseModel):
    """The postal address of a person or organisation."""

    care_of: Annotated[str | None, element(tag="CareOf")] = None
    street: Annotated[str | None, element(tag="Street")] = None
    zip_code: Annotated[str | None, element(tag="ZipCode")] = None
    city: Annotated[str | None, element(tag="City")] = None
    state: Annotated[str | None, element(tag="State")] = None
    country: Annotated[Country | None, element(tag="Country")] = None
    type: Annotated[
        str | None,
        attr(name="type"),
        Doc("The address type, e.g. visitor address or invoice address."),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Contact(IOFBaseModel):
    """Contact information for a person, organisation or other entity."""

    text: Annotated[str, constr(strip_whitespace=True)]
    type: Annotated[
        Literal[
            "PhoneNumber",
            "MobilePhoneNumber",
            "FaxNumber",
            "EmailAddress",
            "WebAddress",
            "Other",
        ],
        attr(name="type"),
    ]
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Person(IOFBaseModel):
    """Represents a person. This could either be a competitor (see the Competitor element) or contact persons in an organisation (see the Organisation element)."""

    ids: Annotated[
        list[Id],
        element(tag="Id"),
        Doc(
            "The identifier of the person. Multiple identifiers can be included, e.g. when there is both a World Ranking Event identifier and a national database identifier for the person.",
        ),
    ] = []
    name: Annotated[PersonName, element(tag="Name")]
    birth_date: Annotated[
        datetime.date | None,
        element(tag="BirthDate"),
        Doc("The date when the person was born, expressed in ISO 8601 format."),
    ] = None
    nationality: Annotated[Country | None, element(tag="Nationality")] = None
    addresses: Annotated[list[Address], element(tag="Address")] = []
    contacts: Annotated[list[Contact], element(tag="Contact")] = []
    sex: Annotated[
        Literal[
            "F",
            "M",
        ]
        | None,
        attr(name="sex"),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class ControlCard(IOFBaseModel):
    """The unique identifier of the control card, i.e. card number."""

    text: Annotated[str, constr(strip_whitespace=True)]
    punching_system: Annotated[
        str | None,
        attr(name="punchingSystem"),
        Doc("The manufacturer of the punching system, e.g. 'SI' or 'Emit'."),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Score(IOFBaseModel):
    """The score earned in an event for some purpose, e.g. a ranking list. The 'type' attribute is used to specify which purpose."""

    value: Annotated[float, constr(strip_whitespace=True)]
    type: Annotated[str | None, attr(name="type")] = None


class GeoPosition(IOFBaseModel):
    """Defines a geographical position, e.g. of a control."""

    lng: Annotated[float, attr(name="lng"), Doc("The longitude.")]
    lat: Annotated[float, attr(name="lat"), Doc("The latitude.")]
    alt: Annotated[float | None, attr(name="alt"), Doc("The altitude (elevation above sea level), in meters.")] = None


class Role(IOFBaseModel):
    """A role defines a connection between a person and some kind of task, responsibility or engagement, e.g. being a course setter at an event."""

    person: Annotated[Person, element(tag="Person")]
    type: Annotated[str, attr(name="type"), Doc("The type of role that the person has.")]


class Account(IOFBaseModel):
    """The bank account of an organisation or an event."""

    text: Annotated[str, constr(strip_whitespace=True)]
    type: Annotated[str | None, attr(name="type"), Doc("The account type.")] = None


class Image(IOFBaseModel):
    base64: Annotated[
        bytes,
        constr(strip_whitespace=True),
        Doc("Defines an image file, either as a link (use the url attribute) or as base64-encoded binary data."),
    ]
    url: Annotated[
        str | None,
        attr(name="url"),
        Doc("The url to the image if it is stored externally (i.e. not as base64-encoded binary data)."),
    ] = None
    media_type: Annotated[
        str,
        attr(name="mediaType"),
        Doc(
            "The type of the image file, e.g. image/jpeg. Refer to http://en.wikipedia.org/wiki/Internet_media_type#Type_image for available media types.",
        ),
    ]
    width: Annotated[int | None, attr(name="width"), Doc("The width of the image in pixels.")] = None
    height: Annotated[int | None, attr(name="height"), Doc("The height of the image in pixels.")] = None
    resolution: Annotated[float | None, attr(name="resolution"), Doc("The resolution of the image in dpi.")] = None


class Organisation(IOFBaseModel):
    """Information about an organisation, i.e. address, contact person(s) etc. An organisation is a general term including federations, clubs, etc."""

    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[str, element(tag="Name"), Doc("The full name of the organisation.")]
    short_name: Annotated[
        str | None,
        element(tag="ShortName"),
        Doc("The short (abbreviated) name of the organisation."),
    ] = None
    media_name: Annotated[
        str | None,
        element(tag="MediaName"),
        Doc("The name of the organisation as appearing in result lists targeted to media."),
    ] = None
    parent_organisation_id: Annotated[
        int | None,
        element(tag="ParentOrganisationId"),
        Doc("The id of the parent of this organisation, e.g. a regional organisation for a club."),
    ] = None
    country: Annotated[Country | None, element(tag="Country")] = None
    addresses: Annotated[list[Address], element(tag="Address")] = []
    contacts: Annotated[list[Contact], element(tag="Contact")] = []
    position: Annotated[
        GeoPosition | None,
        element(tag="Position"),
        Doc("The geographical location of the organisation, e.g. a city center, an office or a club house."),
    ] = None
    accounts: Annotated[list[Account], element(tag="Account")] = []
    roles: Annotated[
        list[Role],
        element(tag="Role"),
        Doc("Persons having certain roles within the organisation, e.g. chairman, secretary, and treasurer."),
    ] = []
    logotypes: Annotated[
        list[Image],
        element(tag="Logotype"),
        Doc(
            "The logotype for the organisation. Multiple logotypes may be included; in this case, make sure to include width and height attributes.",
        ),
    ] = []
    type: Annotated[
        Literal[
            "IOF",
            "IOFRegion",
            "NationalFederation",
            "NationalRegion",
            "Club",
            "School",
            "Company",
            "Military",
            "Other",
        ]
        | None,
        attr(name="type"),
        Doc("The hierarchical level or type of an organisation."),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class DateAndOptionalTime(IOFBaseModel):
    """Defines a point in time which either is known by date and time, or just by date. May be used for event dates, when the event date is decided before the time of the first start."""

    date: Annotated[datetime.date, element(tag="Date"), Doc("The date part, expressed in ISO 8601 format.")]
    time: Annotated[
        datetime.time | None,
        element(tag="Time"),
        Doc("The time part, expressed in ISO 8601 format."),
    ] = None


#  Planned: The event or race is on a planning stadium and has not been submitted to any sanctioning body.
#  Applied: The organiser has submitted the event to the relevant sanctioning body.
#  Proposed: The organiser has bid on hosting the event or race as e.g. a championship.
#  Sanctioned: The event oc race meets the relevant requirements and will happen.
#  Canceled: The event or race has been canceled, e.g. due to weather conditions.
#  Rescheduled: The date of the event or race has changed. A new Event or Race element should be created in addition to the already existing element.
EventStatus = Literal[
    "Planned",
    "Applied",
    "Proposed",
    "Sanctioned",
    "Canceled",
    "Rescheduled",
]


EventClassification = Literal[
    "International",
    "National",
    "Regional",
    "Local",
    "Club",
]


EventForm = Literal[
    "Individual",
    "Team",
    "Relay",
]


class ClassType(IOFBaseModel):
    """Defines a class type, which is used to group classes in categories."""

    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[str, element(tag="Name"), Doc("The name of the class type.")]
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Leg(IOFBaseModel):
    """Defines extra information for a relay leg."""

    name: Annotated[str | None, element(tag="Name"), Doc("The name of the leg, if not sequentially named.")] = None
    min_number_of_competitors: Annotated[
        int | None,
        attr(name="minNumberOfCompetitors"),
        Doc("The minimum number of competitors in case of a parallel leg."),
    ] = 1
    max_number_of_competitors: Annotated[
        int | None,
        attr(name="maxNumberOfCompetitors"),
        Doc("The maximum number of competitors in case of a parallel leg."),
    ] = 1


class Amount(IOFBaseModel):
    """Defines a monetary amount."""

    value: Annotated[Decimal, constr(strip_whitespace=True)]
    currency: Annotated[str | None, attr(name="currency")] = None


class LanguageString(IOFBaseModel):
    """Defines a text that is given in a particular language."""

    text: Annotated[str, constr(strip_whitespace=True)]
    language: Annotated[
        str | None,
        attr(name="language"),
        Doc(
            "The ISO 639-1 two-letter code of the language as stated in http://www.loc.gov/standards/iso639-2/php/code_list.php.",
        ),
    ] = None


class Fee(IOFBaseModel):
    """A fee that applies when entering a class at a race or ordering a service."""

    id: Annotated[Id | None, element(tag="Id")] = None
    names: Annotated[
        list[LanguageString],
        element(tag="Name"),
        Doc("A describing name of the fee, e.g. 'Late entry fee'."),
    ]
    amount: Annotated[
        Amount | None,
        element(tag="Amount"),
        Doc(
            "The fee amount, optionally including currency code. This element must not be present if a Percentage element exists.",
        ),
    ] = None
    taxable_amount: Annotated[
        Amount | None,
        element(tag="TaxableAmount"),
        Doc(
            "The fee amount that is taxable, i.e. considered when calculating taxes for an event. This element must not be present if a Percentage element exists, or if an Amount element does not exist.",
        ),
    ] = None
    percentage: Annotated[
        float | None,
        element(tag="Percentage"),
        Doc(
            "The percentage to increase or decrease already existing fees in a fee list with. This element must not be present if an Amount element exists.",
        ),
    ] = None
    taxable_percentage: Annotated[
        float | None,
        element(tag="TaxablePercentage"),
        Doc(
            "The percentage to increase or decrease already existing taxable fees in a fee list with. This element must not be present if an Amount element exists, or if a Percentage element does not exist.",
        ),
    ] = None
    valid_from_time: Annotated[
        datetime.datetime | None,
        element(tag="ValidFromTime"),
        Doc("The time when the fee takes effect."),
    ] = None
    valid_to_time: Annotated[
        datetime.datetime | None,
        element(tag="ValidToTime"),
        Doc("The time when the fee expires."),
    ] = None
    from_date_of_birth: Annotated[
        datetime.date | None,
        element(tag="FromDateOfBirth"),
        Doc(
            "The start of the birth date interval that the fee should be applied to. Omit if no lower birth date restriction.",
        ),
    ] = None
    to_date_of_birth: Annotated[
        datetime.date | None,
        element(tag="ToDateOfBirth"),
        Doc(
            "The end of the birth date interval that the fee should be applied to. Omit if no upper birth date restriction.",
        ),
    ] = None
    type: Annotated[
        Literal[
            "Normal",
            "Late",
        ]
        | None,
        attr(name="type"),
        Doc(
            """The type of fee.

        Normal: The fee is a normal fee (i.e. not a late entry fee).
        Late: Te fee is a late entry fee.""",
        ),
    ] = "Normal"
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


# The status of the class.
#
#  Normal: The default status.
#  Divided: The class has been divided in two or more classes due to a large number of entries.
#  Joined: The class has been joined with another class due to a small number of entries.
#  Invalidated: The results are considered invalid due to technical issues such as misplaced controls. Entry fees are not refunded.
#  InvalidatedNoFee: The results are considered invalid due to technical issues such as misplaced controls. Entry fees are refunded.
EventClassStatus = Literal[
    "Normal",
    "Divided",
    "Joined",
    "Invalidated",
    "InvalidatedNoFee",
]

# The status of a certain race in the class.
#
#  StartTimesNotAllocated: The start list draw has not been made for this class in this race.
#  StartTimesAllocated: The start list draw has been made for this class in this race.
#  NotUsed: The class is not organised in this race, e.g. for classes that are organised in only some of the races in a multi-race event.
#  Completed: The result list is complete for this class in this race.
#  Invalidated: The results are considered invalid due to technical issues such as misplaced controls. Entry fees are not refunded.
#  InvalidatedNoFee: The results are considered invalid due to technical issues such as misplaced controls. Entry fees are refunded.
RaceClassStatus = Literal[
    "StartTimesNotAllocated",
    "StartTimesAllocated",
    "NotUsed",
    "Completed",
    "Invalidated",
    "InvalidatedNoFee",
]


class SimpleCourse(IOFBaseModel):
    """Defines a course, excluding controls."""

    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[str | None, element(tag="Name"), Doc("The name of the course.")] = None
    course_family: Annotated[
        str | None,
        element(tag="CourseFamily"),
        Doc("The family or group of forked courses that the course is part of."),
    ] = None
    length: Annotated[float | None, element(tag="Length"), Doc("The length of the course, in meters.")] = None
    climb: Annotated[
        float | None,
        element(tag="Climb"),
        Doc("The climb of the course, in meters, along the expected best route choice."),
    ] = None
    number_of_controls: Annotated[
        int | None,
        element(tag="NumberOfControls"),
        Doc("The number of controls in the course, excluding start and finish."),
    ] = None


class MapPosition(IOFBaseModel):
    """Defines a position in a map's coordinate system."""

    x: Annotated[float, attr(name="x"), Doc("The number of units right of the center of the coordinate system.")]
    y: Annotated[float, attr(name="y"), Doc("The number of units below the center of the coordinate system.")]
    unit: Annotated[
        Literal[
            "px",
            "mm",
        ]
        | None,
        attr(name="unit"),
        Doc(
            """The type of unit used.
        px: Pixels, used when the map is represented by a digital image.
        mm: Millimeters, used when the map is represented by a printed piece of paper.""",
        ),
    ] = "mm"


# The type of a control: (ordinary) control, start, finish, crossing point or end of marked route.
ControlType = Literal[
    "Control",
    "Start",
    "Finish",
    "CrossingPoint",
    "EndOfMarkedRoute",
]


class Control(IOFBaseModel):
    """Defines a control, without any relationship to a particular course."""

    id: Annotated[Id | None, element(tag="Id"), Doc("The code of the control.")] = None
    punching_unit_ids: Annotated[
        list[Id],
        element(tag="PunchingUnitId"),
        Doc(
            "If the control has multiple punching units with separate codes, specify all these codes using elements of this kind. Omit this element if there is a single punching unit whose code is the same as the control code.",
        ),
    ] = []
    names: Annotated[
        list[LanguageString],
        element(tag="Name"),
        Doc("The name of the control, used for e.g. online controls ('spectator control', 'prewarning')."),
    ] = []
    position: Annotated[
        GeoPosition | None,
        element(tag="Position"),
        Doc("The geographical position of the control."),
    ] = None
    map_position: Annotated[
        MapPosition | None,
        element(tag="MapPosition"),
        Doc("The position of the control according to tha map's coordinate system."),
    ] = None
    type: Annotated[
        ControlType | None,
        attr(name="type"),
        Doc(
            "The type of the control: (ordinary) control, start, finish, crossing point or end of marked route. This attribute can be overridden on the CourseControl level.",
        ),
    ] = "Control"
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class RaceClass(IOFBaseModel):
    """Information about a class with respect to a race."""

    punching_systems: Annotated[
        list[str],
        element(tag="PunchingSystem"),
        Doc(
            "The punching system used for the class at the race. Multiple punching systems can be specified, e.g. one for punch checking and another for timing.",
        ),
    ] = []
    team_fees: Annotated[
        list[Fee],
        element(tag="TeamFee"),
        Doc(
            "The entry fees for a team as a whole taking part in this class. Use the Fee element to specify a fee for an individual competitor in the team. Use the TeamFee subelement of the Class element to specify a fee on event level.",
        ),
    ] = []
    fees: Annotated[
        list[Fee],
        element(tag="Fee"),
        Doc(
            "The entry fees for an individual competitor taking part in the race class. Use the TeamFee element to specify a fee for the team as a whole. Use the Fee subelement of the Class element to specify a fee on event level.",
        ),
    ] = []
    first_start: Annotated[datetime.datetime | None, element(tag="FirstStart")] = None
    status: Annotated[
        RaceClassStatus | None,
        element(tag="Status"),
        Doc("The status of the race, e.g. if results should be considered invalid due to misplaced constrols."),
    ] = None
    courses: Annotated[
        list[SimpleCourse],
        element(tag="Course"),
        Doc(
            "The courses assigned to this class. For a mass-start event or a relay event, there are usually multiple courses per class due to the usage of spreading methods.",
        ),
    ] = []
    online_controls: Annotated[
        list[Control],
        element(tag="OnlineControl"),
        Doc("The controls that are online controls for this class."),
    ] = []
    race_number: Annotated[
        int | None,
        attr(name="raceNumber"),
        Doc("The ordinal number of the race that the information belongs to for a multi-race event, starting at 1."),
    ] = None
    max_number_of_competitors: Annotated[
        int | None,
        attr(name="maxNumberOfCompetitors"),
        Doc(
            "The maximum number of competitors that are allowed to take part in the race class. A competitor corresponds to a person (if an individual event) or a team (if a team or relay event). This attribute overrides the maxNumberOfCompetitors attribute in the Class element.",
        ),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


RaceDiscipline = Literal[
    "Sprint",
    "Middle",
    "Long",
    "Ultralong",
    "Other",
]


class Service(IOFBaseModel):
    """Defines a general purpose service request, e.g. for rental card or accomodation."""

    id: Annotated[Id | None, element(tag="Id")] = None
    names: Annotated[list[LanguageString], element(tag="Name"), Doc("The name of the service.")]
    fees: Annotated[list[Fee], element(tag="Fee"), Doc("The fees attached to this service.")] = []
    descriptions: Annotated[
        list[LanguageString],
        element(tag="Description"),
        Doc("A further description of the service than the Name element gives."),
    ] = []
    max_number: Annotated[
        float | None,
        element(tag="MaxNumber"),
        Doc(
            "The maximum number of instances of this service that are available. Omit this element if there is no such limit.",
        ),
    ] = None
    requested_number: Annotated[
        float | None,
        element(tag="RequestedNumber"),
        Doc("The number of instances of this service that has been requested."),
    ] = None
    type: Annotated[
        str | None,
        attr(name="type"),
        Doc("Used to mark special services, e.g. rental cards whose fees that are to be used in entry scenarios."),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class EventURL(IOFBaseModel):
    text: Annotated[str, constr(strip_whitespace=True)]
    type: Annotated[
        Literal[
            "Website",
            "StartList",
            "ResultList",
            "Other",
        ],
        attr(name="type"),
    ]


class Race(IOFBaseModel):
    """An event consists of a number of races. The number is equal to the number of times a competitor should start."""

    race_number: Annotated[
        int,
        element(tag="RaceNumber"),
        Doc("The ordinal number of the race in the multi-race event, starting at 1."),
    ]
    name: Annotated[str, element(tag="Name")]
    start_time: Annotated[
        DateAndOptionalTime | None,
        element(tag="StartTime"),
        Doc("The start time for the first starting competitor of the race."),
    ] = None
    end_time: Annotated[
        DateAndOptionalTime | None,
        element(tag="EndTime"),
        Doc("The time when the finish closes."),
    ] = None
    status: Annotated[
        EventStatus | None,
        element(tag="Status"),
        Doc("The status of the race. This element overrides the Status element of the parent Event element."),
    ] = None
    classification: Annotated[
        EventClassification | None,
        element(tag="Classification"),
        Doc(
            "The classification or level of the race. This element overrides the Classification element of the parent Event element.",
        ),
    ] = None
    position: Annotated[
        GeoPosition | None,
        element(tag="Position"),
        Doc("The geographical location of the arena."),
    ] = None
    disciplines: Annotated[list[RaceDiscipline], element(tag="Discipline")] = []
    organisers: Annotated[
        list[Organisation],
        element(tag="Organiser"),
        Doc("The organisations that organise the event."),
    ] = []
    officials: Annotated[
        list[Role],
        element(tag="Official"),
        Doc("The main officials of the event, e.g. course setter and event president."),
    ] = []
    services: Annotated[
        list[Service],
        element(tag="Service"),
        Doc("The services available for the race, e.g. accomodation and transport."),
    ] = []
    urls: Annotated[
        list[EventURL],
        element(tag="URL"),
        Doc("URLs to various types of additional information regarding the event, e.g. event website or result list."),
    ] = []
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class EntryReceiver(IOFBaseModel):
    addresses: Annotated[list[Address], element(tag="Address")] = []
    contacts: Annotated[list[Contact], element(tag="Contact")] = []


class InformationItem(IOFBaseModel):
    """Defines a general-purpose information object containing a title and content."""

    title: Annotated[str, element(tag="Title"), Doc("A short summary of the information.")]
    content: Annotated[str, element(tag="Content"), Doc("The information in detailed form.")]
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Schedule(IOFBaseModel):
    """Defines the schedule of sub-events that comprise the entire orienteering event, e.g. banquets, social events and awards ceremonies."""

    start_time: Annotated[datetime.datetime, element(tag="StartTime"), Doc("The start time of the sub-event.")]
    end_time: Annotated[datetime.datetime | None, element(tag="EndTime"), Doc("The end time of the sub-event.")] = None
    name: Annotated[str, element(tag="Name"), Doc("The name or title of the sub-event.")]
    venue: Annotated[str | None, element(tag="Venue"), Doc("The name of the place where the sub-event occurs.")] = None
    position: Annotated[
        GeoPosition | None,
        element(tag="Position"),
        Doc("The geographical position of the sub-event."),
    ] = None
    details: Annotated[str | None, element(tag="Details"), Doc("Any extra information about the sub-event.")] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Class(IOFBaseModel):
    """Defines a class in an event."""

    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[str, element(tag="Name"), Doc("The name of the class.")]
    short_name: Annotated[
        str | None,
        element(tag="ShortName"),
        Doc("The abbreviated name of a class, used when space is limited."),
    ] = None
    class_types: Annotated[list[ClassType], element(tag="ClassType"), Doc("The class type(s) for the class.")] = []
    legs: Annotated[
        list[Leg],
        element(tag="Leg"),
        Doc("Information about the legs, if the class is a relay class. One Leg element per leg must be present."),
    ] = []
    team_fees: Annotated[
        list[Fee],
        element(tag="TeamFee"),
        Doc(
            "The entry fees for a team as a whole taking part in this class. Use the Fee element to specify a fee for an individual competitor in the team. Use the TeamFee subelement of the RaceClass element to specify a fee on race level.",
        ),
    ] = []
    fees: Annotated[
        list[Fee],
        element(tag="Fee"),
        Doc(
            "The entry fees for an individual competitor taking part in the class. Use the TeamFee element to specify a fee for the team as a whole. Use the Fee subelement of the RaceClass element to specify a fee on race level.",
        ),
    ] = []
    status: Annotated[
        EventClassStatus,
        element(tag="Status"),
        Doc(
            "The overall status of the class, e.g. if overall results should be considered invalid due to misplaced controls.",
        ),
    ] = "Normal"
    race_classes: Annotated[
        list[RaceClass],
        element(tag="RaceClass"),
        Doc("Race-specific information for the class, e.g. course(s) assigned to the class."),
    ] = []
    too_few_entries_substitute_class: Annotated[
        "Class | None",
        element(tag="TooFewEntriesSubstituteClass"),
        Doc(
            "The class that competitors in this class should be transferred to if there are too few entries in this class.",
        ),
    ] = None
    too_many_entries_substitute_class: Annotated[
        "Class | None",
        element(tag="TooManyEntriesSubstituteClass"),
        Doc(
            "The class that competitors that are not qualified (e.g. due to too low ranking) should be transferred to if there are too many entries in this class.",
        ),
    ] = None
    min_age: Annotated[
        int | None,
        attr(name="minAge"),
        Doc("The lowest allowed age for a competitor taking part in the class."),
    ] = None
    max_age: Annotated[
        int | None,
        attr(name="maxAge"),
        Doc("The highest allowed age for a competitor taking part in the class."),
    ] = None
    sex: Annotated[
        Literal[
            "B",
            "F",
            "M",
        ]
        | None,
        attr(name="sex"),
    ] = "B"
    min_number_of_team_members: Annotated[
        int | None,
        attr(name="minNumberOfTeamMembers"),
        Doc("The minimum number of members in a team taking part in the class, if the class is a team class."),
    ] = 1
    max_number_of_team_members: Annotated[
        int | None,
        attr(name="maxNumberOfTeamMembers"),
        Doc("The maximum number of members in a team taking part in the class, if the class is a team class."),
    ] = 1
    min_team_age: Annotated[
        int | None,
        attr(name="minTeamAge"),
        Doc("The lowest allowed age sum of the team members for a team taking part in the class."),
    ] = None
    max_team_age: Annotated[
        int | None,
        attr(name="maxTeamAge"),
        Doc("The highest allowed age sum of the team members for a team taking part in the class."),
    ] = None
    number_of_competitors: Annotated[
        int | None,
        attr(name="numberOfCompetitors"),
        Doc(
            "The number of competitors in the class. A competitor corresponds to a person (if an individual event) or a team (if a team or relay event).",
        ),
    ] = None
    max_number_of_competitors: Annotated[
        int | None,
        attr(name="maxNumberOfCompetitors"),
        Doc(
            "The maximum number of competitors that are allowed to take part in the class. A competitor corresponds to a person (if an individual event) or a team (if a team or relay event). If the maximum number of competitors varies between races in a multi-day event, use the maxNumberOfCompetitors attribute in the RaceClass element.",
        ),
    ] = None
    result_list_mode: Annotated[
        Literal[
            "Default",
            "Unordered",
            "UnorderedNoTimes",
        ]
        | None,
        attr(name="resultListMode"),
        Doc(
            """Defines the kind of information to include in the result list, and how to sort it. For example, the result list of a beginner's class may include just "finished" or "did not finish" instead of the actual times.

        Default: The result list should include place and time for each competitor, and be ordered by place.
        Unordered: The result list should include place and time for each competitor, but be unordered with respect to times (e.g. sorted by competitor name).
        UnorderedNoTimes: The result list should not include any places and times, and be unordered with respect to times (e.g. sorted by competitor name).""",
        ),
    ] = "Default"
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class Event(IOFBaseModel):
    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[str, element(tag="Name")]
    start_time: Annotated[
        DateAndOptionalTime | None,
        element(tag="StartTime"),
        Doc(
            "The start time for the first starting competitor of the event. If the event contains multiple races, this is the start time for the first starting competitor of the first race.",
        ),
    ] = None
    end_time: Annotated[
        DateAndOptionalTime | None,
        element(tag="EndTime"),
        Doc(
            "The expected finish time for the last finishing competitor of the event. If the event contains multiple races, this is the expected finish time for the last finishing competitor of the last race.",
        ),
    ] = None
    status: Annotated[
        EventStatus | None,
        element(tag="Status"),
        Doc(
            "The status of the event. If the event is a multi-race event, and status is set per race, use the Status element of the Race element.",
        ),
    ] = None
    classification: Annotated[
        EventClassification | None,
        element(tag="Classification"),
        Doc(
            "The classification or level of the event. If the event is a multi-race event, and classification is set per race, use the Classification element of the Race element.",
        ),
    ] = None
    forms: Annotated[list[EventForm], element(tag="Form")] = []
    organisers: Annotated[
        list[Organisation],
        element(tag="Organiser"),
        Doc("The organisations that organise the event."),
    ] = []
    officials: Annotated[
        list[Role],
        element(tag="Official"),
        Doc("The main officials of the event, e.g. course setter and event president."),
    ] = []
    classes: Annotated[list[Class], element(tag="Class"), Doc("The classes that are available at the event.")] = []
    races: Annotated[
        list[Race],
        element(tag="Race"),
        Doc(
            "An event consists of a number of races. The number is equal to the number of times a competitor should start. Most events contain a single race, and this elemend could then be omitted.",
        ),
    ] = []
    entry_receiver: Annotated[
        EntryReceiver | None,
        element(tag="EntryReceiver"),
        Doc("Address and contact information to the person or organisation which registers the entries for the event."),
    ] = None
    services: Annotated[
        list[Service],
        element(tag="Service"),
        Doc("The services available for the event, e.g. accomodation and transport."),
    ] = []
    accounts: Annotated[list[Account], element(tag="Account"), Doc("The bank account for the event.")] = []
    urls: Annotated[
        list[EventURL],
        element(tag="URL"),
        Doc("URLs to various types of additional information regarding the event, e.g. event website or result list."),
    ] = []
    information: Annotated[
        list[InformationItem],
        element(tag="Information"),
        Doc(
            """Presents arbitrary data about the event, e.g. "Accommodation", "Local Attractions", and so on. Information present here should be defined well in advance of the event, in contrast to the 'News' element.""",
        ),
    ] = []
    schedules: Annotated[
        list[Schedule],
        element(tag="Schedule"),
        Doc(
            "Defines the schedule of events that comprise the entire orienteering event, e.g. entry deadlines, banquet and social events, and awards ceremonies.",
        ),
    ] = []
    news: Annotated[
        list[InformationItem],
        element(tag="News"),
        Doc("""Presents "last minute information" about the event."""),
    ] = []
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class AssignedFee(IOFBaseModel):
    """Contains information about a fee that has been assigned to a competitor or a team, and the amount that has been paid."""

    fee: Annotated[Fee, element(tag="Fee"), Doc("The fee that has been assigned to the competitor or the team.")]
    paid_amount: Annotated[
        Amount | None,
        element(tag="PaidAmount"),
        Doc("The amount that has been paid, optionally including currency code."),
    ] = None
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None


class SimpleRaceCourse(SimpleCourse):
    """Defines a course for a certain race, excluding controls."""

    race_number: Annotated[
        int | None,
        attr(name="raceNumber"),
        Doc("The ordinal number of the race that the information belongs to for a multi-race event, starting at 1."),
    ] = None


class ServiceRequest(IOFBaseModel):
    id: Annotated[Id | None, element(tag="Id")] = None
    service: Annotated[Service, element(tag="Service"), Doc("The service that is requested.")]
    requested_quantity: Annotated[
        float,
        element(tag="RequestedQuantity"),
        Doc("The quantity (number of instances) of the service that is requested."),
    ]
    delivered_quantity: Annotated[
        float | None,
        element(tag="DeliveredQuantity"),
        Doc(
            "The quantity (number of instances) of the service that has been delivered. Can differ from RequestedQuantity when the available number of instances of a service is limited.",
        ),
    ] = None
    comment: Annotated[
        str | None,
        element(tag="Comment"),
        Doc("Any extra information or comment attached to the service request."),
    ] = None
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc("The fees related to this service request."),
    ] = []
    modify_time: Annotated[datetime.datetime | None, attr(name="modifyTime")] = None
