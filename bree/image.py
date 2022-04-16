from pathlib import Path
from typing import Union, Iterable, Tuple, Optional, List, Collection

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
from PIL import Image as PILImage
from matplotlib.patches import Rectangle

from bree.location import Region, Location
from bree.ocr import OCRMatcher

FileReferenceType = Union[str, Path]


class OutOfBoundsError(Exception):
    pass


def _find_all_within(
        needle: np.ndarray,
        haystack: np.ndarray,
        match_threshold: float = 1.0,
        *,
        match_method=cv2.TM_SQDIFF_NORMED
) -> Iterable[Tuple[Region, float]]:
    # https://stackoverflow.com/questions/7853628/how-do-i-find-an-image-contained-within-an-image/15147009#15147009
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
    def __init__(self):
        self._ocr_matchers = {}

    def _get_numpy_image(self) -> np.ndarray:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseImage):
            return NotImplemented
        return np.array_equal(self._get_numpy_image(), other._get_numpy_image())

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

    def _create_ocr_matcher(self, language, line_break, paragraph_break) -> OCRMatcher:
        return OCRMatcher(
            self._get_numpy_image(),
            language=language,
            line_break=line_break,
            paragraph_break=paragraph_break
        )

    def _get_ocr_matcher(self, language, line_break, paragraph_break):
        # TODO: OCRMatcher can probably be rewritten so it only really depends on language (i.e. _process can be run
        # TODO: when-needed and so line_break and paragraph_break can be updated)
        matcher = self._ocr_matchers.get((language, line_break, paragraph_break))
        if matcher is None:
            matcher = self._create_ocr_matcher(language, line_break, paragraph_break)
            self._ocr_matchers[(language, line_break, paragraph_break)] = matcher
        return matcher

    def get_text(self, *, language: Optional[str] = None, line_break: str = '\n', paragraph_break: str = '\n\n') -> str:
        matcher = self._get_ocr_matcher(language, line_break, paragraph_break)
        return matcher.text

    def find_image_all(
            self,
            needle: Union['BaseImage', Collection['BaseImage']],
            confidence: float = 0.99,
            *,
            match_method=cv2.TM_SQDIFF_NORMED
    ) -> Iterable['MatchedRegionInImage']:
        if isinstance(needle, BaseImage):
            needle = [needle]

        numpy_image = self._get_numpy_image()
        all_found = []  # type: List[MatchedRegionInImage]
        for n in needle:
            results = _find_all_within(
                n._get_numpy_image(),
                numpy_image,
                confidence,
                match_method=match_method
            )
            all_found.extend(
                MatchedRegionInImage.from_region_in_image(self.get_child_region(region), n, score)
                for region, score in results
            )

        return all_found

    def find_text_all(
            self,
            needle: Union[str, Collection[str]],
            confidence: float = 0.9,
            *,
            regex: bool = False,
            regex_flags=0,
            language: Optional[str] = None,
            line_break: str = '\n',
            paragraph_break: str = '\n\n',
    ) -> Iterable['MatchedRegionInImage']:
        if isinstance(needle, str):
            needle = [needle]

        matcher = self._get_ocr_matcher(language, line_break, paragraph_break)

        all_found = []  # type: List[MatchedRegionInImage]
        for n in needle:
            results = matcher.find_all(n, regex=regex, regex_flags=regex_flags)
            all_found.extend(
                MatchedRegionInImage.from_region_in_image(self.get_child_region(result.region), n, result.confidence)
                for result in results
                if result.confidence >= confidence
            )

        return all_found

    def find_all(
            self,
            needle: Union[str, 'BaseImage'],
            confidence: Optional[float] = None,
            **kwargs
    ) -> Iterable['MatchedRegionInImage']:
        if isinstance(needle, str):
            return self.find_text_all(
                needle,
                *([confidence] if confidence is not None else []),
                **kwargs,
            )
        elif isinstance(needle, BaseImage):
            return self.find_image_all(
                needle,
                *([confidence] if confidence is not None else []),
                **kwargs,
            )
        else:
            raise TypeError(f'Unrecognized type for needle: {type(needle)}')

    def find_image(
            self,
            needle: Union['BaseImage', Collection['BaseImage']],
            *args,
            **kwargs
    ) -> Optional['MatchedRegionInImage']:
        result = self.find_image_all(needle, *args, **kwargs)
        result = sorted(result, key=lambda res: res.confidence, reverse=True)
        if result:
            return result[0]
        return None

    def find_text(
            self,
            needle: Union[str, Collection[str]],
            *args,
            **kwargs
    ) -> Optional['MatchedRegionInImage']:
        result = self.find_text_all(needle, *args, **kwargs)
        result = sorted(result, key=lambda res: res.confidence, reverse=True)
        if result:
            return result[0]
        return None

    def find(
            self,
            needle: Union[str, 'BaseImage'],
            *args,
            **kwargs
    ) -> Optional['MatchedRegionInImage']:
        if isinstance(needle, str):
            return self.find_text(needle, *args, **kwargs)
        elif isinstance(needle, BaseImage):
            return self.find_image(needle, *args, **kwargs)
        else:
            raise TypeError(f'Unrecognized type for needle: {type(needle)}')

    def _wait_until_needle_appears(
            self,
            needle,
            confidence: float,
            timeout: float,
            scans_per_second: float,
            find_method,
            **find_all_args,
    ) -> List['MatchedRegionInImage']:
        scan_count = 0 if timeout * scans_per_second > 0 else -1  # We want the loop to occur at least once
        result = []
        while scan_count < timeout * scans_per_second:
            result = list(find_method(needle, confidence, **find_all_args))
            scan_count += 1
            if len(result) > 0:
                break
            else:
                pyautogui.sleep(1/scans_per_second)

        return result

    def wait_until_image_appears(
            self,
            needle: Union['BaseImage', Collection['BaseImage']],
            confidence: float = 0.99,
            timeout: float = 5,
            *,
            match_method=cv2.TM_SQDIFF_NORMED,
            scans_per_second: float = 3,
    ) -> List['MatchedRegionInImage']:
        return self._wait_until_needle_appears(
            needle,
            confidence,
            timeout,
            scans_per_second,
            self.find_image_all,
            match_method=match_method,
        )

    def wait_until_text_appears(
            self,
            needle: Union[str, Collection[str]],
            confidence: float = 0.9,
            timeout: float = 5,
            *,
            regex: bool = False,
            regex_flags=0,
            language: Optional[str] = None,
            line_break: str = '\n',
            paragraph_break: str = '\n\n',
            scans_per_second: float = 3,
    ) -> List['MatchedRegionInImage']:
        return self._wait_until_needle_appears(
            needle,
            confidence,
            timeout,
            scans_per_second,
            self.find_text_all,
            regex=regex,
            regex_flags=regex_flags,
            language=language,
            line_break=line_break,
            paragraph_break=paragraph_break,
        )

    def _wait_until_needle_vanishes(
            self,
            needle,
            confidence: float,
            timeout: float,
            scans_per_second: float,
            find_method,
            **find_all_args,
    ) -> bool:
        scan_count = 0 if timeout * scans_per_second > 0 else -1  # We want the loop to occur at least once
        while scan_count < timeout * scans_per_second:
            result = list(find_method(needle, confidence, **find_all_args))
            scan_count += 1
            if len(result) == 0:
                return True
            else:
                pyautogui.sleep(1/scans_per_second)

        return False

    def wait_until_image_vanishes(
            self,
            needle: Union['BaseImage', Collection['BaseImage']],
            confidence: float = 0.9,
            timeout: float = 5,
            *,
            match_method=cv2.TM_SQDIFF_NORMED,
            scans_per_second: float = 3,
    ) -> bool:
        return self._wait_until_needle_vanishes(
            needle,
            confidence,
            timeout,
            scans_per_second,
            self.find_image_all,
            match_method=match_method,
        )

    def wait_until_text_vanishes(
            self,
            needle: Union[str, Collection[str]],
            confidence: float = 0.99,
            timeout: float = 5,
            *,
            regex: bool = False,
            regex_flags=0,
            language: Optional[str] = None,
            line_break: str = '\n',
            paragraph_break: str = '\n\n',
            scans_per_second: float = 3,
    ) -> bool:
        return self._wait_until_needle_vanishes(
            needle,
            confidence,
            timeout,
            scans_per_second,
            self.find_text_all,
            regex=regex,
            regex_flags=regex_flags,
            language=language,
            line_break=line_break,
            paragraph_break=paragraph_break,
        )

    def contains(self, needle: Union[str, 'BaseImage'], *args, **kwargs) -> bool:
        if isinstance(needle, BaseImage):
            return self.contains_image(needle, *args, **kwargs)
        elif isinstance(needle, str):
            return self.contains_text(needle, *args, **kwargs)
        raise TypeError(f'Unsupported needle type: {type(needle)}')

    def contains_image(self, needle: Union['BaseImage', Collection['BaseImage']], *args, **kwargs) -> bool:
        return len(self.wait_until_image_appears(needle, *args, **kwargs)) > 0

    def contains_text(self, needle: Union[str, Collection[str]], *args, **kwargs) -> bool:
        return len(self.wait_until_text_appears(needle, *args, **kwargs)) > 0

    def __contains__(self, needle: Union[str, 'BaseImage']) -> bool:
        return self.contains(needle, timeout=0)


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

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(parent_image={self.parent_image!r}, region={self.region!r})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegionInImage):
            return NotImplemented

        return (
            isinstance(other, RegionInImage) and
            self._parent_image == other._parent_image and
            self._region == other._region
        )

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

    def raw_region_left(self, size: Optional[int] = None, absolute=True) -> Region:
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

    def region_left(self, size: Optional[int] = None, absolute=True) -> 'RegionInImage':
        region = self.raw_region_left(size, absolute)

        return RegionInImage(
            self._parent_image if not absolute else self._get_root_image(),
            region
        )

    def raw_region_above(self, size: Optional[int] = None, absolute=True) -> Region:
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

    def region_above(self, size: Optional[int] = None, absolute=True) -> 'RegionInImage':
        region = self.raw_region_above(size, absolute)

        return RegionInImage(
            self._parent_image if not absolute else self._get_root_image(),
            region
        )

    def raw_region_right(self, size: Optional[int] = None, absolute=True) -> Region:
        region = self.absolute_region if absolute else self.region

        left_edge = region.right + 1
        if absolute:
            total_width = self._get_root_image().width
        else:
            total_width = self._parent_image.width

        return Region(
            left_edge,
            region.y,
            (total_width - left_edge) if size is None else size,
            region.height,
        )

    def region_right(self, size: Optional[int] = None, absolute=True) -> 'RegionInImage':
        region = self.raw_region_right(size, absolute)

        return RegionInImage(
            self._parent_image if not absolute else self._get_root_image(),
            region
        )

    def raw_region_below(self, size: Optional[int] = None, absolute=True) -> Region:
        region = self.absolute_region if absolute else self.region

        top_edge = region.bottom + 1
        if absolute:
            total_height = self._get_root_image().height
        else:
            total_height = self._parent_image.height

        return Region(
            region.x,
            top_edge,
            region.width,
            (total_height - top_edge) if size is None else size,
        )

    def region_below(self, size: Optional[int] = None, absolute=True) -> 'RegionInImage':
        region = self.raw_region_below(size, absolute)

        return RegionInImage(
            self._parent_image if not absolute else self._get_root_image(),
            region
        )

    def get_left(self, absolute: bool = True) -> int:
        region = self.absolute_region if absolute else self.region
        return region.left

    @property
    def left(self) -> int:
        return self.get_left()

    def get_top(self, absolute: bool = True) -> int:
        region = self.absolute_region if absolute else self.region
        return region.top

    @property
    def top(self) -> int:
        return self.get_top()

    def get_right(self, absolute: bool = True) -> int:
        region = self.absolute_region if absolute else self.region
        return region.right

    @property
    def right(self) -> int:
        return self.get_right()

    def get_bottom(self, absolute: bool = True) -> int:
        region = self.absolute_region if absolute else self.region
        return region.bottom

    @property
    def bottom(self) -> int:
        return self.get_bottom()

    def get_min_point(self, absolute: bool = True) -> Location:
        return Location(self.get_left(absolute), self.get_top(absolute))

    @property
    def min_point(self) -> Location:
        return self.get_min_point()

    def get_max_point(self, absolute: bool = True) -> Location:
        return Location(self.get_right(absolute), self.get_bottom(absolute))

    @property
    def max_point(self) -> Location:
        return self.get_max_point()

    def get_center(self, absolute: bool = True) -> Location:
        return Location(
            (self.get_right(absolute) + self.get_left(absolute)) // 2,
            (self.get_bottom(absolute) + self.get_top(absolute)) // 2
        )

    @property
    def center(self) -> Location:
        return self.get_center()


