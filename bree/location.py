from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_points(cls, left, top, right, bottom):
        return cls(left, top, right - left, bottom - top)

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def min_point(self):
        return (self.x, self.y)

    @property
    def max_point(self):
        return (self.right, self.bottom)

    @property
    def center(self):
        return (self.right + self.left) // 2, (self.bottom + self.top) // 2
