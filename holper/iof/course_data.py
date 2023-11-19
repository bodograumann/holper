from collections.abc import Iterable
from datetime import datetime
from itertools import chain
from typing import Annotated, Literal

from pydantic_xml import attr, element
from typing_extensions import Doc

from .common import BaseMessageElement, Control, ControlType, Event, Id, Image, IOFBaseModel, MapPosition


class ClassCourseAssignment(IOFBaseModel):
    """Element that connects a course with a class. Courses should be present in the RaceCourseData element and are matched on course name and/or course family. Classes are matched by 1) Id, 2) Name."""

    class_id: Annotated[Id | None, element(tag="ClassId"), Doc("The id of the class.")] = None
    class_name: Annotated[str, element(tag="ClassName"), Doc("The name of the class.")]
    allowed_on_legs: Annotated[
        list[int],
        element(tag="AllowedOnLeg"),
        Doc(
            "The legs that the course can be assigned to in a relay class. This element can be omitted for individual classes.",
        ),
    ] = []
    course_name: Annotated[str | None, element(tag="CourseName"), Doc("The name of the course.")] = None
    course_family: Annotated[
        str | None,
        element(tag="CourseFamily"),
        Doc("The family or group of forked courses that the course is part of."),
    ] = None
    number_of_competitors: Annotated[
        int | None,
        attr(name="numberOfCompetitors"),
        Doc(
            "The number of competitors in the class. A competitor corresponds to a person (if an individual event) or a team (if a team or relay event).",
        ),
    ] = None


