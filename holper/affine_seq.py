"""Affine Sequences with convenience operators"""

import re
from math import gcd


def lcm(int1, int2):
    """Calculate the least common multiple of two integers"""
    if not int1 or not int2:
        return 0
    return int(abs(int1 * int2) / gcd(int1, int2))


# Affine sequences are described by strings of the form '5n+7', similar to nth-child in css
affine_sequence_re = re.compile(r"(?P<interval>[0-9]*)n(?:\+(?P<offset>[0-9]+))?")


class AffineSeq:
    __slots__ = ["start", "stop", "step"]

    def __init__(self, start, stop, step=1):
        if isinstance(start, str):
            match = affine_sequence_re.match(start)
            self.start = int(match.group("offset") or 0)
            self.step = int(match.group("interval") or 1)
        else:
            self.start = start
            self.step = step

        self.stop = stop

        assert self.step > 0

    def pretty(self):
        return (
            (str(self.step) if self.step != 1 else "")
            + "n"
            + ("+" + str(self.start) if self.start else "")
        )

    def to_range(self):
        return range(self.start, self.stop, self.step)

    def __len__(self):
        return len(self.to_range())

    def __getitem__(self, key):
        if isinstance(key, AffineSeq):
            return AffineSeq(self[key.start], self[key.stop], self.step * key.step)
        return self.start + self.step * key

    def __iter__(self):
        return iter(self.to_range())

    def __reversed__(self):
        return reversed(self.to_range())

    def __contains__(self, item):
        return self.start <= item < self.stop and (item - self.start) % self.step == 0

    def __add__(self, other):
        return AffineSeq(
            self.start + other.start, self.stop + other.stop, self.step + other.step
        )

    def __lshift__(self, steps):
        return AffineSeq(
            self.start - steps * self.step, self.stop - steps * self.step, self.step
        )

    def __rshift__(self, steps):
        return AffineSeq(
            self.start + steps * self.step, self.stop + steps * self.step, self.step
        )

    def __and__(self, other):
        start = max(self.start, other.start)
        stop = min(self.stop, other.stop)
        step = lcm(self.step, other.step)

        if (self.start - other.start) % gcd(self.step, other.step):
            stop = start
        else:
            for item in self:
                if item in other:
                    start = item
                    break
            else:
                stop = start

        return AffineSeq(start, stop, step)

    def __repr__(self):
        return "AffineSeq({}, {}, {})".format(self.start, self.stop, self.step)

    def __str__(self):
        length = len(self)
        string = "("
        if length > 0:
            string += str(self.start)
        if length > 1:
            string += ", " + str(self.start + self.step)
        if length > 3:
            string += ", …"
        if length > 2:
            string += ", " + str(next(reversed(self)))
        string += ")"

        return string
