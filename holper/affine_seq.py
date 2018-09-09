import re
from fractions import gcd

def lcm(a, b):
    return int(abs(a * b) / gcd(a,b)) if a and b else 0


# Affine sequences are described by strings of the form '5n+7', similar to nth-child in css
affine_sequence_re = re.compile(r'(?P<interval>[0-9]*)n(?:\+(?P<offset>[0-9]+))?')

class AffineSeq:
    __slots__ = ['start', 'stop', 'step']

    def __init__(self, start, stop, step = 1):
        if type(start) is str:
            match = affine_sequence_re.match(start)
            self.start = int(match.group('offset') or 0)
            self.step = int(match.group('interval') or 1)
        else:
            self.start = start
            self.step = step

        self.stop = stop

        assert(self.step > 0)

    def pretty(self):
        return (str(self.step) if self.step != 1 else '') + 'n' + ('+' + str(self.start) if self.start else '')

    def toRange(self):
        return range(self.start, self.stop, self.step)

    def __len__(self):
        return len(self.toRange())

    def __getitem__(self, key):
        if type(key) is AffineSeq:
            return AffineSeq(self[key.start], self[key.stop], self.step * key.step)
        else:
            return self.start + self.step * key

    def __iter__(self):
        return iter(self.toRange())

    def __reversed__(self):
        return reversed(self.toRange())

    def __contains__(self, item):
        return (self.start <= item < self.stop
                and (item - self.start) % self.step == 0)

    def __add__(self, other):
        return AffineSeq(self.start + other.start, self.stop + other.stop, self.step + other.step)

    def __lshift__(self, steps):
        return AffineSeq(self.start - steps * self.step, self.stop - steps * self.step, self.step)

    def __rshift__(self, steps):
        return AffineSeq(self.start + steps * self.step, self.stop + steps * self.step, self.step)

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
        return 'AffineSeq({}, {}, {})'.format(self.start, self.stop, self.step)

    def __str__(self):
        l = len(self)
        s = '('
        if l > 0:
            s += str(self.start)
        if l > 1:
            s += ', ' + str(self.start + self.step)
        if l > 3:
            s += ', …'
        if l > 2:
            s += ', ' + str(next(reversed(self)))
        s += ')'

        return s
