from datetime import datetime
from typing import Annotated

from pydantic import constr
from pydantic_xml import attr, element
from typing_extensions import Doc

from .common import (
    AssignedFee,
    BaseMessageElement,
    Class,
    ControlCard,
    Event,
    Id,
    IOFBaseModel,
    Organisation,
    Person,
    ServiceRequest,
    SimpleCourse,
    SimpleRaceCourse,
)


class TeamMemberRaceStart(IOFBaseModel):
    """Start information for a team member in a race."""

    leg: Annotated[
        int | None,
        element(tag="Leg"),
        Doc("In case of a relay, this is the number of the leg that the team member takes part in."),
    ] = None
    leg_order: Annotated[
        int | None,
        element(tag="LegOrder"),
        Doc(
            "In case of a relay with parallel legs, this defines the team member's starting order of the leg within the team.",
        ),
    ] = None
    bib_number: Annotated[
        str | None,
        element(tag="BibNumber"),
        Doc("The bib number that the team member is wearing."),
    ] = None
    start_time: Annotated[
        datetime | None,
        element(tag="StartTime"),
        Doc("The time when the team member starts."),
    ] = None
    course: Annotated[
        SimpleCourse | None,
        element(tag="Course"),
        Doc("Defines the course assigned to the team member."),
    ] = None
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc(
            "Defines the control card assigned to the team member. Multiple control cards can be specified, e.g. one for punch checking and another for timing.",
        ),
    ] = []
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc("Defines the fees that the team member has been assigned."),
    ] = []
    service_requests: Annotated[
        list[ServiceRequest],
        element(tag="ServiceRequest"),
        Doc("Defines the services requested by the team member."),
    ] = []
    race_number: Annotated[
        int | None,
        attr(name="raceNumber"),
        Doc("The ordinal number of the race that the information belongs to for a multi-race event, starting at 1."),
    ] = None


class TeamMemberStart(IOFBaseModel):
    """Start information for an individual competitor, including e.g. start time and bib number."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this team member's entry in an EntryList."),
    ] = None
    person: Annotated[
        Person | None,
        element(tag="Person"),
        Doc("The team member that the start time belongs to."),
    ] = None
    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc("The organisation that the team member is representing at the event."),
    ] = None
    starts: Annotated[
        list[TeamMemberRaceStart],
        element(tag="Start"),
        Doc("The core start information for the team member; one element per race in the event."),
    ]
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class TeamStart(IOFBaseModel):
    """Start information for a team, including e.g. team name, start times and bib numbers."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this team's entry in an EntryList."),
    ] = None
    name: Annotated[
        str | None,
        element(tag="Name"),
        Doc(
            "The name of the team, e.g. organisation name and team number for a relay team. Omit if the team name is not know, e.g. a vacant team.",
        ),
    ] = None
    organisations: Annotated[
        list[Organisation],
        element(tag="Organisation"),
        Doc("The organisation(s) the team is representing."),
    ] = []
    bib_number: Annotated[
        str | None,
        element(tag="BibNumber"),
        Doc(
            "The bib number that the members of the team are wearing. If each team member has a unique bib number, use the BibNumber of the TeamMemberStart element.",
        ),
    ] = None
    team_member_starts: Annotated[
        list[TeamMemberStart],
        element(tag="TeamMemberStart"),
        Doc(
            "Information about the start times for the team members. One element per relay leg must be included, even if the team has not assigned any team member to the leg.",
        ),
    ] = []
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc("Defines the fees that the team has been assigned."),
    ] = []
    service_requests: Annotated[
        list[ServiceRequest],
        element(tag="ServiceRequest"),
        Doc("Defines the services requested by the team."),
    ] = []
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class PersonRaceStart(IOFBaseModel):
    """Start information for a person in a race."""

    bib_number: Annotated[
        str | None,
        element(tag="BibNumber"),
        Doc("The bib number that the person is wearing."),
    ] = None
    start_time: Annotated[datetime | None, element(tag="StartTime"), Doc("The time when the person starts.")] = None
    course: Annotated[
        SimpleCourse | None,
        element(tag="Course"),
        Doc("Defines the course assigned to the person."),
    ] = None
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc(
            "Defines the control cards assigned to the person. Multiple control cards can be specified, e.g. one for punch checking and another for timing.",
        ),
    ] = []
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc("Defines the fees that the person has been assigned."),
    ] = []
    service_requests: Annotated[
        list[ServiceRequest],
        element(tag="ServiceRequest"),
        Doc("Defines the services requested by the person."),
    ] = []
    race_number: Annotated[
        int | None,
        attr(name="raceNumber"),
        Doc("The ordinal number of the race that the information belongs to for a multi-race event, starting at 1."),
    ] = None


class PersonStart(IOFBaseModel):
    """Start information for an individual competitor, including e.g. start time and bib number."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this person's entry in an EntryList."),
    ] = None
    person: Annotated[
        Person | None,
        element(tag="Person"),
        Doc(
            "The person that the start time belongs to. Omit if there is no person assigned to the start time, e.g. a vacant person.",
        ),
    ] = None
    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc("The organisation that the person is representing at the event."),
    ] = None
    starts: Annotated[
        list[PersonRaceStart],
        element(tag="Start"),
        Doc("The core start information for the person; one element per race in the event."),
    ]
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class StartName(IOFBaseModel):
    text: Annotated[
        str,
        constr(strip_whitespace=True),
        Doc("Defines the name of the start place (e.g. Start 1), if the race has multiple start places."),
    ]
    race_number: Annotated[
        int | None,
        attr(name="raceNumber"),
        Doc("The ordinal number of the race that the information belongs to for a multi-race event, starting at 1."),
    ] = None


class ClassStart(IOFBaseModel):
    """The start list of a single class containing either individual start times or team start times."""

    class_: Annotated[Class, element(tag="Class"), Doc("The class that the start list belongs to.")]
    courses: Annotated[
        list[SimpleRaceCourse],
        element(tag="Course"),
        Doc(
            "Defines the course assigned to the class. If courses are unique per competitor, use PersonStart/Course or TeamStart/TeamMemberStart/Course instead. One element per race.",
        ),
    ] = []
    start_names: Annotated[
        list[StartName],
        element(tag="StartName"),
        Doc(
            "Defines the name of the start place (e.g. Start 1), if the race has multiple start places. One element per race.",
        ),
    ] = []
    person_starts: Annotated[
        list[PersonStart],
        element(tag="PersonStart"),
        Doc("Start times for individual competitors in the class."),
    ] = []
    team_starts: Annotated[list[TeamStart], element(tag="TeamStart"), Doc("Start times for teams in the class.")] = []
    time_resolution: Annotated[
        float | None,
        attr(name="timeResolution"),
        Doc("The time resolution of the start times, normally 1. For tenths of a second, use 0.1."),
    ] = 1
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class StartList(BaseMessageElement):
    """Contains information about the start lists for the classes in an event."""

    event: Annotated[Event, element(tag="Event"), Doc("The event that the start lists belong to.")]
    class_starts: Annotated[
        list[ClassStart],
        element(tag="ClassStart"),
        Doc("Start lists for the classes in the event."),
    ] = []
