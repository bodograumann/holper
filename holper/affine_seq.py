"""Affine Sequences with convenience operators"""

import re
from collections.abc import Iterator
from math import gcd
from typing import Self


def lcm(int1: int, int2: int) -> int:
    """Calculate the least common multiple of two integers"""
    if not int1 or not int2:
        return 0
    return int(abs(int1 * int2) / gcd(int1, int2))


# Affine sequences are described by strings of the form '5n+7', similar to nth-child in css
affine_sequence_re = re.compile(r"(?P<interval>[0-9]*)n(?:\+(?P<offset>[0-9]+))?")


class AffineSeq:
    __slots__ = ["start", "step", "stop"]

    def __init__(self, start: int | str, stop: int, step: int = 1) -> None:
        if isinstance(start, str):
            match = affine_sequence_re.match(start)
            if match is None:
                msg = f"`start` value '{start}' has invalid format"
                raise ValueError(msg)
            self.start = int(match.group("offset") or 0)
            self.step = int(match.group("interval") or 1)
        else:
            self.start = start
            self.step = step

        self.stop = stop

        if self.step < 1:
            msg = "`step` value must be positive"
            raise ValueError(msg)

    def pretty(self) -> str:
        return (str(self.step) if self.step != 1 else "") + "n" + ("+" + str(self.start) if self.start else "")

    def to_range(self) -> range:
        return range(self.start, self.stop, self.step)

    def __len__(self) -> int:
        return len(self.to_range())

    def __getitem__(self, key: int) -> int:
        return self.start + self.step * key

    def __iter__(self) -> Iterator[int]:
        return iter(self.to_range())

    def __reversed__(self) -> Iterator[int]:
        return reversed(self.to_range())

    def __contains__(self, item: int) -> bool:
        return self.start <= item < self.stop and (item - self.start) % self.step == 0

    def __add__(self, other: Self) -> Self:
        return type(self)(self.start + other.start, self.stop + other.stop, self.step + other.step)

    def __lshift__(self, steps: int) -> Self:
        return type(self)(self.start - steps * self.step, self.stop - steps * self.step, self.step)

    def __rshift__(self, steps: int) -> Self:
        return type(self)(self.start + steps * self.step, self.stop + steps * self.step, self.step)

    def __and__(self, other: Self) -> Self:
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

        return type(self)(start, stop, step)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start}, {self.stop}, {self.step})"

    def __str__(self) -> str:
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
