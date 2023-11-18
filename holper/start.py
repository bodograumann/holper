"""Generate start times.

The implementation follows the official german competiton rules (`WKB`_).
That means competitors in a category have to start in equal intervals.
Intervals between categories can differ though.

Multiple categories that run on the same course are required to start one after
another with one unused start slot in between. That means the gap between them
is  at least two times the gap between two competitiors on the course. The
:py:class:`StartConstraints` class can be used to define conditions that must
be followed when generating start slots, e.g. the order of the categories with
the same course.

.. _WKB: https://o-sport.de/dokumente/wettkampfwesen/
"""

import operator
import random
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping
from datetime import timedelta

from more_itertools import peekable

# Cf. https://github.com/google/or-tools/issues/3993
from ortools.sat.python import cp_model  # type: ignore [import-untyped]

from .affine_seq import AffineSeq
from .model import Category, Course, Race, Start, StartTimeAllocationRequestType
from .tools import disjoin


class InfeasibleError(Exception):
    """Raise when an optimization cannot find a solution."""

    def __init__(self) -> None:
        super().__init__("No solution possible")


def _category_request_counts(category: Category) -> Counter:
    return Counter(request.type for start in category.starts for request in start.entry.start_time_allocation_requests)


EARLY = StartTimeAllocationRequestType.EARLY_START
LATE = StartTimeAllocationRequestType.LATE_START


def _category_order_key(category: Category) -> tuple[int, int, int]:
    counter = _category_request_counts(category)
    return (
        counter[LATE] - counter[EARLY],
        -counter[EARLY],
        counter[LATE],
    )


class StartConstraints:
    """Declare constraints for start list creation"""

    def __init__(
        self,
        interval: int = 1,
        parallel_max: int | None = None,
        conflicts: list[list[int]] | None = None,
    ) -> None:
        # Map course ids to an ordered list of categories
        self.order: dict[int, list[Category]] = defaultdict(list)
        # Maximal number of parallel starts for each start time
        self.parallel_max: int | None = parallel_max
        # Minimal time difference between two consecutive starts for each class
        self.interval: int = interval
        # Collection of course groups where each group is a collection of
        # course ids so that the courses must not start at the same time
        self.conflicts: list[list[int]] = [] if conflicts is None else conflicts

    def add_race_courses(self, race: Race) -> None:
        for category in race.categories:
            self.order[category.courses[0].course.course_id].append(category)

        for categories in self.order.values():
            categories.sort(key=_category_order_key)

    def set_category_early(self, course: Course, categories: list[Category]) -> None:
        self.order[course.course_id] = categories + list(
            filter(
                lambda category: category not in categories,
                self.order[course.course_id],
            ),
        )

    def set_category_late(self, course: Course, categories: list[Category]) -> None:
        self.order[course.course_id] = (
            list(
                filter(
                    lambda category: category not in categories,
                    self.order[course.course_id],
                ),
            )
            + categories
        )

    def get_categories(self, course: Course) -> list[Category]:
        try:
            return self.order[course.course_id]
        except KeyError:
            return []

    @property
    def course_slot_counts(self) -> dict[int, int]:
        return {
            course_id: len(categories)
            - 1
            + sum(
                len(category.starts) + (category.vacancies_before or 0) + (category.vacancies_after or 0)
                for category in categories
            )
            for course_id, categories in self.order.items()
        }


def generate_slots_greedily(constraints: StartConstraints, time_max: int = 12 * 60) -> dict[int, AffineSeq]:
    """Greedily finds a start slot scheme under the given constraints

    :param constraints: Conditions that the resulting start list must follow.
    :param time_max: Time limit before which all starts have to occur. Can usually be
        left as the default, because it has no impact on the calculation time.
    :return: Start slots object for each course id
    """

    # Map course ids to the set of allocated start times
    slots: dict[int, AffineSeq] = {}
    # Number of already assigned slots for each possible start time
    parallel: dict[int, int] = defaultdict(int)

    # Assign start slots to courses, starting from the course with the most entries
    for course_id, count in sorted(constraints.course_slot_counts.items(), key=operator.itemgetter(1), reverse=True):
        # Find first free slot
        for first_slot in range(time_max):
            # Check number of parallel starters
            if constraints.parallel_max and parallel[first_slot] >= constraints.parallel_max:
                continue

            # Check conflicts with already assigned slots
            if any(
                course_id in course_group
                and any(
                    other_course_id in slots and first_slot in slots[other_course_id]
                    for other_course_id in course_group
                )
                for course_group in constraints.conflicts
            ):
                continue

            # Slot can be used for the current course
            break
        else:
            msg = "No free slots found"
            raise KeyError(msg)

        slots[course_id] = AffineSeq(first_slot, first_slot + constraints.interval * count, constraints.interval)

        for slot in slots[course_id]:
            parallel[slot] += 1

    return slots


