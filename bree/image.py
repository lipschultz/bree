from dataclasses import dataclass
from pathlib import Path
from typing import Union, Iterable, Tuple, Optional

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import pyautogui
from matplotlib.patches import Rectangle

FileReferenceType = Union[str, Path]


class OutOfBoundsError(Exception):
    pass


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


def _find_all_within(needle: np.ndarray, haystack: np.ndarray, match_threshold: float = 1.0, *, match_method=cv2.TM_SQDIFF_NORMED) -> Iterable[Tuple[Region, float]]:
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
        (Region(x, y, width, height), score)
        for (x, y), score in zip(zip(*locations[::-1]), scores)
    )


class Image:
    def __init__(self, image: Union[FileReferenceType, np.ndarray, PILImage.Image]):
        self._original_image = image

        self.__numpy_image = None

    def _get_numpy_image(self) -> np.ndarray:
        if self.__numpy_image is None:
            image = self._original_image

            if isinstance(image, (str, Path)):
                image = PILImage.open(str(self._original_image))

            if isinstance(image, PILImage.Image):
                image = np.asarray(image)

            if isinstance(image, np.ndarray):
                if image.shape[2] == 4:
                    image = image[:, :, :3]  # Remove alpha channel for now
                self.__numpy_image = image
            else:
                raise TypeError(f'Unrecognized type for image: {self._original_image!r}')
        return self.__numpy_image

    @property
    def width(self) -> int:
        return self._get_numpy_image().shape[1]

    @property
    def height(self) -> int:
        return self._get_numpy_image().shape[0]

    def show(self, bounding_boxes: Iterable[Region] = ()) -> None:
        """
        Open a window to show the image using matplotlib.
        """
        plt.imshow(self._get_numpy_image())

        ax = plt.gca()
        for bounding_box in bounding_boxes:
            ax.add_patch(Rectangle(
                (bounding_box.x, bounding_box.y),
                bounding_box.width,
                bounding_box.height,
                linewidth=2,
                edgecolor='r',
                facecolor='none',
            ))

        plt.show()

    def get_child_region(self, region: Region) -> 'ChildImage':
        if region.left < 0:
            raise OutOfBoundsError(f'region.x={region.left}.  Value must be at least zero.')
        if region.top < 0:
            raise OutOfBoundsError(f'region.y={region.top}.  Value must be at least zero.')

        if region.right >= self.width:
            raise OutOfBoundsError(f'region.right={region.right}.  Value exceeds size of image (width={self.width}).')
        if region.bottom >= self.height:
            raise OutOfBoundsError(f'region.left={region.left}.  Value exceeds size of image (height={self.height}).')

        return ChildImage(self, region)

    def find_image_all(self, needle: 'Image', confidence: float = 0.99, *, match_method=cv2.TM_SQDIFF_NORMED) -> Iterable[Tuple['ChildImage', float]]:
        results = _find_all_within(
            needle._get_numpy_image(),
            self._get_numpy_image(),
            confidence,
            match_method=match_method
        )
        return ((self.get_child_region(region), score) for region, score in results)

    def find_image(self, needle: 'Image', *args, **kwargs) -> Optional['ChildImage']:
        result = self.find_image_all(needle, *args, **kwargs)
        result = sorted(result, key=lambda res: res[1], reverse=True)
        if result:
            return result[0][0]
        return None


class ChildImage(Image):
    def __init__(self, parent_image: Image, region: Region):
        super().__init__(None)
        self._parent_image = parent_image
        self._region = region

    @property
    def parent_image(self) -> Image:
        return self._parent_image

    @property
    def region(self) -> Region:
        return self._region

    def _get_numpy_image(self) -> np.ndarray:
        x_min = self._region.left
        x_max = self._region.right

        y_min = self._region.top
        y_max = self._region.bottom

        return self._parent_image._get_numpy_image()[y_min:y_max, x_min:x_max, :]


class Screen(Image):
    def __init__(self):
        super().__init__(None)

    @classmethod
    def _get_pil_image(cls):
        return pyautogui.screenshot()

    def _get_numpy_image(self):
        return np.asarray(self._get_pil_image())

    def screenshot(self):
        return Image(self._get_numpy_image())
