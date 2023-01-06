import math
from dataclasses import dataclass
from typing import Tuple, Union


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    @classmethod
    def from_tuple(cls, location: Tuple[int, int]) -> "Point":
        return cls(location[0], location[1])

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_coordinates(cls, left, top, right, bottom):
        return cls(left, top, right - left, bottom - top)

    @classmethod
    def from_points(cls, top_left: Union[Point, Tuple[int, int]], bottom_right: Union[Point, Tuple[int, int]]):
        if not isinstance(top_left, Point):
            top_left = Point.from_tuple(top_left)
        if not isinstance(bottom_right, Point):
            bottom_right = Point.from_tuple(bottom_right)
        return cls.from_coordinates(top_left.x, top_left.y, bottom_right.x, bottom_right.y)

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

    top_left = min_point

    @property
    def top_right(self) -> Point:
        return Point(self.right, self.top)

    @property
    def bottom_left(self) -> Point:
        return Point(self.left, self.bottom)

    @property
    def max_point(self) -> Point:
        return Point(self.right, self.bottom)

    bottom_right = max_point

    @property
    def center(self) -> Point:
        return Point((self.right + self.left) // 2, (self.bottom + self.top) // 2)

    def contains(self, item: "LocationType", overlap="all") -> bool:
        if isinstance(item, Point):
            return (self.left <= item.x <= self.right) and (self.top <= item.y <= self.bottom)
        elif isinstance(item, Region):
            overlap = overlap.lower()
            if overlap == "all":
                return item.min_point in self and item.max_point in self
            elif overlap == "any":
                return (
                    self.bottom >= item.top
                    and self.top <= item.bottom
                    and self.right >= item.left
                    and self.left <= item.right
                )
            else:
                raise ValueError(f'Unrecognized value for "overlap": {overlap!r}')
        else:
            raise NotImplementedError(f"Unsupported type ({type(item)}) for {item!r}")

    def __contains__(self, item: "LocationType") -> bool:
        return self.contains(item, overlap="all")


LocationType = Union[Point, Region]