def generate_slots_optimal(constraints: StartConstraints, timeout: int = 30) -> dict[int, AffineSeq]:
    """Tries to find the optimal compact start slot scheme

    :param constraints: Conditions that the resulting start list must follow.
    :param timeout: Number of seconds after which to stop the optimization.
    :return: Start slots object for each course id
    """

    interval_min = constraints.interval
    interval_max = 12
    interval_common_factor = 1
    parallel_max = constraints.parallel_max

    # Courses are identified by their index in the model
    course_slot_counts = list(constraints.course_slot_counts.values())
    course_starters = list(enumerate(course_slot_counts))
    course_ids = list(constraints.course_slot_counts.keys())

    course_idx_by_id = {course_id: idx for idx, course_id in enumerate(course_ids)}
    no_common_slots = [
        [course_idx_by_id[course_id] for course_id in course_group if course_id in course_idx_by_id]
        for course_group in constraints.conflicts
    ]

    # Time range to consider
    time_max = sum(course_slot_counts) * interval_common_factor

    # Model and Constraints
    model = cp_model.CpModel()

    # start intervals per course, up to the common factor
    intervals = [
        model.NewIntVar(
            interval_min,
            min(interval_max, time_max // (starters - 1) if starters > 1 else time_max) // interval_common_factor,
            f"interval_{idx}",
        )
        for (idx, starters) in course_starters
    ]

    # Offsets of first start per course
    offsets = [
        model.NewIntVar(0, time_max - (starters - 1) * interval_min, f"offset_{idx}")
        for idx, starters in course_starters
    ]

    # variables for each starter
    slot_variables = [
        [model.NewIntVar(0, time_max, f"slot_{idx}_{starter}") for starter in range(starters)]
        for idx, starters in course_starters
    ]
    for idx, starters in course_starters:
        for starter in range(starters):
            model.Add(offsets[idx] + intervals[idx] * interval_common_factor * starter == slot_variables[idx][starter])

    # Limit total start length
    last_start = model.NewIntVar(0, time_max, "last_start")
    model.AddMaxEquality(last_start, (vars[-1] for vars in slot_variables if vars))

    # Forbid conflicting courses to start at the same time. E.g. when they have the same first control.
    for course_group in no_common_slots:
        model.AddAllDifferent([slot for idx in course_group for slot in slot_variables[idx]])

    # Limit number of starts at the same time using indicator variables for each start time.
    indicators = [
        [
            [model.NewBoolVar(f"assign_{idx}_{starter}_{time}") for time in range(time_max + 1)]
            for starter in range(starters)
        ]
        for idx, starters in course_starters
    ]

    for idx, starters in course_starters:
        for starter in range(starters):
            model.AddMapDomain(slot_variables[idx][starter], indicators[idx][starter])

    parallel = [
        sum(indicators[idx][starter][time] for idx, starters in course_starters for starter in range(starters))
        for time in range(time_max + 1)
    ]

    if parallel_max is not None:
        for time in range(time_max + 1):
            model.Add(parallel[time] <= parallel_max)

    # Step 1: Find the shortest possible start duration
    model.Minimize(last_start)

    # Not setting time limit, because this step is usually extremely fast
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        raise InfeasibleError

    time_max = solver.Value(last_start)
    model.Add(last_start == time_max)

    # Step 2: Find the optimal solution
    model.Maximize(
        sum((starters - 1) * intervals[idx] for idx, starters in course_starters)  # Maximize intervals
        - sum(offsets),  # Minimize offsets
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        raise InfeasibleError

    return {
        course_id: AffineSeq(
            solver.Value(offsets[idx]),
            solver.Value(offsets[idx])
            + solver.Value(intervals[idx]) * interval_common_factor * course_slot_counts[idx],
            solver.Value(intervals[idx]) * interval_common_factor,
        )
        for idx, course_id in enumerate(course_ids)
    }


def fill_slots(
    race: Race,
    constraints: StartConstraints,
    start_slots: Mapping[int, Iterable[int]],
) -> None:
    """Assign :py:class:`entries <.model.Entry>` to the start slots.

    There already has to be a :py:class:`Start <.model.Start>` object
    which defines the category the entry is assigned to.
    """
    for category in race.categories:
        category.time_offset = None

    for course in race.courses:
        _fill_course_slots(constraints.order[course.course_id], start_slots.get(course.course_id, []))


def _fill_course_slots(categories: list[Category], slots_iter: Iterable[int]):
    slots = peekable(slots_iter)
    for category in categories:
        try:
            category.time_offset = timedelta(minutes=slots.peek())
        except StopIteration:
            break

        # Skip vacancies at the start
        for _ in range(category.vacancies_before):
            next(slots)

        # Non-competitive entries after competitive ones
        starts: dict[bool, list[Start]] = defaultdict(list)
        for start in category.starts:
            starts[start.competitive].append(start)

        for competitive in [True, False]:
            if starts[competitive]:
                _assign_entries_randomly(starts[competitive], slots)

                # After each category there has to be one slot left empty
                try:  # noqa: SIM105
                    next(slots)
                except StopIteration:
                    # TODO: make sure this only happens at the very end of a course
                    ...

        # Skip vacancies at the end
        for _ in range(category.vacancies_after):
            next(slots)


def _assign_entries_randomly(starts: Iterable[Start], slot_iter: Iterator[int]) -> None:
    preferences = defaultdict(list)
    for start in starts:
        pref = 0
        for request in start.entry.start_time_allocation_requests:
            if request.type == EARLY:
                pref = 1
            elif request.type == LATE:
                pref = 2
            else:
                continue
            break
        preferences[pref].append(start)

    for pref in preferences:
        random.shuffle(preferences[pref])

    sequence = preferences[1] + preferences[0] + preferences[2]

    disjoin(sequence, lambda start: start.entry.organisation)

    for start in sequence:
        start.time_offset = timedelta(minutes=next(slot_iter)) - start.category.time_offset


class Statistics:
    def __init__(self, race: Race) -> None:
        starts = sum((list(category.starts) for category in race.categories), [])
        total = len(starts)
        last_slot = max(start.category.time_offset + start.time_offset for start in starts)
        mean = total / ((last_slot + timedelta(minutes=1)).total_seconds() / 60)
        counts = Counter(start.category.time_offset + start.time_offset for start in starts)
        stats = Counter(counts.values())

        self.entries_total = total
        self.last_start = last_slot.total_seconds() / 60
        self.entries_per_slot = stats
        self.entries_per_slot_avg = mean
        self.entries_per_slot_var = (
            sum(counts[slot] ** 2 for slot in counts) / (last_slot.total_seconds() / 60 + 1) - mean**2
        )