class PersonCourseAssignment(IOFBaseModel):
    """Element that connects a course with an individual competitor. Courses should be present in the RaceCourseData element and are matched on course name and/or course family. Persons are matched by 1) BibNumber, 2) EntryId."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this person's entry in an EntryList."),
    ] = None
    bib_number: Annotated[str | None, element(tag="BibNumber"), Doc("The bib number of the person.")] = None
    person_name: Annotated[str | None, element(tag="PersonName"), Doc("The name of the person.")] = None
    class_name: Annotated[
        str | None,
        element(tag="ClassName"),
        Doc("The name of the class that the person belongs to."),
    ] = None
    course_name: Annotated[str | None, element(tag="CourseName"), Doc("The name of the course.")] = None
    course_family: Annotated[
        str | None,
        element(tag="CourseFamily"),
        Doc("The family or group of forked courses that the course is part of."),
    ] = None


class TeamMemberCourseAssignment(IOFBaseModel):
    """Element that connects a course with a relay team member. Courses should be present in the RaceCourseData element and are matched on course name and/or course family. Team members are matched by 1) BibNumber, 2) Leg and LegOrder, 3) EntryId."""

    entry_id: Annotated[
        Id | None,
        element(tag="EntryId"),
        Doc("The id corresponding to this person's entry in an EntryList."),
    ] = None
    bib_number: Annotated[
        str | None,
        element(tag="BibNumber"),
        Doc(
            "The bib number of the person or the team that the person belongs to. Omit if the bib number is specified in the TeamCourseAssignment element.",
        ),
    ] = None
    leg: Annotated[
        int | None,
        element(tag="Leg"),
        Doc("For relay entries, the number of the leg that the person is taking part in."),
    ] = None
    leg_order: Annotated[
        int | None,
        element(tag="LegOrder"),
        Doc("Defines the person's starting order within a team at a parallel relay leg."),
    ] = None
    team_member_name: Annotated[str | None, element(tag="TeamMemberName"), Doc("The name of the person.")] = None
    course_name: Annotated[str | None, element(tag="CourseName"), Doc("The name of the course.")] = None
    course_family: Annotated[
        str | None,
        element(tag="CourseFamily"),
        Doc("The family or group of forked courses that the course is part of."),
    ] = None


class TeamCourseAssignment(IOFBaseModel):
    """Element that connects a number of team members in a relay team to a number of courses. Teams are matched by 1) BibNumber, 2) TeamName+ClassName."""

    bib_number: Annotated[str | None, element(tag="BibNumber"), Doc("The bib number of the team.")] = None
    team_name: Annotated[str | None, element(tag="TeamName"), Doc("The name of the team.")] = None
    class_name: Annotated[
        str | None,
        element(tag="ClassName"),
        Doc("The name of the class that the team belongs to."),
    ] = None
    team_member_course_assignments: Annotated[
        list[TeamMemberCourseAssignment],
        element(tag="TeamMemberCourseAssignment"),
        Doc("The assignment of courses to team members."),
    ] = []


class CourseControl(IOFBaseModel):
    """A control included in a particular course."""

    controls: Annotated[
        list[str],
        element(tag="Control"),
        Doc(
            "The code(s) of the control(s), without course-specific information. Specifying multiple control codes means that the competitor is required to punch one of the controls, but not all of them.",
        ),
    ]
    map_text: Annotated[
        str | None,
        element(tag="MapText"),
        Doc("Indicates the text shown next to the control circle, i.e. the control number."),
    ] = None
    map_text_position: Annotated[
        MapPosition | None,
        element(tag="MapTextPosition"),
        Doc("Indicates the position of the center of the text relative to the center of the control circle."),
    ] = None
    leg_length: Annotated[
        float | None,
        element(tag="LegLength"),
        Doc(
            "The length in meters from the previous control on the course. For starts, this length may refer to the distance from the time start to the start flag.",
        ),
    ] = None
    score: Annotated[float | None, element(tag="Score"), Doc("The score of the control in score-O events.")] = None
    type: Annotated[
        ControlType | None,
        attr(name="type"),
        Doc(
            "The type of the control: (ordinary) control, start, finish, crossing point or end of marked route. If this attribute is specified, it overrides the corresponding Control's type.",
        ),
    ] = None
    random_order: Annotated[
        bool | None,
        attr(name="randomOrder"),
        Doc(
            "Non-broken sequences of course controls having randomOrder set to true can be visited in an arbitrary order.",
        ),
    ] = False
    special_instruction: Annotated[
        Literal[
            "None",
            "TapedRoute",
            "FunnelTapedRoute",
            "MandatoryCrossingPoint",
            "MandatoryOutOfBoundsAreaPassage",
        ]
        | None,
        attr(name="specialInstruction"),
        Doc(
            "Any special instruction applied at the control, see http://orienteering.org/wp-content/uploads/2010/12/Control-Descriptions-2004-symbols-only.pdf, page 15.",
        ),
    ] = "None"
    taped_route_length: Annotated[
        float | None,
        attr(name="tapedRouteLength"),
        Doc(
            "The length of the taped route in meters. Only to be specified if specialInstruction is TapedRoute or FunnelTapedRoute and if different from the value specified in LegLength element, i.e. when Special Instruction 13.1 is used.",
        ),
    ] = None
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class Course(IOFBaseModel):
    """Defines a course, i.e. a number of controls including start and finish."""

    id: Annotated[Id | None, element(tag="Id")] = None
    name: Annotated[str, element(tag="Name"), Doc("The name of the course.")]
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
    course_controls: Annotated[
        list[CourseControl],
        element(tag="CourseControl"),
        Doc("The controls, including start and finish, that the course is made up of."),
    ]
    map_id: Annotated[int | None, element(tag="MapId"), Doc("The id of the map used for this course.")] = None
    number_of_competitors: Annotated[
        int | None,
        attr(name="numberOfCompetitors"),
        Doc("The number of competitors that this course has been assigned to."),
    ] = None
    modify_time: Annotated[datetime | None, attr(name="modifyTime")] = None


class Map(IOFBaseModel):
    """Map information, used in course setting software with regard to the "real" map."""

    id: Annotated[Id | None, element(tag="Id")] = None
    image: Annotated[Image | None, element(tag="Image"), Doc("The map image.")] = None
    scale: Annotated[
        float,
        element(tag="Scale"),
        Doc("The denominator of the scale of the map. 1:15000 should be represented as 15000."),
    ]
    map_position_top_left: Annotated[
        MapPosition,
        element(tag="MapPositionTopLeft"),
        Doc("The position of the map's top left corner given in the map's coordinate system, usually (0, 0)."),
    ]
    map_position_bottom_right: Annotated[
        MapPosition,
        element(tag="MapPositionBottomRight"),
        Doc("The position of the map's bottom right corner given in the map's coordinate system."),
    ]


class RaceCourseData(IOFBaseModel):
    """This element defines all the control and course information for a race."""

    maps: Annotated[
        list[Map],
        element(tag="Map"),
        Doc(
            "The map(s) used in this race. Usually just one map, but different courses may use different scales and/or areas.",
        ),
    ] = []
    controls: Annotated[list[Control], element(tag="Control"), Doc("All controls of the race.")] = []
    courses: Annotated[list[Course], element(tag="Course"), Doc("All courses of the race.")] = []
    class_course_assignments: Annotated[
        list[ClassCourseAssignment],
        element(tag="ClassCourseAssignment"),
        Doc("The assignment of courses to classes."),
    ] = []
    person_course_assignments: Annotated[
        list[PersonCourseAssignment],
        element(tag="PersonCourseAssignment"),
        Doc("The assignment of courses to individual competitors."),
    ] = []
    team_course_assignments: Annotated[
        list[TeamCourseAssignment],
        element(tag="TeamCourseAssignment"),
        Doc("The assignment of courses to relay team members teams."),
    ] = []
    race_number: Annotated[
        int | None,
        attr(name="raceNumber"),
        Doc("The ordinal number of the race that the information belongs to for a multi-race event, starting at 1."),
    ] = None

    @property
    def all_course_assignments(self) -> Iterable[TeamMemberCourseAssignment | ClassCourseAssignment]:
        return chain(
            chain.from_iterable(
                team_assignment.team_member_course_assignments for team_assignment in self.team_course_assignments or []
            ),
            self.class_course_assignments or [],
        )

    def delete_unused_courses(self) -> None:
        used_courses = [assignment.course_name for assignment in self.all_course_assignments]
        self.courses = [course for course in self.courses if course.name in used_courses]


class CourseData(BaseMessageElement):
    """This element defines all the control and course information for an event or race. Used when transferring courses from course-setting software to event administration software."""

    event: Annotated[Event, element(tag="Event"), Doc("The event that the course data belongs to.")]
    race_course_data: Annotated[
        list[RaceCourseData],
        element(tag="RaceCourseData"),
        Doc("The course data for each race; one element per race in the event."),
    ]

    def delete_unused_courses(self) -> None:
        for race in self.race_course_data:
            race.delete_unused_courses()
