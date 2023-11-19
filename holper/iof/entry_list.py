from datetime import datetime
from typing import Annotated, Literal

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
    Score,
    ServiceRequest,
)


class StartTimeAllocationRequest(IOFBaseModel):
    """Used to state start time allocation requests. It consists of a possible reference Organisation or Person and the allocation request, e.g. late start or grouped with the reference Organisation/Person. This way it is possible to state requests to the event organizer so that e.g. all members of an organisation has start times close to each other - or parents have start times far from each other. It is totally up to the event software and organizers whether they will support such requests."""

    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc("The reference organisation for the start time allocation request."),
    ] = None
    person: Annotated[
        Person | None,
        element(tag="Person"),
        Doc("The reference person for the start time allocation request."),
    ] = None
    type: Annotated[
        Literal[
            "Normal",
            "EarlyStart",
            "LateStart",
            "SeparatedFrom",
            "GroupedWith",
        ]
        | None,
        attr(name="type"),
        Doc(
            """The type of start time allocation request.

        Normal: No special preference; use normal start time allocations.
        EarlyStart: The competitor preferences an early start time.
        LateStart: The competitor preferences a late start time.
        SeparatedFrom: The competitor preferences to start well separated in time from the person or organisation that is given by the Person or Organisation element.
        GroupedWith: The competitor preferences to start close in time from the person or organisation that is given by the Person or Organisation element.""",
        ),
    ] = "Normal"


class PersonEntry(IOFBaseModel):
    """Defines an event entry for a person."""

    id: Annotated[Id | None, element(tag="Id")] = None
    person: Annotated[Person, element(tag="Person"), Doc("The person that is entered.")]
    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc("The organisation that the person represents at the event."),
    ] = None
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc(
            "Information about the control cards (punching cards) that the person uses at the event. Multiple control cards can be specified, e.g. one for punch checking and another for timing.",
        ),
    ] = []
    scores: Annotated[
        list[Score],
        element(tag="Score"),
        Doc("Any score that is submitted together with the entry, e.g. World Ranking points."),
    ] = []
    classes: Annotated[
        list[Class],
        element(tag="Class"),
        Doc(
            "The class(es) the person wants to take part in. Multiple classes may be provided in order of preference in scenarios where the number of competitors are limited in some classes.",
        ),
    ] = []
    race_numbers: Annotated[
        list[int],
        element(tag="RaceNumber"),
        Doc(
            "The ordinal numbers of the races that the person is taking part in, starting at 1. If not specified, the person takes part in all races.",
        ),
    ] = []
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc(
            "The fees that the person has to pay when entering the event. In a multi-race event, there is usually one element for each race.",
        ),
    ] = []
    service_requests: Annotated[
        list[ServiceRequest],
        element(tag="ServiceRequest"),
        Doc("Defines the services requested by the person."),
    ] = []
    start_time_allocation_request: Annotated[
        StartTimeAllocationRequest | None,
        element(tag="StartTimeAllocationRequest"),
        Doc(
            "Any special preferences regarding start time that has to be taken into consideration when making the start list draw.",
        ),
    ] = None
    entry_time: Annotated[
        datetime | None,
        element(tag="EntryTime"),
        Doc("The time when the entry was first submitted."),
    ] = None
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class TeamEntryPerson(IOFBaseModel):
    """Defines a person that is part of a team entry."""

    person: Annotated[
        Person | None,
        element(tag="Person"),
        Doc("The person. Omit if the person is not known at the moment, but for example the control card is known."),
    ] = None
    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc(
            "The organisation that the person represent. Omit if this is the same as the organsiation given in the TeamEntry element.",
        ),
    ] = None
    leg: Annotated[
        int | None,
        element(tag="Leg"),
        Doc("For relay entries, the number of the leg that this person is taking part in."),
    ] = None
    leg_order: Annotated[
        int | None,
        element(tag="LegOrder"),
        Doc("Defines the person's starting order within a team at a parallel relay leg."),
    ] = None
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc(
            "Information about the control cards (punching cards) that the person uses at the event. Multiple control cards can be specified, e.g. one for punch checking and another for timing.",
        ),
    ] = []
    scores: Annotated[
        list[Score],
        element(tag="Score"),
        Doc("Any score that is submitted together with the entry, e.g. World Ranking points."),
    ] = []
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc(
            "The fees that this particular person has to pay when entering the event. In a multi-race event, there is usually one element for each race. Fees assigned to the team as a whole should be defined in the TeamEntry element.",
        ),
    ] = []


class TeamEntry(IOFBaseModel):
    """Defines an event entry for a team."""

    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[
        str,
        element(tag="Name"),
        Doc(
            "The name of the team. If a relay, this is probably the name of the club optionally followed by a sequence number to distinguish teams from the same club in a class.",
        ),
    ]
    organisations: Annotated[
        list[Organisation],
        element(tag="Organisation"),
        Doc("The organisation(s) that the team represents."),
    ] = []
    team_entry_persons: Annotated[
        list[TeamEntryPerson],
        element(tag="TeamEntryPerson"),
        Doc("The persons that make up the team."),
    ] = []
    classes: Annotated[
        list[Class],
        element(tag="Class"),
        Doc(
            "The class(es) the team wants to take part in. Multiple classes may be provided in order of preference in scenarios where the number of competitors are limited in some classes.",
        ),
    ] = []
    races: Annotated[
        list[int],
        element(tag="Race"),
        Doc(
            "The numbers of the races that the team is taking part in. If not specified, team person takes part in all races.",
        ),
    ] = []
    assigned_fees: Annotated[
        list[AssignedFee],
        element(tag="AssignedFee"),
        Doc(
            "The fees that the team as a whole has to pay when entering the event. In a multi-race event, there is usually one element for each race. If there are differentated fees for the team members, specify them in the TeamEntryPerson elements.",
        ),
    ] = []
    service_requests: Annotated[
        list[ServiceRequest],
        element(tag="ServiceRequest"),
        Doc("Defines the services requested by the team."),
    ] = []
    start_time_allocation_request: Annotated[
        StartTimeAllocationRequest | None,
        element(tag="StartTimeAllocationRequest"),
        Doc(
            "Any special preferences regarding start time that has to be taken into consideration when making the start list draw.",
        ),
    ] = None
    contact_information: Annotated[
        str | None,
        element(tag="ContactInformation"),
        Doc(
            "Contact information (name and e.g. mobile phone number) to a team leader or coach, expressed as plain text.",
        ),
    ] = None
    entry_time: Annotated[
        datetime | None,
        element(tag="EntryTime"),
        Doc("The time when the entry was first submitted."),
    ] = None
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class EntryList(BaseMessageElement):
    """A list of persons and/or teams which are registered for a particular event."""

    event: Annotated[Event, element(tag="Event"), Doc("The event that the entry list belongs to.")]
    team_entries: Annotated[list[TeamEntry], element(tag="TeamEntry"), Doc("The teams registered for the event.")] = []
    person_entries: Annotated[
        list[PersonEntry],
        element(tag="PersonEntry"),
        Doc("The individual competitors registered for the event."),
    ] = []