class MatchedRegionInImage(RegionInImage):
    def __init__(self, parent_image: BaseImage, region: Region, needle: Union[BaseImage, str], confidence: float):
        super().__init__(parent_image, region)
        self._needle = needle
        self._confidence = confidence

    @classmethod
    def from_region_in_image(
            cls,
            region_in_image: RegionInImage,
            needle: Union[BaseImage, str],
            confidence: float
    ) -> 'MatchedRegionInImage':
        return cls(region_in_image.parent_image, region_in_image.region, needle, confidence)

    @property
    def needle(self) -> Union[BaseImage, str]:
        return self._needle

    @property
    def confidence(self) -> float:
        return self._confidence

    def __repr__(self) -> str:
        attributes = ('parent_image', 'region', 'confidence')
        attribute_str = ', '.join(f'{attr}={getattr(self, attr)!r}' for attr in attributes)
        return f'{self.__class__.__name__}({attribute_str})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MatchedRegionInImage):
            return NotImplemented

        return (
            isinstance(other, MatchedRegionInImage) and
            super().__eq__(other) and
            self._needle == other._needle and
            self._confidence == other._confidence
        )


class Screen(BaseImage):
    def _get_ocr_matcher(self, language, line_break, paragraph_break):
        return self._create_ocr_matcher(language, line_break, paragraph_break)

    @classmethod
    def _get_pil_image(cls):
        return pyautogui.screenshot()

    def _get_numpy_image(self):
        return np.asarray(self._get_pil_image())

    def screenshot(self) -> Image:
        return Image(self._get_numpy_image())
