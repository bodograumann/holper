from collections.abc import Iterable
from datetime import datetime
from itertools import chain
from typing import Annotated

from pydantic_xml import BaseXmlModel, attr, element

# Unsupported:
# - forward refs with `from __future__ import annotations`

nsmap = {
    "": "http://www.orienteering.org/datastandard/3.0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


class IOFBaseModel(BaseXmlModel, nsmap=nsmap, search_mode="ordered"):
    pass


class ClassCourseAssignment(IOFBaseModel):
    class_name: Annotated[str, element(tag="ClassName")]
    course_name: Annotated[str, element(tag="CourseName")]


class TeamMemberCourseAssignment(IOFBaseModel):
    leg: Annotated[int, element(tag="Leg")]
    course_name: Annotated[str, element(tag="CourseName")]
    course_family: Annotated[str, element(tag="CourseFamily")]


class TeamCourseAssignment(IOFBaseModel):
    bib_number: Annotated[str, element(tag="BibNumber")]
    team_member_course_assignments: Annotated[
        list[TeamMemberCourseAssignment],
        element(tag="TeamMemberCourseAssignment"),
    ]


class CourseControl(IOFBaseModel):
    type: Annotated[str, attr()]
    control: Annotated[str, element(tag="Control")]
    leg_length: Annotated[int | None, element(tag="LegLength")]


class Course(IOFBaseModel):
    name: Annotated[str, element(tag="Name")]
    course_family: Annotated[str | None, element(tag="CourseFamily")] = None
    length: Annotated[int, element(tag="Length")]
    climb: Annotated[int, element(tag="Climb")]
    course_controls: Annotated[list[CourseControl] | None, element(tag="CourseControl")] = None


class MapPosition(IOFBaseModel):
    x: Annotated[float, attr()]
    y: Annotated[float, attr()]
    unit: Annotated[str, attr()]


class Control(IOFBaseModel):
    control_id: Annotated[str, element(tag="Id")]
    map_position: Annotated[MapPosition, element(tag="MapPosition")]


class Map(IOFBaseModel):
    scale: Annotated[int, element(tag="Scale")]


class RaceCourseData(IOFBaseModel):
    maps: Annotated[list[Map], element(tag="Map")] = []
    controls: Annotated[list[Control], element(tag="Control")] = []
    courses: Annotated[list[Course], element(tag="Course")] = []
    class_course_assignments: Annotated[list[ClassCourseAssignment], element(tag="ClassCourseAssignment")] = []
    team_course_assignments: Annotated[list[TeamCourseAssignment], element(tag="TeamCourseAssignment")] = []

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


class Event(IOFBaseModel):
    name: Annotated[str, element(tag="Name")]


class CourseData(IOFBaseModel):
    iof_version: Annotated[str, attr(name="iofVersion")]
    create_time: Annotated[datetime, attr(name="createTime")]
    creator: Annotated[str, attr()]

    event: Annotated[Event, element(tag="Event")]
    race_course_data: Annotated[RaceCourseData, element(tag="RaceCourseData")]
