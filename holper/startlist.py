"""Generate start times.

According to the official german competiton rules (`WKB`_), the
competitors in a category have to start in equal intervals. These
intervals can be defined through the :py:class:`StartSlots` class.

Multiple categories that run on the same course are required to start
one after another with one unused start slot in between. That means the
gap between them is two times the gap between two competitiors on the
course. The :py:class:`CategoryOrder` class can be used to define
the order of the categories with the same course.

.. _WKB: http://www.orientierungslauf.de/6/1
"""

import random
from collections import Counter, defaultdict
from datetime import timedelta
import operator

from . import model
from .affine_seq import AffineSeq
from .tools import disjoin


class CategoryOrder:
    """Register all categories on the same course and define their order in the start list"""

    def __init__(self, race):
        self.race = race
        self.order = defaultdict(list)

        for category in race.categories:
            self.order[category.courses[0].course.course_id].append(category)

    def set_order_early(self, course, categories):
        self.order[course.course_id] = categories + list(filter(
            lambda category: category not in categories,
            self.order[course.course_id]
            ))

    def set_order_late(self, course, categories):
        self.order[course.course_id] = list(filter(
            lambda category: category not in categories,
            self.order[course.course_id]
            )) + categories

    def get_categories(self, course):
        try:
            return self.order[course.course_id]
        except KeyError:
            return []

    def get_course_slot_counts(self):
        counts = {}
        for course_id, categories in self.order.items():
            counts[course_id] = len(categories) - 1 + sum(
                len(category.starts)
                + (category.vacancies_before or 0)
                + (category.vacancies_after or 0)
                for category in categories
            )
        return counts


class StartSlots:
    def __init__(self, start_window = 12 * 60):
        self.start_window = start_window
        self.slot_sets = {}
        self.box_sizes = defaultdict(int)

    @staticmethod
    def generate(slot_counts, box_count, interval, groups = None):
        slots = StartSlots()
        for course_id, count in sorted(slot_counts.items(), key=operator.itemgetter(1), reverse=True):
            try:
                group = next(groups[key] for key in groups if course_id in groups[key])
            except StopIteration as exc:
                print('No first control for course %s found' % course_id)
                raise exc

            start = slots.get_free_slot(box_count, group)
            slots.set_slots(course_id, AffineSeq(start, start + interval * count, interval))

        return slots

    def set_slots(self, course_id, slots):
        if course_id in self.slot_sets:
            for slot in self.slot_sets[course_id]:
                self.box_sizes[slot] -= 1
        self.slot_sets[course_id] = slots
        for slot in slots:
            self.box_sizes[slot] += 1

    def get_slots(self, course_id):
        yield from self.slot_sets[course_id]

    def get_free_slot(self, box_count = 1, group = []):
        for slot in range(self.start_window):
            if self.box_sizes[slot] >= box_count:
                continue
            for conflict in group:
                if slot in self.slot_sets.get(conflict, []):
                    break
            else:
                return slot

        raise KeyError('No free slot found')


class StartList:
    """Assign :py:class:`entries <.model.Entry>` to the start slots.

    There already has to be a :py:class:`Start <.model.Start>` object
    which defines the category the entry is assigned to.
    """

    def __init__(self, race, category_order, start_slots):
        self.race = race
        self.category_order = category_order
        self.start_slots = start_slots

        for category in race.categories:
            category.time_offset = None

    def assign_random(self):
        """Assign start slots randomly"""
        for course in self.race.courses:
            slots = self.start_slots.getSlots(course.course_id)

            for category in self.category_order.get_categories(course):
                # Non-competitive entries after competitive ones
                starts = defaultdict(list)
                for start in category.starts:
                    starts[start.competitive].append(start)

                for competitive in [True, False]:
                    if starts[competitive]:
                        self._assign_entries_random(starts[competitive], slots)

                        # After each category there has to be one slot left empty
                        next(slots)

    def _assign_entries_random(self, starts, slot_iter):
        preferences = defaultdict(list)
        for start in starts:
            pref = 0
            for request in start.entry.start_time_allocation_requests:
                if request.type is model.StartTimeAllocationRequestType.EARLY_START:
                    pref = 1
                elif request.type is model.StartTimeAllocationRequestType.LATE_START:
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
            if start.category.time_offset is None:
                start.category.time_offset = timedelta(minutes=next(slot_iter))
                start.time_offset = timedelta()
            else:
                start.time_offset = timedelta(minutes=next(slot_iter)) - start.category.time_offset

    def get_statistics(self):
        starts = sum((list(category.starts) for category in self.race.categories), [])
        total = len(starts)
        last_slot = max(start.category.time_offset + start.time_offset for start in starts)
        mean = total / ((last_slot + timedelta(minutes=1)).total_seconds() / 60)
        counts = Counter(start.category.time_offset + start.time_offset for start in starts)
        stats = Counter(counts.values())

        return {
                'entries_total': total,
                'last_start': (last_slot + timedelta(minutes=1)).total_seconds() / 60,
                'entries_per_slot': stats,
                'entries_per_slot_avg': mean,
                'entries_per_slot_var': sum(counts[slot] ** 2 for slot in counts) / (last_slot.total_seconds() / 60 + 1) - mean ** 2
                }
