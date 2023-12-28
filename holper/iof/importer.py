import logging
from contextlib import suppress
from typing import TypedDict, TypeVar

from holper import model, tools

from .common import BaseMessageElement, Class, Control, ControlCard, Country, Id, Organisation, Person
from .course_data import ClassCourseAssignment, Course
from .entry_list import PersonEntry, StartTimeAllocationRequest, TeamEntry, TeamEntryPerson

EntityWithId = TypeVar("EntityWithId", bound=model.HasExternalIds)


class IdArgs(TypedDict):
    issuer: str
    external_id: str


class Importer:
    def __init__(self, root: BaseMessageElement, countries: list[model.Country]) -> None:
        self.default_issuer = root.creator or "unknown"
        self.organisations: list[model.Organisation] = []
        self.countries = countries

    def extract_id(self, id_: Id) -> IdArgs:
        return {
            "issuer": id_.type or self.default_issuer,
            "external_id": id_.text,
        }

    def find_by_id(self, entities: list[EntityWithId], id_: Id) -> EntityWithId:
        args = self.extract_id(id_)
        return next(
            entity
            for entity in entities
            if any(
                entity_id.issuer == args["issuer"] and entity_id.external_id == args["external_id"]
                for entity_id in entity.external_ids
            )
        )

    def find_country(self, ioc_code: str) -> model.Country | None:
        try:
            return next(country for country in self.countries if country.ioc_code == ioc_code)
        except StopIteration:
            logging.warning("Could not find country with ioc_code %s.", ioc_code)
            return None

    def import_class(self, class_: Class) -> model.EventCategory:
        imported = model.EventCategory(
            name=class_.name,
            short_name=class_.short_name,
            legs=[
                model.Leg(
                    leg_number=idx + 1,
                    min_number_of_competitors=leg.min_number_of_competitors,
                    max_number_of_competitors=leg.max_number_of_competitors,
                )
                for idx, leg in enumerate(class_.legs)
            ],
            min_age=class_.min_age,
            max_age=class_.max_age,
            sex=self.import_sex(class_.sex),
        )
        if class_.id is not None:
            imported.external_ids.append(model.EventCategoryXID(**self.extract_id(class_.id)))
        return imported

    def import_person_entry(self, person_entry: PersonEntry, categories: list[model.EventCategory]) -> model.Entry:
        organisation = self.import_organisation(person_entry.organisation)
        competitor = model.Competitor(
            external_ids=[model.CompetitorXID(**self.extract_id(person_entry.id))]
            if person_entry.id is not None
            else [],
            person=self.import_person(person_entry.person),
            organisation=organisation,
            control_cards=[self.import_control_card(control_card) for control_card in person_entry.control_cards],
        )
        return model.Entry(
            competitors=[competitor],
            organisation=organisation,
            category_requests=[
                model.EntryCategoryRequest(event_category=self.find_by_id(categories, request.id))
                for request in person_entry.classes
                if request.id is not None
            ],
            start_time_allocation_requests=[
                self.import_start_time_allocation_request(person_entry.start_time_allocation_request),
            ]
            if person_entry.start_time_allocation_request is not None
            else [],
        )

    def import_team_entry(self, entry: TeamEntry, categories: list[model.EventCategory]) -> model.Entry:
        competitors = [self.import_team_entry_person(entry_person) for entry_person in entry.team_entry_persons]
        for idx, competitor in enumerate(competitors):
            competitor.entry_sequence = idx + 1
        return model.Entry(
            name=entry.name,
            competitors=competitors,
            organisation=self.import_organisation(entry.organisations[0] if len(entry.organisations) > 0 else None),
            category_requests=[
                model.EntryCategoryRequest(event_category=self.find_by_id(categories, request.id))
                for request in entry.classes
                if request.id is not None
            ],
            start_time_allocation_requests=[
                self.import_start_time_allocation_request(entry.start_time_allocation_request),
            ]
            if entry.start_time_allocation_request is not None
            else [],
        )

    def import_team_entry_person(self, entry: TeamEntryPerson) -> model.Competitor:
        return model.Competitor(
            leg_number=entry.leg,
            leg_order=entry.leg_order,
            person=self.import_person(entry.person),
            organisation=self.import_organisation(entry.organisation),
            control_cards=[self.import_control_card(control_card) for control_card in entry.control_cards],
        )

    def import_person(self, person: Person | None) -> model.Person | None:
        if person is None:
            return None
        return model.Person(
            external_ids=[model.PersonXID(**self.extract_id(id_)) for id_ in person.ids],
            family_name=person.name.family.strip(),
            given_name=person.name.given.strip(),
            birth_date=person.birth_date,
            country=self.import_country(person.nationality),
            sex=self.import_sex(person.sex),
        )

    def import_sex(self, sex: str | None) -> model.Sex | None:
        if sex == "F":
            return model.Sex.FEMALE
        if sex == "M":
            return model.Sex.MALE
        return None

    def import_organisation(self, organisation: Organisation | None) -> model.Organisation | None:
        if organisation is None:
            return None
        if organisation.id is not None:
            with suppress(StopIteration):
                return self.find_by_id(self.organisations, organisation.id)

        imported = model.Organisation(
            external_ids=[model.OrganisationXID(**self.extract_id(organisation.id))]
            if organisation.id is not None
            else [],
            name=organisation.name,
            short_name=organisation.short_name,
            country=self.import_country(organisation.country),
            type=model.OrganisationType(tools.camelcase_to_snakecase(organisation.type))
            if organisation.type is not None
            else None,
        )
        self.organisations.append(imported)
        return imported

    def import_country(self, country: Country | None) -> model.Country | None:
        if country is None:
            return None
        return self.find_country(country.code)

    def import_control_card(self, control_card: ControlCard) -> model.ControlCard:
        imported = model.ControlCard(label=control_card.text)

        if (system := control_card.punching_system) is not None:
            if system.lower() in {"si", "sportident"}:
                imported.system = model.PunchingSystem.SPORT_IDENT
            elif system.lower() == "emit":
                imported.system = model.PunchingSystem.EMIT
            else:
                msg = f"Unknown punching system: {system}"
                raise NotImplementedError(msg)

        return imported

    def import_start_time_allocation_request(
        self,
        request: StartTimeAllocationRequest,
    ) -> model.StartTimeAllocationRequest:
        return model.StartTimeAllocationRequest(
            type=model.StartTimeAllocationRequestType(tools.camelcase_to_snakecase(request.type)),
            person=self.import_person(request.person) if request.person is not None else None,
            organisation=self.import_organisation(request.organisation) if request.organisation is not None else None,
        )

    def import_control(self, control: Control) -> model.Control:
        if control.id is None:
            msg = "Control without label"
            raise ValueError(msg)
        return model.Control(label=control.id.text)

    def import_course(self, course: Course, controls: list[model.Control]) -> model.Course:
        imported = model.Course(
            name=course.name,
            length=course.length,
            climb=course.climb,
        )

        random_order_segment = False
        control_order = 0
        for course_control in course.course_controls:
            if not course_control.controls:
                logging.warning(
                    "Missing label for course control. Skipping course control at position %d of course %s.",
                    control_order,
                    course.name,
                )
                continue
            if len(course_control.controls) > 1:
                logging.warning(
                    "Only one label per control is supported. Dropping all but the first: %s",
                    ", ".join(course_control.controls),
                )
            imported.controls.append(
                model.CourseControl(
                    control=next(control for control in controls if control.label == course_control.controls[0]),
                    leg_length=course_control.leg_length,
                    type=model.ControlType(tools.camelcase_to_snakecase(course_control.type or "Control")),
                    score=course_control.score,
                    order=control_order,
                ),
            )

            if not (random_order_segment and course_control.random_order):
                control_order += 1
            random_order_segment = course_control.random_order

        return imported

    def import_class_course_assignment(
        self,
        assignment: ClassCourseAssignment,
        courses: list[model.Course],
        categories: list[model.Category],
        *,
        use_short_category_name: bool = False,
    ) -> model.CategoryCourseAssignment | None:
        if not assignment.course_name:
            logging.warning("Course name required for assignment")
            return None
        course = next(course for course in courses if course.name == assignment.course_name)
        try:
            category = next(
                category
                for category in categories
                if category.name == assignment.class_name
                or use_short_category_name
                and category.short_name == assignment.class_name
            )
        except StopIteration:
            logging.warning(
                "No category %s found, so cannot assign course %s to it.",
                assignment.class_name,
                course.name,
            )
            return None
        return model.CategoryCourseAssignment(
            category=category,
            leg=1,
            course=course,
        )
