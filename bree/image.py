from collections.abc import MutableMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Iterable, Tuple, Optional, Iterator, KeysView, ValuesView, overload

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import pyautogui
from matplotlib.patches import Rectangle

FileReferenceType = Union[str, Path]


class OutOfBoundsError(Exception):
    pass


class InvalidRegionError(Exception):
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


class BaseImage:
    def _get_numpy_image(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def width(self) -> int:
        return self._get_numpy_image().shape[1]

    @property
    def height(self) -> int:
        return self._get_numpy_image().shape[0]

    @property
    def region(self) -> Region:
        return Region(0, 0, self.width, self.height)

    def show(self, *, bounding_boxes: Iterable[Region] = ()) -> None:
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
                edgecolor='b',
                facecolor='none',
            ))

        plt.show()

    def get_child_region(self, region: Region) -> 'RegionInImage':
        if region.left < 0:
            raise OutOfBoundsError(f'region.x={region.left}.  Value must be at least zero.')
        if region.top < 0:
            raise OutOfBoundsError(f'region.y={region.top}.  Value must be at least zero.')

        if region.right >= self.width:
            raise OutOfBoundsError(f'region.right={region.right}.  Value exceeds size of image (width={self.width}).')
        if region.bottom >= self.height:
            raise OutOfBoundsError(f'region.left={region.left}.  Value exceeds size of image (height={self.height}).')

        return RegionInImage(self, region)

    def find_image_all(self, needle: 'BaseImage', confidence: float = 0.99, *, match_method=cv2.TM_SQDIFF_NORMED) -> Iterable[Tuple['RegionInImage', float]]:
        found = _find_all_within(
            needle._get_numpy_image(),
            self._get_numpy_image(),
            confidence,
            match_method=match_method
        )
        results = []
        for region, score in found:
            child = self.get_child_region(region)
            results.append((child, score))
        return results
        # return ((self.get_child_region(region), score) for region, score in found)

    def find_image(self, needle: 'BaseImage', *args, **kwargs) -> Optional['RegionInImage']:
        result = self.find_image_all(needle, *args, **kwargs)
        result = sorted(result, key=lambda res: res[1], reverse=True)
        if result:
            return result[0][0]
        return None


class Image(BaseImage):
    def __init__(self, image: Union[FileReferenceType, np.ndarray, PILImage.Image]):
        super().__init__()
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
                    # Remove alpha channel.  This is necessary for `find_image_all`, where color dimension needs to
                    # match between the two images (and the datatype, e.g. uint8 vs float, but for now this isn't
                    # checked/corrected).
                    image = image[:, :, :3]
                self.__numpy_image = image
            else:
                raise TypeError(f'Unrecognized type for image: {self._original_image!r}')
        return self.__numpy_image

    def __repr__(self):
        return f'Image(image={self._original_image!r})'


class RegionInImage(BaseImage):
    def __init__(self, parent_image: BaseImage, region: Region):
        super().__init__()
        self._parent_image = parent_image
        self._region = region

    def __repr__(self):
        return f'{self.__class__.__name__}(parent_image={self.parent_image!r}, region={self.region!r})'

    @property
    def parent_image(self) -> BaseImage:
        return self._parent_image

    @property
    def region(self) -> Region:
        return self._region

    @property
    def absolute_region(self) -> Region:
        if isinstance(self._parent_image, RegionInImage):
            parent_absolute_region = self._parent_image.absolute_region
            return Region(
                parent_absolute_region.x + self.region.x,
                parent_absolute_region.y + self.region.y,
                self.region.width,
                self.region.height,
            )
        else:
            return self.region

    def _get_root_image(self) -> BaseImage:
        if isinstance(self._parent_image, RegionInImage):
            return self._parent_image._get_root_image()
        return self._parent_image

    def _get_numpy_image(self) -> np.ndarray:
        x_min = self._region.left
        x_max = self._region.right

        y_min = self._region.top
        y_max = self._region.bottom

        return self._parent_image._get_numpy_image()[y_min:y_max, x_min:x_max, :]

    def region_left(self, size: Optional[int] = None, absolute=True) -> Region:
        region = self.absolute_region if absolute else self.region

        if size is None:
            left_edge = 0
        else:
            left_edge = max(region.x - size, 0)

        return Region(
            left_edge,
            region.y,
            region.x - left_edge,
            region.height,
        )

    def region_above(self, size: Optional[int] = None, absolute=True) -> Region:
        region = self.absolute_region if absolute else self.region

        if size is None:
            top_edge = 0
        else:
            top_edge = max(region.y - size, 0)

        return Region(
            region.x,
            top_edge,
            region.width,
            region.y - top_edge,
        )


class Screen(BaseImage):
    @classmethod
    def _get_pil_image(cls):
        return pyautogui.screenshot()

    def _get_numpy_image(self):
        return np.asarray(self._get_pil_image())

    def screenshot(self) -> Image:
        return Image(self._get_numpy_image())
