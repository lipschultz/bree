import math
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    @classmethod
    def from_tuple(cls, location) -> 'Point':
        return cls(location[0], location[1])

    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_coordinates(cls, left, top, right, bottom):
        return cls(left, top, right - left, bottom - top)

    @property
    def left(self) -> int:
        return self.x

    @property
    def top(self) -> int:
        return self.y

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def min_point(self) -> Point:
        return Point(self.x, self.y)

    @property
    def max_point(self) -> Point:
        return Point(self.right, self.bottom)

    @property
    def center(self) -> Point:
        return Point((self.right + self.left) // 2, (self.bottom + self.top) // 2)


LocationType = Union[Point, Region]
