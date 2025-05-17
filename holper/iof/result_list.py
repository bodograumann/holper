from datetime import datetime
from typing import Annotated, Literal

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
    Score,
    ServiceRequest,
    SimpleCourse,
    SimpleRaceCourse,
)


class SplitTime(IOFBaseModel):
    """Defines a split time at a control."""

    control_code: Annotated[str, element(tag="ControlCode"), Doc("The code of the control.")]
    time: Annotated[
        float | None,
        element(tag="Time"),
        Doc(
            "The time, in seconds, elapsed from start to punching the control. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None
    status: Annotated[
        Literal[
            "OK",
            "Missing",
            "Additional",
        ],
        attr(name="status"),
        Doc(
            """
        The status of the split time.

        OK: Control belongs to the course and has been punched (either by electronical punching or pin punching). If the time is not available or invalid, omit the Time element.
        Missing: Control belongs to the course but has not been punched.
        Additional: Control does not belong to the course, but the competitor has punched it.""",
        ),
    ] = "OK"


# The result status of the person or team at the time of the result generation.
#
#  OK: Finished and validated.
#  Finished: Finished but not yet validated.
#  MissingPunch: Missing punch.
#  Disqualified: Disqualified (for some other reason than a missing punch).
#  DidNotFinish: Did not finish (i.e. conciously cancelling the race after having started, in contrast to MissingPunch).
#  Active: Currently on course.
#  Inactive: Has not yet started.
#  OverTime: Overtime, i.e. did not finish within the maximum time set by the organiser.
#  SportingWithdrawal: Sporting withdrawal (e.g. helping an injured competitor).
#  NotCompeting: Not competing (i.e. running outside the competition).
#  Moved: Moved to another class.
#  MovedUp: Moved to a "better" class, in case of entry restrictions.
#  DidNotStart: Did not start (in this race).
#  DidNotEnter: Did not enter (in this race).
#  Cancelled: The competitor has cancelled his/hers entry.
ResultStatus = Literal[
    "OK",
    "Finished",
    "MissingPunch",
    "Disqualified",
    "DidNotFinish",
    "Active",
    "Inactive",
    "OverTime",
    "SportingWithdrawal",
    "NotCompeting",
    "Moved",
    "MovedUp",
    "DidNotStart",
    "DidNotEnter",
    "Cancelled",
]


class OverallResult(IOFBaseModel):
    time: Annotated[
        float | None,
        element(tag="Time"),
        Doc(
            "The time, in seconds, that is shown in the result list. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None
    time_behind: Annotated[
        float | None,
        element(tag="TimeBehind"),
        Doc(
            "The time, in seconds, that the the person or team is behind the leader or winner. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None
    position: Annotated[
        int | None,
        element(tag="Position"),
        Doc(
            "The position in the result list for the person or team that the result belongs to. This element should only be present when the Status element is set to OK.",
        ),
    ] = None
    status: Annotated[ResultStatus, element(tag="Status"), Doc("The status of the result.")]
    scores: Annotated[
        list[Score],
        element(tag="Score"),
        Doc("Any scores that are attached to the result, e.g. World Ranking points."),
    ] = []


class ControlAnswer(IOFBaseModel):
    """Defines the the selected answer, the correct answer and the time used on a Trail-O control."""

    answer: Annotated[
        str,
        element(tag="Answer"),
        Doc("The answer that the competitor selected. If the competitor did not give any answer, use an empty string."),
    ]
    correct_answer: Annotated[
        str,
        element(tag="CorrectAnswer"),
        Doc("The correct answer. If no answer is correct, use an empty string."),
    ]
    time: Annotated[
        float | None,
        element(tag="Time"),
        Doc(
            "The time in seconds used to give the answer, in case of a timed control. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None


class Route(IOFBaseModel):
    """Defines a route, i.e. a number of geographical positions (waypoints) describing a competitor's navigation throughout a course.

    As routes contain large amounts of information, a compact storage format is utilized to keep the overall file size small. A route is stored as a base64-encoded byte sequence of waypoints. A waypoint is represented as described below. All multi-byte data types are stored in big-endian byte order (most significant byte first). Typically, a one-hour route with one-second waypoint recording interval occupies around 20 kilobytes.


    Waypoint header byte
    ====================
    Each waypoint byte sequence starts with a waypoint header byte:
    Waypoint header byte, bit 1: Waypoint type. 0 for normal waypoint, 1 for interruption waypoint. An interruption waypoint is a waypoint that is the last waypoint before an interruption in the route occurs, e.g. due to a satellite signal receiving failure. The last waypoint of a route should be a normal waypoint, not an interruption waypoint.
    Waypoint header byte, bits 2 and 3: Time storage mode. For a description of the time storage modes, see below.
    Bit 2   Bit 3   Time storage mode
    0      0      full storage mode (6 bytes)
    1      0      milliseconds delta storage mode (2 bytes)
    0      1      seconds delta storage mode (1 byte)
    Waypoint header byte, bits 4 and 5: Position storage mode (latitude, longitude, and altitude (if present)). For a description of the position storage modes, see below.
    Bit 4   Bit 5   Position storage mode
    0      0      full storage mode (4 + 4 (+ 3) bytes for latitude, longitude and altitude (if present))
    1      0      big delta delta storage mode (2 + 2 (+ 1) bytes)
    0      1      small delta storage mode (1 + 1 (+ 1) bytes)
    Waypoint header byte, bit 6: Altitude presence. 0 if an altitude value is not present, 1 if it is present.
    Waypoint header byte, bit 7: Unused, always 0.
    Waypoint header byte, bit 8: Unused, always 0.


    Time byte sequence
    ==================
    After the waypoint byte comes the time byte sequence. Depending on the time storage mode defined in the waypoint header, the time byte sequence is either 6 bytes (full), 2 bytes (milliseconds delta) or 1 byte (seconds delta) long.

    Full storage mode
    -----------------
    The following 6 bytes are an unsigned 48-bit integer defining the waypoint's time as the number of milliseconds (1/1000 seconds) since January 1, 1900, 00:00:00 UTC.

    Milliseconds delta storage mode
    -------------------------------
    The following 2 bytes are an unsigned 16-bit integer defining the waypoint's time as the number of milliseconds to add to the last waypoint's time.

    Seconds delta storage mode
    --------------------------
    The following byte is an unsigned 8-bit integer defining the waypoint's time as the number of seconds to add to the last waypoint's time. This storage mody can only be used when the difference to the last waypoint's time is an integer value.

    Consequently:
    - seconds delta storage mode is used when the waypoint's time is less than 256 seconds later than the last waypoint's time, and the difference between the times is an integer value.
    - milliseconds delta storage mode is used when the waypoint's time is less than 65.536 seconds later than the last waypoint's time
    - otherwise, full storage mode is used
    The time of the first waypoint of a route is always stored in full storage mode.


    Position byte sequence
    ======================
    Next, the position byte sequence appears: latitude, longitude and (if present) altitude bytes. Depending on the position storage mode defined in the waypoint header, the position byte sequence is either 4 + 4 (+ 3) bytes (full), 2 + 2 (+ 1) bytes (big delta) or 1 + 1 (+ 1) bytes (small delta) long.

    Full storage mode
    -----------------
    The first 4 bytes are a signed 32-bit integer defining the waypoint's latitude as microdegrees (1/1000000 degrees) relative to the equator. A negative value implies a latitude south of the equator. A microdegree is approximately equivalent to 0.1 meters.
    The following 4 bytes are a signed 32-bit integer defining the waypoint's latitude as microdegrees (1/1000000 degrees) relative to the Greenwich meridian. A negative value implies a longitude west of the Greenwich meridian. A microdegree is approximately equivalent to 0.1 meters at the equator and infinitely small at the poles.
    If the altitude presence bit in the waypoint header bit is set to 1, the following 3 bytes are a signed 24-bit integer defining the waypoint's altitude as decimeters (1/10 meters) relative to the sea level.

    Big delta storage mode
    ----------------------
    The first 2 bytes are a signed 16-bit integer defining the waypoint's latitude as the number of microdegrees to add to the last waypoint's latitude.
    The following 2 bytes are a signed 16-bit integer defining the waypoint's longitude as the number of microdegrees to add to the last waypoint's longitude.
    If the altitude presence bit in the waypoint header bit is set to 1, the following byte is a signed 8-bit integer defining the waypoint's altitude as the number of decimeters to add to the last waypoint's altitude.

    Small delta storage mode
    ----------------------
    The first byte is a signed 8-bit integer defining the waypoint's latitude as the number of microdegrees to add to the last waypoint's latitude.
    The following byte is a signed 8-bit integer defining the waypoint's longitude as the number of microdegrees to add to the last waypoint's longitude.
    If the altitude presence bit in the waypoint header bit is set to 1, the following byte is a signed 8-bit integer defining the waypoint's altitude as the number of decimeters to add to the last waypoint's altitude.

    Consequently:
    - small delta storage mode is used when the waypoint's latitude and longitude is within -0.000128 to 0.000127 degrees from the last waypoint's latitude, and when the altitude is not present or is within -12.8 to 12.7 meters from the last waypoint's altitude
    - big delta storage mode is used when the waypoint's latitude and longitude is within -0.032768 to 0.032767 degrees from the last waypoint's latitude, and when the altitude is not present or is within -12.8 to 12.7 meters from the last waypoint's altitude
    - otherwise, full storage mode is used
    The position of the first waypoint of a route is always stored in full storage mode.

    Code libraries for reading and writing route data are found at http://www.orienteering.org/datastandard/3.0/Libraries.zip.
    """

    base64: Annotated[bytes, constr(strip_whitespace=True)]


class PersonRaceResult(IOFBaseModel):
    """Result information for a person in a race."""

    bib_number: Annotated[
        str | None,
        element(tag="BibNumber"),
        Doc("The bib number that the person that the result belongs to is wearing."),
    ] = None
    start_time: Annotated[
        datetime | None,
        element(tag="StartTime"),
        Doc("The time when the person that the result belongs to started, expressed in ISO 8601 format."),
    ] = None
    finish_time: Annotated[
        datetime | None,
        element(tag="FinishTime"),
        Doc("The time when the person that the result belongs to finished, expressed in ISO 8601 format."),
    ] = None
    time: Annotated[
        float | None,
        element(tag="Time"),
        Doc(
            "The time, in seconds, that is shown in the result list. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None
    time_behind: Annotated[
        float | None,
        element(tag="TimeBehind"),
        Doc(
            "The time, in seconds, that the the person is behind the winner. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None
    position: Annotated[
        int | None,
        element(tag="Position"),
        Doc(
            "The position in the result list for the person that the result belongs to. This element should only be present when the Status element is set to OK.",
        ),
    ] = None
    status: Annotated[ResultStatus, element(tag="Status"), Doc("The status of the result.")]
    scores: Annotated[
        list[Score],
        element(tag="Score"),
        Doc("Any scores that are attached to the result, e.g. World Ranking points."),
    ] = []
    overall_result: Annotated[
        OverallResult | None,
        element(tag="OverallResult"),
        Doc("Holds the overall result for the person after the current race for a multi-race event."),
    ] = None
    course: Annotated[
        SimpleCourse | None,
        element(tag="Course"),
        Doc("Defines the course assigned to the person."),
    ] = None
    split_times: Annotated[
        list[SplitTime],
        element(tag="SplitTime"),
        Doc(
            "Contains the times at each control of the course. Each control of the competitor's course (if known) has to be defined in a SplitTime element, even if the control has not been punched or if the competitor has not started. Start and finish times must not be present as SplitTime elements.",
        ),
    ] = []
    control_answers: Annotated[
        list[ControlAnswer],
        element(tag="ControlAnswer"),
        Doc("Defines the answer for a trail-O control."),
    ] = []
    route: Annotated[
        Route | None,
        element(tag="Route"),
        Doc("Defines the person's route recorded by a tracking device."),
    ] = None
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc(
            "Defines the control card assigned to the person. Multiple control cards can be specified, e.g. one for punch checking and another for timing.",
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


class PersonResult(IOFBaseModel):
    """Result information for an individual competitor, including e.g. result status, place, finish time, and split times."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this person's entry in an EntryList."),
    ] = None
    person: Annotated[Person, element(tag="Person"), Doc("The person that the result belongs to.")]
    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc("The organisation that the person is representing at the event."),
    ] = None
    results: Annotated[
        list[PersonRaceResult],
        element(tag="Result"),
        Doc("The core result information for the person; one element per race in the event."),
    ] = []
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class TimeBehind(IOFBaseModel):
    value: Annotated[float, constr(strip_whitespace=True)]
    type: Annotated[
        Literal[
            "Leg",
            "Course",
        ],
        attr(name="type"),
        Doc(
            """
        Leg: The time behind refers to the best time of the competitors that are taking part on the same leg as this team member, independly of the course assigned.
        Course: The time behind refers to the best time of the competitors that have been assigned the same course as this team member.
    """,
        ),
    ]


class Position(IOFBaseModel):
    value: Annotated[int, constr(strip_whitespace=True)]
    type: Annotated[
        Literal[
            "Leg",
            "Course",
        ],
        attr(name="type"),
        Doc(
            """
    Leg: The position refers to all competitors that are taking part on the same leg as this team member, independly of the course assigned.
    Course: The position refers to all competitors that have been assigned the same course as this team member.""",
        ),
    ]


class TeamMemberRaceResult(IOFBaseModel):
    """Result information for a person in a race."""

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
        Doc("The bib number that the team member that the result belongs to is wearing."),
    ] = None
    start_time: Annotated[
        datetime | None,
        element(tag="StartTime"),
        Doc("The time when the team member that the result belongs to started, expressed in ISO 8601 format."),
    ] = None
    finish_time: Annotated[
        datetime | None,
        element(tag="FinishTime"),
        Doc("The time when the team member that the result belongs to finished, expressed in ISO 8601 format."),
    ] = None
    time: Annotated[
        float | None,
        element(tag="Time"),
        Doc(
            "The time, in seconds, that is shown in the result list. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = None
    time_behind: Annotated[
        list[TimeBehind],
        element(tag="TimeBehind"),
        Doc(
            "The time, in seconds, that the the team member is behind the winner. Fractions of seconds (e.g. 258.7) may be used if the time resolution is higher than one second.",
        ),
    ] = []
    positions: Annotated[
        list[Position],
        element(tag="Position"),
        Doc(
            "The position in the result list for the person that the result belongs to. This element should only be present when the Status element is set to OK.",
        ),
    ] = []
    status: Annotated[ResultStatus, element(tag="Status"), Doc("The status of the result.")]
    scores: Annotated[
        list[Score],
        element(tag="Score"),
        Doc("Any scores that are attached to the result, e.g. World Ranking points."),
    ] = []
    overall_result: Annotated[
        OverallResult | None,
        element(tag="OverallResult"),
        Doc("Holds the result after the current leg for the team."),
    ] = None
    course: Annotated[
        SimpleCourse | None,
        element(tag="Course"),
        Doc("Defines the course assigned to the person."),
    ] = None
    split_times: Annotated[
        list[SplitTime],
        element(tag="SplitTime"),
        Doc(
            "Contains the times at each control of the course. Each control of the team member's course has to be defined in a SplitTime element, even if the control has not been punched. Start and finish times must not be present as SplitTime elements.",
        ),
    ] = []
    control_answers: Annotated[
        list[ControlAnswer],
        element(tag="ControlAnswer"),
        Doc("Defines the answer for a trail-O control."),
    ] = []
    route: Annotated[
        Route | None,
        element(tag="Route"),
        Doc("Defines the person's route recorded by a tracking device."),
    ] = None
    control_cards: Annotated[
        list[ControlCard],
        element(tag="ControlCard"),
        Doc(
            "Defines the control card assigned to the person. Multiple control cards can be specified, e.g. one for punch checking and another for timing.",
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


class TeamMemberResult(IOFBaseModel):
    """Result information for a team member, including e.g. result status, place, finish time, and split times."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this team member's entry in an EntryList."),
    ] = None
    person: Annotated[
        Person | None,
        element(tag="Person"),
        Doc("The team member that the result belongs to. If a relay team is missing a team member, omit this element."),
    ] = None
    organisation: Annotated[
        Organisation | None,
        element(tag="Organisation"),
        Doc("The organisation that the team member is representing at the event."),
    ] = None
    results: Annotated[
        list[TeamMemberRaceResult],
        element(tag="Result"),
        Doc("The core result information for the person; one element per race in the event."),
    ] = []
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class TeamResult(IOFBaseModel):
    """Result information for a team, including e.g. result status, place, finish time and individual times for the team members."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this team's entry in an EntryList."),
    ] = None
    name: Annotated[
        str,
        element(tag="Name"),
        Doc("The name of the team, e.g. organisation name and team number for a relay team."),
    ]
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
    team_member_results: Annotated[
        list[TeamMemberResult],
        element(tag="TeamMemberResult"),
        Doc(
            "Defines the result information for each team member. One element per relay leg must be included, even if the team has not assigned any team member to the leg, with exception for delta results.",
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


class ClassResult(IOFBaseModel):
    """The result list for a single class containing either individual results or team results."""

    class_: Annotated[Class, element(tag="Class"), Doc("The class that the result list belongs to.")]
    courses: Annotated[
        list[SimpleRaceCourse],
        element(tag="Course"),
        Doc(
            "Defines the course assigned to the class. If courses are unique per competitor, use PersonResult/Course or TeamResult/TeamMemberResult/Course instead. One element per race.",
        ),
    ] = []
    person_results: Annotated[
        list[PersonResult],
        element(tag="PersonResult"),
        Doc("Results for individual competitors in the class."),
    ] = []
    team_results: Annotated[list[TeamResult], element(tag="TeamResult"), Doc("Results for teams in the class.")] = []
    time_resolution: Annotated[
        float,
        attr(name="timeResolution"),
        Doc("The time resolution of the results, normally 1. For tenths of a second, use 0.1."),
    ] = 1
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class ResultList(BaseMessageElement):
    """Contains information about the result lists for the classes in an event."""

    event: Annotated[Event, element(tag="Event"), Doc("The event that the result lists belong to.")]
    class_results: Annotated[
        list[ClassResult],
        element(tag="ClassResult"),
        Doc("Result lists for the classes in the event."),
    ] = []
    status: Annotated[
        Literal[
            "Complete",
            "Delta",
            "Snapshot",
        ],
        attr(name="status"),
        Doc(
            """
    The status of the result list.

    Complete: The result list is complete, i.e. all competitors are included. Used for official results after the event.
    Delta: The result list only contains changes since last list. Used for frequent exchange of results.
    Snapshot: The result list is a snapshot of the current standings. Used while the event is under way.")] = "Complete""",
        ),
    ]
