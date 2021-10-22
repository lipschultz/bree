from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Union

import cv2
import numpy as np
import PIL
import pyautogui


@dataclass(frozen=True)
class Point:
    x: int
    y: int


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
        return (self.right + self.left)//2, (self.bottom + self.top)//2

    def get_sub_region(self, left=None, top=None, width=None, height=None):
        parameters = {
            'left': left,
            'top': top,
            'width': width,
            'height': height,
        }

        for parameter_name, parameter_value in parameters.items():
            if isinstance(parameter_value, int):
                pass
            elif isinstance(parameter_value, float):
                if parameter_name in ('top', 'height'):
                    parameters[parameter_name] = int(self.height * parameter_value)
                else:
                    parameters[parameter_name] = int(self.width * parameter_value)
            elif parameter_value is None:
                parameters[parameter_name] = getattr(self, parameter_name)
            else:
                raise TypeError(f'Unrecognized type for {parameter_name}: {parameter_value!r}')

        return Region(
            parameters['left'],
            parameters['top'],
            parameters['width'],
            parameters['height']
        )


@dataclass(frozen=True)
class ScoredRegion(Region):
    score: float


def find_all_within(needle, haystack, match_threshold=1, *, match_method=cv2.TM_SQDIFF_NORMED) -> Iterable[ScoredRegion]:
    # from: https://stackoverflow.com/questions/7853628/how-do-i-find-an-image-contained-within-an-image/15147009#15147009
    height, width = needle.shape[:2]

    result = cv2.matchTemplate(needle, haystack, match_method)
    if match_method == cv2.TM_SQDIFF:
        result = result.max() - result
    elif match_method == cv2.TM_SQDIFF_NORMED:
        result = 1 - result

    locations = np.where(result >= match_threshold)
    scores = result[locations]
    return (
        ScoredRegion(x, y, width, height, score)
        for (x, y), score in zip(zip(*locations[::-1]), scores)
    )


def find_within(needle, haystack, match_threshold=1, *, match_method=cv2.TM_SQDIFF_NORMED) -> Optional[ScoredRegion]:
    matches = find_all_within(needle, haystack, match_threshold, match_method=match_method)
    if matches:
        matches = sorted(matches, key=lambda sr: sr.score, reverse=True)
        return matches[0]
    return None


@dataclass(frozen=True)
class RegionInImage(ScoredRegion):
    image: 'Image'
    labels: dict = field(default_factory=dict, compare=False)

    @classmethod
    def from_scored_region(cls, scored_region, image, *, labels=None):
        labels = labels or {}
        return cls(scored_region.x, scored_region.y, scored_region.width, scored_region.height, scored_region.score, image, labels=labels)

    def mouse_to(self, location=None, duration=0):
        """
            `location` is relative to the region.
        """
        print('mouse_to.0:', location)
        if location in self.labels:
            print('\tin label')
            location = self.labels[location]

        print('mouse_to.1:', location)
        if location is None:
            print('\tis None')
            location = self.center

        print('mouse_to.2:', location)
        if isinstance(location, tuple):
            print('\tis tuple', len(location))
            if len(location) == 2:
                location = Point(*location)
            elif len(location) == 4:
                location = Region(*location)
            else:
                raise ValueError(f'Unrecognized dimension for location: {location!r}')

        print('mouse_to.3:', location)
        if isinstance(location, Point):
            print('\tis Point')
            location = (
                location.x if isinstance(location.x, int) else int(location.x * self.width),
                location.y if isinstance(location.y, int) else int(location.y * self.height)
            )
        elif isinstance(location, Region):
            print('\tis Region')
            location = location.center

        print('mouse_to.4:', location)
        location = (
            location[0] + self.x,
            location[1] + self.y,
        )

        print('mouse_to.5:', location)
        pyautogui.moveTo(*location, duration=duration)

    def click(self, location=None, **args_for_move):
        if location is None and 'click' in self.labels:
            location = 'click'
        self.mouse_to(location, **args_for_move)
        pyautogui.click()



class Image:
    def __init__(self, image):
        self._original_image = image
        self._labeled_regions = {}

        self.__numpy_image = None

    def _get_numpy_image(self):
        if self.__numpy_image is None:
            if isinstance(self._original_image, np.ndarray):
                self.__numpy_image = self._original_image
            elif isinstance(self._original_image, (str, Path)):
                self.__numpy_image = np.asarray(PIL.Image.open(str(self._original_image)))
            else:
                raise TypeError(f'Unrecognized type for image: {self._original_image!r}')
        return self.__numpy_image

    @property
    def width(self):
        return self._get_numpy_image().shape[1]

    @property
    def height(self):
        return self._get_numpy_image().shape[0]

    def get_bounding_box(self):
        return RegionInImage(0, 0, self.width, self.height, 1, self)

    def get_subregion(self, left=None, top=None, width=None, height=None):
        raw_subregion = self.get_bounding_box().get_sub_region(left, top, width, height)

        return RegionInImage(
            raw_subregion.left,
            raw_subregion.top,
            raw_subregion.width,
            raw_subregion.height,
            1,
            self
        )

    def find_image_all(self, needle: 'Image', confidence=0.99, *, match_method=cv2.TM_SQDIFF_NORMED) -> Iterable[RegionInImage]:
        results = find_all_within(needle._get_numpy_image(), self._get_numpy_image(), confidence, match_method=match_method)
        return (RegionInImage.from_scored_region(r, self, labels=needle._labeled_regions) for r in results)

    def find_image(self, needle: 'Image', **kwargs) -> Optional[RegionInImage]:
        matches = self.find_image_all(needle, **kwargs)
        if matches:
            matches = sorted(matches, key=lambda sr: sr.score, reverse=True)
            return matches[0]
        return None

    def label_region(self, region: Union[Point, Region, 'Image'], label):
        self._labeled_regions[label] = region

    def get_region(self, label):
        return self._labeled_regions[label]


class Screen(Image):
    def __init__(self):
        super().__init__(None)

    def _get_pil_image(self):
        return pyautogui.screenshot()

    def _get_numpy_image(self):
        return np.asarray(self._get_pil_image())

    def screenshot(self):
        return Image(self._get_numpy_image())



import matplotlib.pyplot as plt

screen = Screen()
lower_third_of_screen = screen.get_subregion(top=2/3)
checkbox_and_label = Image('checkbox_and_label.png')
checkbox_and_label.label_region((11, 0.5), 'click')
# alternatively: checkbox_and_label.label_region(Image('checkbox.png'), 'click')

haystack = screen.screenshot()

best_region = haystack.find_image(checkbox_and_label)
best_region.click(duration=1)

# cv2.rectangle(haystack._get_numpy_image(), best_region.min_point, best_region.max_point, (255,0,0), 2)
# plt.imshow(haystack._get_numpy_image())
# plt.show()





'''
screen.screenshot([region=lower_third_of_screen]).find(checkbox_and_label, [wait=3]).click()
'''


'''
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    needle = Image('small_image.png')
    haystack = Image('large_image.png')

    # needle = cv2.imread('mario-needle.png')
    # haystack = cv2.imread('mario-haystack.png')

    best_region = haystack.find(needle)
    print('best:', best_region)

    if best_region is not None:
        cv2.rectangle(haystack._get_numpy_image(), best_region.min_point, best_region.max_point, (0,0,255), 2)
        plt.imshow(cv2.cvtColor(haystack._get_numpy_image(), cv2.COLOR_BGR2RGB))
        plt.show()
    else:
        print('None found')
'''
