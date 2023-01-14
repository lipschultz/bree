from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, call

import numpy as np
import pyautogui
import pytest
from PIL import Image as PILImage
from PIL import ImageChops

from bree.image import BaseImage, Image, MatchedRegionInImage, OutOfBoundsError, RegionInImage, Screen
from bree.location import Point, Region
from bree.ocr import OCRMatch

RESOURCES_DIR = Path(__file__).parent / "resources"


def are_pil_images_equal(img1, img2):
    # from https://stackoverflow.com/a/68402702
    equal_size = img1.height == img2.height and img1.width == img2.width

    if img1.mode == img2.mode == "RGBA":
        img1_alphas = [pixel[3] for pixel in img1.getdata()]
        img2_alphas = [pixel[3] for pixel in img2.getdata()]
        equal_alphas = img1_alphas == img2_alphas
    else:
        equal_alphas = True

    equal_content = not ImageChops.difference(img1.convert("RGB"), img2.convert("RGB")).getbbox()

    return equal_size and equal_alphas and equal_content


class TestBaseImage:
    @staticmethod
    def test_inverted_colors():
        any_image = BaseImage()
        any_numpy_image = np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]])
        any_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        actual = any_image.get_as_inverted_colors()

        expected = Image(255 - any_numpy_image)
        any_image._get_numpy_image.assert_called_once()
        assert actual == expected

    @staticmethod
    def test_inverted_colors_with_alpha_channel():
        any_image = BaseImage()
        any_numpy_image = np.array([[[1, 2, 3, 0], [4, 5, 6, 1]], [[255, 254, 253, 2], [252, 251, 250, 255]]])
        any_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        actual = any_image.get_as_inverted_colors()

        expected = Image(np.array([[[254, 253, 252, 0], [251, 250, 249, 1]], [[0, 1, 2, 2], [3, 4, 5, 255]]]))
        any_image._get_numpy_image.assert_called_once()
        assert actual == expected

    @staticmethod
    def test_height():
        any_image = BaseImage()
        any_numpy_image = np.array(
            [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[255, 254, 253], [252, 251, 250], [249, 248, 247]]]
        )
        any_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        assert any_image.height == 2
        any_image._get_numpy_image.assert_called_once()

    @staticmethod
    def test_width():
        any_image = BaseImage()
        any_numpy_image = np.array(
            [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[255, 254, 253], [252, 251, 250], [249, 248, 247]]]
        )
        any_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        assert any_image.width == 3
        any_image._get_numpy_image.assert_called_once()

    @staticmethod
    def test_region():
        any_image = BaseImage()
        any_numpy_image = np.array(
            [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[255, 254, 253], [252, 251, 250], [249, 248, 247]]]
        )
        any_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        assert any_image.region == Region(0, 0, 3, 2)


class TestImage:
    @staticmethod
    def test_getting_child_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 100, 400)

        child_image = any_image.get_child_region(region)

        expected_child_image = any_image._get_numpy_image()[30:430, 10:110, :]
        actual_child_image = child_image._get_numpy_image()

        assert (expected_child_image == actual_child_image).all()

    @staticmethod
    def test_getting_child_image_where_left_is_negative_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(-1, 30, 100, 400)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_child_image_where_top_is_negative_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, -1, 100, 400)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_child_image_where_right_exceeds_bounds_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 10_000, 400)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_child_image_where_bottom_exceeds_bounds_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 100, 40_000)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_text():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        mock_ocr_matcher = MagicMock()
        mock_ocr_matcher.text = "any value"
        any_image._get_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        actual = any_image.get_text()

        any_image._get_ocr_matcher.assert_called_once()
        assert actual == "any value"

    @staticmethod
    def test_getting_ocr_matcher_for_same_language_only_creates_it_once():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        mock_ocr_matcher = MagicMock()
        any_image._create_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        any_image._get_ocr_matcher("eng", "\n", "\n\n")
        any_image._get_ocr_matcher("eng", "\n", "\n\n")

        any_image._create_ocr_matcher.assert_called_once()

    @staticmethod
    def test_getting_ocr_matcher_for_different_language_creates_different_matchers():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        mock_ocr_matcher = MagicMock()
        any_image._create_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        any_image._get_ocr_matcher("eng", "\n", "\n\n")
        any_image._get_ocr_matcher("asd", "\n", "\n\n")

        assert any_image._create_ocr_matcher.call_count == 2
        any_image._create_ocr_matcher.assert_has_calls(
            [
                call("eng", "\n", "\n\n"),
                call("asd", "\n", "\n\n"),
            ]
        )

    @staticmethod
    def test_finding_all_instances_of_an_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle = Image(RESOURCES_DIR / "the.png")

        found = list(any_image.find_image_all(needle))

        expected = {
            Region(x=1046, y=142, width=30, height=19),
            Region(x=427, y=293, width=30, height=19),
            Region(x=704, y=293, width=30, height=19),
            Region(x=329, y=409, width=30, height=19),
        }

        assert len(found) == len(expected)
        assert all(f.confidence >= 0.99 for f in found)
        assert expected == {image.region for image in found}

    @staticmethod
    def test_finding_all_instances_of_text():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        mock_ocr_matcher = MagicMock()
        mock_ocr_matcher.find_all = MagicMock(
            return_value=[
                OCRMatch(1, 8, Region(155, 84, 24, 12), 90),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 96.697075),
            ]
        )
        any_image._get_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        found = list(
            any_image.find_text_all(
                "text", 0.89, regex=True, regex_flags=13, language="eng", line_break="\n", paragraph_break="\n\n"
            )
        )

        expected = [
            MatchedRegionInImage(any_image, Region(155, 84, 24, 12), "text", 90),
            MatchedRegionInImage(any_image, Region(50, 106, 79, 12), "text", 96.697075),
        ]

        any_image._get_ocr_matcher.assert_called_once_with("eng", "\n", "\n\n")
        mock_ocr_matcher.find_all.assert_called_once_with("text", regex=True, regex_flags=13)
        assert found == expected

    @staticmethod
    def test_finding_all_instances_of_text_when_no_results_found():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        mock_ocr_matcher = MagicMock()
        mock_ocr_matcher.find_all = MagicMock(return_value=[])
        any_image._get_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        found = list(
            any_image.find_text_all(
                "text",
                0.89,
                regex=True,
                regex_flags=13,
                language="eng",
                line_break="\n",
                paragraph_break="\n\n",
            )
        )

        expected = []

        any_image._get_ocr_matcher.assert_called_once_with("eng", "\n", "\n\n")
        mock_ocr_matcher.find_all.assert_called_once_with("text", regex=True, regex_flags=13)
        assert found == expected

    @staticmethod
    def test_finding_best_match_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle = Image(RESOURCES_DIR / "the.png")

        found = any_image.find_image(needle)

        assert found.parent_image == any_image
        assert found.region == Region(x=1046, y=142, width=30, height=19)

    @staticmethod
    def test_finding_best_match_text():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        any_image.find_text_all = MagicMock(
            return_value=[
                MatchedRegionInImage(any_image, Region(155, 84, 24, 12), "text", 90),
                MatchedRegionInImage(any_image, Region(50, 106, 79, 12), "text", 96.697075),
            ]
        )

        found = any_image.find_text(
            "text",
            0.89,
            regex=True,
            regex_flags=13,
            language="eng",
            line_break="\n",
            paragraph_break="\n\n",
        )

        assert found == MatchedRegionInImage(any_image, Region(50, 106, 79, 12), "text", 96.697075)
        any_image.find_text_all.assert_called_once_with(
            "text",
            0.89,
            regex=True,
            regex_flags=13,
            language="eng",
            line_break="\n",
            paragraph_break="\n\n",
        )

    @staticmethod
    def test_finding_best_match_text_returns_none_on_no_results_found():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        any_image.find_text_all = MagicMock(return_value=[])

        found = any_image.find_text(
            "text",
            0.89,
            regex=True,
            regex_flags=13,
            language="eng",
            line_break="\n",
            paragraph_break="\n\n",
        )

        assert found is None
        any_image.find_text_all.assert_called_once_with(
            "text",
            0.89,
            regex=True,
            regex_flags=13,
            language="eng",
            line_break="\n",
            paragraph_break="\n\n",
        )

    @staticmethod
    def test_find_all_when_given_only_one_text_needle():
        # Arrange
        any_image = BaseImage()
        expected_results = [
            MatchedRegionInImage(any_image, Region(1, 2, 3, 4), "text", 0.9),
            MatchedRegionInImage(any_image, Region(2, 5, 4, 7), "text", 0.89),
        ]
        any_image.find_text_all = mock.MagicMock(return_value=expected_results)
        any_image.find_image_all = mock.MagicMock(return_value=[])

        # Act
        actual = any_image.find_all(
            "text", text_kwargs={"regex": True, "regex_flags": 13}, image_kwargs={"match_method": None}
        )

        # Assert
        assert actual == expected_results
        any_image.find_text_all.assert_called_once_with(["text"], regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([], match_method=None)

    @staticmethod
    def test_find_all_when_given_only_text_needles():
        # Arrange
        any_image = BaseImage()
        expected_results = [
            MatchedRegionInImage(any_image, Region(1, 2, 3, 4), "text", 0.9),
            MatchedRegionInImage(any_image, Region(2, 5, 4, 7), "string", 0.89),
        ]
        any_image.find_text_all = mock.MagicMock(return_value=expected_results)
        any_image.find_image_all = mock.MagicMock(return_value=[])

        # Act
        actual = any_image.find_all(
            ["text", "string"], text_kwargs={"regex": True, "regex_flags": 13}, image_kwargs={"match_method": None}
        )

        # Assert
        assert actual == expected_results
        any_image.find_text_all.assert_called_once_with(["text", "string"], regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([], match_method=None)

    @staticmethod
    def test_find_all_when_given_only_one_image_needle():
        # Arrange
        any_image = BaseImage()
        needle_image = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        expected_results = [
            MatchedRegionInImage(any_image, Region(1, 2, 3, 4), needle_image, 0.9),
            MatchedRegionInImage(any_image, Region(2, 5, 4, 7), needle_image, 0.89),
        ]
        any_image.find_text_all = mock.MagicMock(return_value=[])
        any_image.find_image_all = mock.MagicMock(return_value=expected_results)

        # Act
        actual = any_image.find_all(
            needle_image, text_kwargs={"regex": True, "regex_flags": 13}, image_kwargs={"match_method": None}
        )

        # Assert
        assert actual == expected_results
        any_image.find_text_all.assert_called_once_with([], regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([needle_image], match_method=None)

    @staticmethod
    def test_find_all_when_given_only_image_needles():
        # Arrange
        any_image = BaseImage()
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        needle_image2 = Image(np.array([[[2, 5, 6], [25, 45, 56]], [[255, 254, 253], [252, 251, 250]]]))
        expected_results = [
            MatchedRegionInImage(any_image, Region(1, 2, 3, 4), needle_image2, 0.9),
            MatchedRegionInImage(any_image, Region(2, 5, 4, 7), needle_image1, 0.89),
        ]
        any_image.find_text_all = mock.MagicMock(return_value=[])
        any_image.find_image_all = mock.MagicMock(return_value=expected_results)

        # Act
        actual = any_image.find_all(
            [needle_image1, needle_image2],
            text_kwargs={"regex": True, "regex_flags": 13},
            image_kwargs={"match_method": None},
        )

        # Assert
        assert actual == expected_results
        any_image.find_text_all.assert_called_once_with([], regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([needle_image1, needle_image2], match_method=None)

    @staticmethod
    def test_find_all_when_given_mixed_needles_and_both_find_results():
        # Arrange
        any_image = BaseImage()
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        needle_image2 = Image(np.array([[[2, 5, 6], [25, 45, 56]], [[255, 254, 253], [252, 251, 250]]]))
        expected_text_results = [
            MatchedRegionInImage(any_image, Region(1, 3, 5, 7), "string", 0.59),
            MatchedRegionInImage(any_image, Region(2, 4, 6, 8), "text", 0.69),
        ]
        expected_image_results = [
            MatchedRegionInImage(any_image, Region(1, 2, 3, 4), needle_image2, 0.9),
            MatchedRegionInImage(any_image, Region(2, 5, 4, 7), needle_image1, 0.89),
        ]
        any_image.find_text_all = mock.MagicMock(return_value=expected_text_results)
        any_image.find_image_all = mock.MagicMock(return_value=expected_image_results)

        # Act
        actual = any_image.find_all(
            ["text", needle_image1, "string", needle_image2],
            0.88,
            text_kwargs={"regex": True, "regex_flags": 13},
            image_kwargs={"match_method": None},
        )

        # Assert
        assert actual == expected_text_results + expected_image_results
        any_image.find_text_all.assert_called_once_with(["text", "string"], 0.88, regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([needle_image1, needle_image2], 0.88, match_method=None)

    @staticmethod
    def test_find_all_when_given_mixed_needles_and_only_text_finds_results():
        # Arrange
        any_image = BaseImage()
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        needle_image2 = Image(np.array([[[2, 5, 6], [25, 45, 56]], [[255, 254, 253], [252, 251, 250]]]))
        expected_text_results = [
            MatchedRegionInImage(any_image, Region(1, 3, 5, 7), "string", 0.59),
            MatchedRegionInImage(any_image, Region(2, 4, 6, 8), "text", 0.69),
        ]
        expected_image_results = []
        any_image.find_text_all = mock.MagicMock(return_value=expected_text_results)
        any_image.find_image_all = mock.MagicMock(return_value=expected_image_results)

        # Act
        actual = any_image.find_all(
            ["text", needle_image1, "string", needle_image2],
            0.88,
            text_kwargs={"regex": True, "regex_flags": 13},
            image_kwargs={"match_method": None},
        )

        # Assert
        assert actual == expected_text_results + expected_image_results
        any_image.find_text_all.assert_called_once_with(["text", "string"], 0.88, regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([needle_image1, needle_image2], 0.88, match_method=None)

    @staticmethod
    def test_find_all_when_given_mixed_needles_and_only_image_finds_results():
        # Arrange
        any_image = BaseImage()
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        needle_image2 = Image(np.array([[[2, 5, 6], [25, 45, 56]], [[255, 254, 253], [252, 251, 250]]]))
        expected_text_results = []
        expected_image_results = [
            MatchedRegionInImage(any_image, Region(1, 2, 3, 4), needle_image2, 0.9),
            MatchedRegionInImage(any_image, Region(2, 5, 4, 7), needle_image1, 0.89),
        ]
        any_image.find_text_all = mock.MagicMock(return_value=expected_text_results)
        any_image.find_image_all = mock.MagicMock(return_value=expected_image_results)

        # Act
        actual = any_image.find_all(
            ["text", needle_image1, "string", needle_image2],
            0.88,
            text_kwargs={"regex": True, "regex_flags": 13},
            image_kwargs={"match_method": None},
        )

        # Assert
        assert actual == expected_text_results + expected_image_results
        any_image.find_text_all.assert_called_once_with(["text", "string"], 0.88, regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([needle_image1, needle_image2], 0.88, match_method=None)

    @staticmethod
    def test_find_all_passes_confidence_when_provided_as_positional_argument():
        # Arrange
        any_image = BaseImage()
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        needle_image2 = Image(np.array([[[2, 5, 6], [25, 45, 56]], [[255, 254, 253], [252, 251, 250]]]))
        any_image.find_text_all = mock.MagicMock(return_value=[])
        any_image.find_image_all = mock.MagicMock(return_value=[])

        # Act
        any_image.find_all(
            ["text", needle_image1, "string", needle_image2],
            0.88,
            text_kwargs={"regex": True, "regex_flags": 13},
            image_kwargs={"match_method": None},
        )

        # Assert
        any_image.find_text_all.assert_called_once_with(["text", "string"], 0.88, regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with([needle_image1, needle_image2], 0.88, match_method=None)

    @staticmethod
    def test_find_all_passes_confidence_when_provided_as_keyword_argument():
        # Arrange
        any_image = BaseImage()
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        needle_image2 = Image(np.array([[[2, 5, 6], [25, 45, 56]], [[255, 254, 253], [252, 251, 250]]]))
        any_image.find_text_all = mock.MagicMock(return_value=[])
        any_image.find_image_all = mock.MagicMock(return_value=[])

        # Act
        any_image.find_all(
            ["text", needle_image1, "string", needle_image2],
            text_kwargs={"confidence": 0.66, "regex": True, "regex_flags": 13},
            image_kwargs={"confidence": 0.88, "match_method": None},
        )

        # Assert
        any_image.find_text_all.assert_called_once_with(["text", "string"], confidence=0.66, regex=True, regex_flags=13)
        any_image.find_image_all.assert_called_once_with(
            [needle_image1, needle_image2], confidence=0.88, match_method=None
        )

    @staticmethod
    def test_finding_best_match():
        # Arrange
        any_image = BaseImage()
        any_image._get_numpy_image = MagicMock(return_value=np.array([[[1, 1, 1], [2, 2, 2]], [[3, 3, 3], [4, 4, 4]]]))
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        any_image.find_all = MagicMock(
            return_value=[
                MatchedRegionInImage(any_image, Region(155, 84, 24, 12), "text", 0.90),
                MatchedRegionInImage(any_image, Region(50, 106, 79, 12), needle_image1, 0.96697075),
            ]
        )

        # Act
        found = any_image.find(
            ["text", needle_image1],
            0.89,
            text_kwargs={
                "regex": True,
                "regex_flags": 13,
                "language": "eng",
                "line_break": "\n",
                "paragraph_break": "\n\n",
            },
            image_kwargs={"match_method": None},
        )

        # Assert
        assert found == MatchedRegionInImage(any_image, Region(50, 106, 79, 12), needle_image1, 0.96697075)
        any_image.find_all.assert_called_once_with(
            ["text", needle_image1],
            0.89,
            text_kwargs={
                "regex": True,
                "regex_flags": 13,
                "language": "eng",
                "line_break": "\n",
                "paragraph_break": "\n\n",
            },
            image_kwargs={"match_method": None},
        )

    @staticmethod
    def test_finding_best_match_returns_none_on_no_results_found():
        # Arrange
        any_image = BaseImage()
        any_image._get_numpy_image = MagicMock(return_value=np.array([[[1, 1, 1], [2, 2, 2]], [[3, 3, 3], [4, 4, 4]]]))
        needle_image1 = Image(np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]]))
        any_image.find_all = MagicMock(return_value=[])

        # Act
        found = any_image.find(
            ["text", needle_image1],
            0.89,
            text_kwargs={
                "regex": True,
                "regex_flags": 13,
                "language": "eng",
                "line_break": "\n",
                "paragraph_break": "\n\n",
            },
            image_kwargs={"match_method": None},
        )

        # Assert
        assert found is None
        any_image.find_all.assert_called_once_with(
            ["text", needle_image1],
            0.89,
            text_kwargs={
                "regex": True,
                "regex_flags": 13,
                "language": "eng",
                "line_break": "\n",
                "paragraph_break": "\n\n",
            },
            image_kwargs={"match_method": None},
        )


class TestBaseImageWaitUntilAppears:
    @staticmethod
    def test_wait_until_image_appears_passes_arguments_to_general_wait_until_appears_method():
        # Arrange
        subject = BaseImage()
        subject.wait_until_appears = MagicMock(return_value=[])
        any_image1 = Image(RESOURCES_DIR / "the.png")
        any_image2 = Image(RESOURCES_DIR / "wiki-python-text.png")

        # Act
        actual = subject.wait_until_image_appears(
            [any_image1, any_image2], 0.8, 10, match_method=10, scans_per_second=15
        )

        # Assert
        subject.wait_until_appears.assert_called_once_with(
            [any_image1, any_image2], 0.8, 10, scans_per_second=15, image_kwargs=dict(match_method=10)
        )
        assert actual == []

    @staticmethod
    def test_wait_until_text_appears_passes_arguments_to_general_wait_until_appears_method():
        # Arrange
        subject = BaseImage()
        subject.wait_until_appears = MagicMock(return_value=[])
        any_text1 = "text"
        any_text2 = "str"

        # Act
        actual = subject.wait_until_text_appears(
            [any_text1, any_text2],
            0.8,
            10,
            regex=True,
            regex_flags=14,
            language="deu",
            line_break="\r\n",
            paragraph_break="\r\n\r\n",
            scans_per_second=15,
        )

        # Assert
        subject.wait_until_appears.assert_called_once_with(
            [any_text1, any_text2],
            0.8,
            10,
            scans_per_second=15,
            text_kwargs=dict(regex=True, regex_flags=14, language="deu", line_break="\r\n", paragraph_break="\r\n\r\n"),
        )
        assert actual == []

    @staticmethod
    def test_wait_until_appears_returns_empty_list_when_needle_not_found_in_image():
        subject = BaseImage()
        subject.find_image_all = MagicMock(return_value=[])
        subject.find_text_all = MagicMock(return_value=[])
        needle1 = "text"
        needle2 = BaseImage()

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            found = subject.wait_until_appears(
                [needle1, needle2], 0.8, 10, scans_per_second=20, image_kwargs={"match_method": "ANY-METHOD"}
            )

            assert found == []
            assert subject.find_text_all.call_count == 200
            subject.find_text_all.assert_has_calls([call([needle1], 0.8)] * 200)
            assert subject.find_image_all.call_count == 200
            subject.find_image_all.assert_has_calls([call([needle2], 0.8, match_method="ANY-METHOD")] * 200)
            assert sleep_patch.call_count == 200
            sleep_patch.assert_has_calls([call(1 / 20)] * 200)

    @staticmethod
    def test_wait_until_appears_returns_found_region_when_needle_found_in_image_immediately():
        subject = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle1 = "text"
        needle2 = Image(RESOURCES_DIR / "the.png")
        subject.find_all = MagicMock(return_value=[MatchedRegionInImage(subject, Region(0, 0, 1, 1), needle2, 1.0)])

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            found = subject.wait_until_appears([needle1, needle2], 0.8, 10, scans_per_second=20)

            assert found == [MatchedRegionInImage(subject, Region(0, 0, 1, 1), needle2, 1.0)]
            subject.find_all.assert_has_calls([call([needle1, needle2], 0.8, text_kwargs=None, image_kwargs=None)])
            assert subject.find_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_appears_returns_found_region_when_needle_found_in_image_after_some_scans():
        subject = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle1 = "text"
        needle2 = Image(RESOURCES_DIR / "the.png")
        subject.find_all = MagicMock(
            side_effect=[
                [],
                [],
                [MatchedRegionInImage(subject, Region(0, 0, 1, 1), needle1, 1.0)],
            ]
        )

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            found = subject.wait_until_appears([needle1, needle2], 0.8, 10, scans_per_second=20)

            assert found == [MatchedRegionInImage(subject, Region(0, 0, 1, 1), needle1, 1.0)]
            subject.find_all.assert_has_calls([call([needle1, needle2], 0.8, text_kwargs=None, image_kwargs=None)])
            assert subject.find_all.call_count == 3
            assert sleep_patch.call_count == 2

    @staticmethod
    def test_wait_until_appears_scans_once_when_timeout_is_zero():
        subject = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle1 = "text"
        needle2 = Image(RESOURCES_DIR / "the.png")
        subject.find_all = MagicMock(return_value=[])

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            found = subject.wait_until_appears([needle1, needle2], 0.8, 0, scans_per_second=20)

            assert found == []
            subject.find_all.assert_has_calls([call([needle1, needle2], 0.8, text_kwargs=None, image_kwargs=None)])
            assert subject.find_all.call_count == 1
            sleep_patch.assert_called_once_with(1 / 20)


class TestBaseImageWaitUntilVanishes:
    @staticmethod
    def test_wait_until_image_vanishes_passes_arguments_to_general_wait_until_vanishes_method():
        # Arrange
        subject = BaseImage()
        subject.wait_until_vanishes = MagicMock(return_value=[])
        any_image1 = Image(RESOURCES_DIR / "the.png")
        any_image2 = Image(RESOURCES_DIR / "wiki-python-text.png")

        # Act
        actual = subject.wait_until_image_vanishes(
            [any_image1, any_image2], 0.8, 10, match_method=10, scans_per_second=15
        )

        # Assert
        subject.wait_until_vanishes.assert_called_once_with(
            [any_image1, any_image2], 0.8, 10, scans_per_second=15, image_kwargs=dict(match_method=10)
        )
        assert actual == []

    @staticmethod
    def test_wait_until_text_vanishes_passes_arguments_to_general_wait_until_vanishes_method():
        # Arrange
        subject = BaseImage()
        subject.wait_until_vanishes = MagicMock(return_value=[])
        any_text1 = "text"
        any_text2 = "str"

        # Act
        actual = subject.wait_until_text_vanishes(
            [any_text1, any_text2],
            0.8,
            10,
            regex=True,
            regex_flags=14,
            language="deu",
            line_break="\r\n",
            paragraph_break="\r\n\r\n",
            scans_per_second=15,
        )

        # Assert
        subject.wait_until_vanishes.assert_called_once_with(
            [any_text1, any_text2],
            0.8,
            10,
            scans_per_second=15,
            text_kwargs=dict(regex=True, regex_flags=14, language="deu", line_break="\r\n", paragraph_break="\r\n\r\n"),
        )
        assert actual == []

    @staticmethod
    def test_wait_until_vanishes_returns_true_when_needle_not_found_in_image():
        subject = BaseImage()
        subject.find_image_all = MagicMock(return_value=[])
        subject.find_text_all = MagicMock(return_value=[])
        needle1 = "text"
        needle2 = BaseImage()

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            result = subject.wait_until_vanishes(
                [needle1, needle2], 0.8, 10, scans_per_second=20, image_kwargs={"match_method": "ANY-METHOD"}
            )

            assert result is True
            subject.find_text_all.assert_called_once_with([needle1], 0.8)
            subject.find_image_all.assert_called_once_with([needle2], 0.8, match_method="ANY-METHOD")
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_vanishes_returns_false_when_needle_found_in_image():
        subject = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle1 = "text"
        needle2 = Image(RESOURCES_DIR / "the.png")
        subject.find_image_all = MagicMock(
            return_value=[MatchedRegionInImage(subject, Region(0, 0, 1, 1), needle2, 1.0)]
        )
        subject.find_text_all = MagicMock(return_value=[])

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            result = subject.wait_until_vanishes(
                [needle1, needle2], 0.8, 10, scans_per_second=20, image_kwargs={"match_method": "ANY-METHOD"}
            )

            assert result is False
            assert subject.find_text_all.call_count == 200
            subject.find_text_all.assert_has_calls([call([needle1], 0.8)] * 200)
            assert subject.find_image_all.call_count == 200
            subject.find_image_all.assert_has_calls([call([needle2], 0.8, match_method="ANY-METHOD")] * 200)
            assert sleep_patch.call_count == 200
            sleep_patch.assert_has_calls([call(1 / 20)] * 200)

    @staticmethod
    def test_wait_until_vanishes_returns_true_when_needle_eventually_leaves_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle = "text"
        any_image.find_all = MagicMock(
            side_effect=[
                [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), needle, 1.0)],
                [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), needle, 1.0)],
                [],
            ]
        )

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_vanishes(needle, 0.8, 10, scans_per_second=20)

            assert vanished is True
            any_image.find_all.assert_has_calls([call(needle, 0.8, text_kwargs=None, image_kwargs=None)] * 3)
            assert any_image.find_all.call_count == 3
            sleep_patch.assert_has_calls([call(1 / 20)] * 2)
            assert sleep_patch.call_count == 2

    @staticmethod
    def test_wait_until_vanishes_scans_once_when_timeout_is_zero():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle = "text"
        any_image.find_all = MagicMock(return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), needle, 1.0)])

        with mock.patch("bree.image.pyautogui.sleep", return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_vanishes(needle, 0.8, 0, scans_per_second=20)

            assert vanished is False
            any_image.find_all.assert_has_calls([call(needle, 0.8, text_kwargs=None, image_kwargs=None)])
            assert any_image.find_all.call_count == 1
            sleep_patch.assert_called_once_with(1 / 20)


class TestBaseImageContains:
    @staticmethod
    def test_contains_image_returns_false_when_needle_not_found_in_image():
        any_image = Image(RESOURCES_DIR / "the.png")
        needle = Image(RESOURCES_DIR / "wiki-python-text.png")
        any_image.wait_until_image_appears = MagicMock(return_value=[])

        found = any_image.contains_image(needle, 0.8, 10, scans_per_second=99)

        assert found is False
        any_image.wait_until_image_appears.assert_called_once_with(needle, 0.8, 10, scans_per_second=99)

    @staticmethod
    def test_contains_image_returns_true_when_needle_found_in_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle = Image(RESOURCES_DIR / "the.png")
        any_image.wait_until_image_appears = MagicMock(
            return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), needle, 1.0)]
        )

        found = any_image.contains_image(needle, 0.8, 10, scans_per_second=99)

        assert found is True
        any_image.wait_until_image_appears.assert_called_once_with(needle, 0.8, 10, scans_per_second=99)

    @staticmethod
    def test_in_returns_false_when_needle_image_not_found_in_image():
        any_image = Image(RESOURCES_DIR / "the.png")
        needle = Image(RESOURCES_DIR / "wiki-python-text.png")
        any_image.contains_image = MagicMock(return_value=False)

        found = needle in any_image

        assert found is False

    @staticmethod
    def test_in_returns_true_when_needle_image_found_in_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        needle = Image(RESOURCES_DIR / "the.png")
        any_image.contains_image = MagicMock(return_value=True)

        found = needle in any_image

        assert found is True


class TestChildImage:
    @staticmethod
    def test_height():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.height == 400

    @staticmethod
    def test_width():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.width == 100

    @staticmethod
    def test_getting_region_for_child():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.region == region

    @staticmethod
    def test_getting_absolute_region_for_child():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.absolute_region == region

    @staticmethod
    def test_getting_grandchild_image():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        expected_child_image = any_image._get_numpy_image()[35 : 100 + 35, 13 : 20 + 13, :]
        actual_child_image = grandchild_image._get_numpy_image()

        assert (expected_child_image == actual_child_image).all()

    @staticmethod
    def test_getting_region_for_grandchild():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        assert grandchild_image.region == grandchild_region

    @staticmethod
    def test_getting_absolute_region_for_grandchild():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        assert grandchild_image.absolute_region == Region(13, 35, 20, 100)

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(0, 30, 10, 400)),
            (None, True, Region(0, 30, 10, 400)),
            (3, False, Region(7, 30, 3, 400)),
            (3, True, Region(7, 30, 3, 400)),
        ],
    )
    def test_getting_raw_region_left(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.raw_region_left(size, absolute)

        assert actual_region == expected_region

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(0, 5, 3, 100)),
            (None, True, Region(0, 35, 13, 100)),
            (2, False, Region(1, 5, 2, 100)),
            (4, True, Region(9, 35, 4, 100)),
        ],
    )
    def test_getting_raw_region_left_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.raw_region_left(size, absolute)

        assert actual_region == expected_region

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(10, 0, 100, 30)),
            (None, True, Region(10, 0, 100, 30)),
            (3, False, Region(10, 27, 100, 3)),
            (3, True, Region(10, 27, 100, 3)),
        ],
    )
    def test_getting_raw_region_above(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.raw_region_above(size, absolute)

        assert actual_region == expected_region

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(3, 0, 20, 5)),
            (None, True, Region(13, 0, 20, 35)),
            (2, False, Region(3, 3, 20, 2)),
            (4, True, Region(13, 31, 20, 4)),
        ],
    )
    def test_getting_raw_region_above_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.raw_region_above(size, absolute)

        assert actual_region == expected_region

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(111, 30, 1202, 400)),
            (None, True, Region(111, 30, 1202, 400)),
            (3, False, Region(111, 30, 3, 400)),
            (3, True, Region(111, 30, 3, 400)),
        ],
    )
    def test_getting_raw_region_right(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.raw_region_right(size, absolute)

        assert actual_region == expected_region

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(24, 5, 76, 100)),
            (None, True, Region(34, 35, 1279, 100)),
            (2, False, Region(24, 5, 2, 100)),
            (4, True, Region(34, 35, 4, 100)),
        ],
    )
    def test_getting_raw_region_right_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.raw_region_right(size, absolute)

        assert actual_region == expected_region

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(10, 431, 100, 386)),
            (None, True, Region(10, 431, 100, 386)),
            (3, False, Region(10, 431, 100, 3)),
            (3, True, Region(10, 431, 100, 3)),
        ],
    )
    def test_getting_raw_region_below(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.raw_region_below(size, absolute)

        assert actual_region == expected_region

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(3, 106, 20, 294)),
            (None, True, Region(13, 136, 20, 681)),
            (2, False, Region(3, 106, 20, 2)),
            (4, True, Region(13, 136, 20, 4)),
        ],
    )
    def test_getting_raw_region_below_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.raw_region_below(size, absolute)

        assert actual_region == expected_region

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(0, 30, 10, 400)),
            (None, True, Region(0, 30, 10, 400)),
            (3, False, Region(7, 30, 3, 400)),
            (3, True, Region(7, 30, 3, 400)),
        ],
    )
    def test_getting_region_left(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.region_left(size, absolute)

        assert actual_region == RegionInImage(any_image, expected_region)

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(0, 5, 3, 100)),
            (None, True, Region(0, 35, 13, 100)),
            (2, False, Region(1, 5, 2, 100)),
            (4, True, Region(9, 35, 4, 100)),
        ],
    )
    def test_getting_region_left_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.region_left(size, absolute)

        assert actual_region == RegionInImage(any_image if absolute else child_image, expected_region)

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(10, 0, 100, 30)),
            (None, True, Region(10, 0, 100, 30)),
            (3, False, Region(10, 27, 100, 3)),
            (3, True, Region(10, 27, 100, 3)),
        ],
    )
    def test_getting_region_above(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.region_above(size, absolute)

        assert actual_region == RegionInImage(any_image, expected_region)

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(3, 0, 20, 5)),
            (None, True, Region(13, 0, 20, 35)),
            (2, False, Region(3, 3, 20, 2)),
            (4, True, Region(13, 31, 20, 4)),
        ],
    )
    def test_getting_region_above_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.region_above(size, absolute)

        assert actual_region == RegionInImage(any_image if absolute else child_image, expected_region)

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(111, 30, 1202, 400)),
            (None, True, Region(111, 30, 1202, 400)),
            (3, False, Region(111, 30, 3, 400)),
            (3, True, Region(111, 30, 3, 400)),
        ],
    )
    def test_getting_region_right(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.region_right(size, absolute)

        assert actual_region == RegionInImage(any_image, expected_region)

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(24, 5, 76, 100)),
            (None, True, Region(34, 35, 1279, 100)),
            (2, False, Region(24, 5, 2, 100)),
            (4, True, Region(34, 35, 4, 100)),
        ],
    )
    def test_getting_region_right_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.region_right(size, absolute)

        assert actual_region == RegionInImage(any_image if absolute else child_image, expected_region)

    @staticmethod
    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(10, 431, 100, 386)),
            (None, True, Region(10, 431, 100, 386)),
            (3, False, Region(10, 431, 100, 3)),
            (3, True, Region(10, 431, 100, 3)),
        ],
    )
    def test_getting_region_below(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        actual_region = child_image.region_below(size, absolute)

        assert actual_region == RegionInImage(any_image, expected_region)

    @pytest.mark.parametrize(
        "size,absolute,expected_region",
        [
            (None, False, Region(3, 106, 20, 294)),
            (None, True, Region(13, 136, 20, 681)),
            (2, False, Region(3, 106, 20, 2)),
            (4, True, Region(13, 136, 20, 4)),
        ],
    )
    def test_getting_region_below_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.region_below(size, absolute)

        assert actual_region == RegionInImage(any_image if absolute else child_image, expected_region)

    @staticmethod
    def test_get_numpy_image_calls_parents_get_numpy_image():
        # Arrange
        parent_image = BaseImage()
        any_numpy_image = np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]])
        parent_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        child_region = Region(0, 0, 1, 1)
        child_image = parent_image.get_child_region(child_region)
        parent_image._get_numpy_image.reset_mock()

        # Act
        child_image._get_numpy_image()

        # Assert
        parent_image._get_numpy_image.assert_called_once_with()

    @staticmethod
    def test_get_numpy_image_calls_parents_get_numpy_image_each_time():
        # Arrange
        parent_image = BaseImage()
        any_numpy_image = np.array([[[1, 2, 3], [4, 5, 6]], [[255, 254, 253], [252, 251, 250]]])
        parent_image._get_numpy_image = MagicMock(return_value=any_numpy_image)

        child_region = Region(0, 0, 1, 1)
        child_image = parent_image.get_child_region(child_region)
        parent_image._get_numpy_image.reset_mock()

        # Act
        child_image._get_numpy_image()
        child_image._get_numpy_image()
        child_image._get_numpy_image()

        # Assert
        assert parent_image._get_numpy_image.call_count == 3


class TestRegionInImage:
    @staticmethod
    @pytest.mark.parametrize(
        "is_absolute",
        [True, False],
    )
    def test_get_max_point_when_parent_image_has_no_ancestor(is_absolute):
        image = BaseImage()
        region = Region(10, 5, 20, 40)
        subject = RegionInImage(image, region)

        point = subject.get_max_point(is_absolute)

        assert point == Point(30, 45)

    @staticmethod
    @pytest.mark.parametrize(
        "grandparent_region, parent_region, is_absolute, expected_point",
        [
            (Region(10, 5, 200, 400), Region(20, 10, 30, 22), False, Point(50, 32)),
            (Region(10, 5, 200, 400), Region(20, 10, 30, 22), True, Point(60, 37)),
            (Region(10, 5, 200, 400), Region(5, 2, 30, 22), False, Point(35, 24)),
            (Region(10, 5, 200, 400), Region(5, 2, 30, 22), True, Point(45, 29)),
        ],
    )
    def test_get_max_point_when_parent_image_has_ancestor(
        grandparent_region, parent_region, is_absolute, expected_point
    ):
        grandparent_image = BaseImage()
        parent_image = RegionInImage(grandparent_image, grandparent_region)
        subject = RegionInImage(parent_image, parent_region)

        point = subject.get_max_point(is_absolute)

        assert point == expected_point

    @staticmethod
    def test_max_point_property():
        image = BaseImage()
        region = Region(10, 5, 20, 40)
        subject = RegionInImage(image, region)
        subject.get_max_point = MagicMock(return_value=Point(7, 13))

        point = subject.max_point

        assert point == Point(7, 13)
        subject.get_max_point.assert_called_once_with()

    @staticmethod
    @pytest.mark.parametrize(
        "region, is_absolute, expected_center",
        [
            (Region(10, 5, 20, 40), True, Point(20, 25)),
            (Region(10, 5, 21, 41), True, Point(20, 25)),
            (Region(10, 5, 20, 40), False, Point(20, 25)),
            (Region(10, 5, 21, 41), False, Point(20, 25)),
        ],
    )
    def test_get_center_when_parent_image_has_no_ancestor(region, is_absolute, expected_center):
        image = BaseImage()
        subject = RegionInImage(image, region)

        center = subject.get_center(is_absolute)

        assert center == expected_center

    @staticmethod
    @pytest.mark.parametrize(
        "grandparent_region, parent_region, is_absolute, expected_center",
        [
            (Region(10, 5, 200, 400), Region(20, 10, 30, 22), False, Point(35, 21)),
            (Region(10, 5, 200, 400), Region(20, 10, 31, 23), False, Point(35, 21)),
            (Region(10, 5, 200, 400), Region(20, 10, 30, 22), True, Point(45, 26)),
            (Region(10, 5, 200, 400), Region(20, 10, 31, 23), True, Point(45, 26)),
            (Region(10, 5, 200, 400), Region(5, 2, 30, 22), False, Point(20, 13)),
            (Region(10, 5, 200, 400), Region(5, 2, 31, 23), False, Point(20, 13)),
            (Region(10, 5, 200, 400), Region(5, 2, 30, 22), True, Point(30, 18)),
            (Region(10, 5, 200, 400), Region(5, 2, 31, 23), True, Point(30, 18)),
        ],
    )
    def test_get_center_when_parent_image_has_ancestor(grandparent_region, parent_region, is_absolute, expected_center):
        grandparent_image = BaseImage()
        parent_image = RegionInImage(grandparent_image, grandparent_region)
        subject = RegionInImage(parent_image, parent_region)

        center = subject.get_center(is_absolute)

        assert center == expected_center

    @staticmethod
    def test_center_property():
        image = BaseImage()
        region = Region(10, 5, 20, 40)
        subject = RegionInImage(image, region)
        subject.get_center = MagicMock(return_value=Point(7, 13))

        center = subject.center

        assert center == Point(7, 13)
        subject.get_center.assert_called_once_with()


class TestScreen:
    @staticmethod
    def test_getting_ocr_matcher_for_same_language_creates_it_each_time():
        any_image = Screen()
        mock_ocr_matcher = MagicMock()
        any_image._create_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        any_image._get_ocr_matcher("eng", "\n", "\n\n")
        any_image._get_ocr_matcher("eng", "\n", "\n\n")

        assert any_image._create_ocr_matcher.call_count == 2
        any_image._create_ocr_matcher.assert_has_calls(
            [
                call("eng", "\n", "\n\n"),
                call("eng", "\n", "\n\n"),
            ]
        )

    @staticmethod
    def test_getting_screenshot_takes_a_screenshot():
        any_image = Screen()
        fake_screenshot = PILImage.new("RGB", (100, 100))
        pyautogui.screenshot = MagicMock(return_value=fake_screenshot)

        actual = any_image.screenshot()

        pyautogui.screenshot.assert_called_once_with()
        assert (actual._get_numpy_image() == np.asarray(fake_screenshot)).all()

    @staticmethod
    def test_calling_screenshot_takes_a_new_screenshot_each_time():
        any_image = Screen()
        fake_screenshot1 = PILImage.new("RGB", (100, 100))
        fake_screenshot2 = PILImage.new("RGB", (10, 10))
        pyautogui.screenshot = MagicMock(side_effect=[fake_screenshot1, fake_screenshot2])

        first_screenshot = any_image.screenshot()
        second_screenshot = any_image.screenshot()

        assert pyautogui.screenshot.call_count == 2
        assert (first_screenshot._get_numpy_image() == np.asarray(fake_screenshot1)).all()
        assert (second_screenshot._get_numpy_image() == np.asarray(fake_screenshot2)).all()

    @staticmethod
    def test_calling_get_numpy_image_takes_new_screenshot_each_time():
        any_image = Screen()
        fake_screenshot1 = PILImage.new("RGB", (100, 100))
        fake_screenshot2 = PILImage.new("RGB", (10, 10))
        pyautogui.screenshot = MagicMock(side_effect=[fake_screenshot1, fake_screenshot2])

        first_screenshot = any_image._get_numpy_image()
        second_screenshot = any_image._get_numpy_image()

        assert pyautogui.screenshot.call_count == 2
        assert (first_screenshot == np.asarray(fake_screenshot1)).all()
        assert (second_screenshot == np.asarray(fake_screenshot2)).all()

    @staticmethod
    def test_calling_find_all_only_takes_one_screenshot():
        # Arrange
        screen = Screen()
        fake_screenshot = PILImage.open(str(RESOURCES_DIR / "wiki-python-text.png"))
        pyautogui.screenshot = MagicMock(return_value=fake_screenshot)
        needle_image = Image(RESOURCES_DIR / "the.png")

        # Act
        screen.find_all(["text", needle_image])

        # Assert
        assert pyautogui.screenshot.call_count == 1

    @staticmethod
    def test_saving_screenshot(tmp_path):
        # Arrange
        screen = Screen()
        fake_screenshot = PILImage.open(str(RESOURCES_DIR / "wiki-python-text.png"))
        pyautogui.screenshot = MagicMock(return_value=fake_screenshot)

        # Act
        screen.save(tmp_path / "out.png")

        # Assert
        saved_screenshot = PILImage.open(str(tmp_path / "out.png"))
        assert are_pil_images_equal(saved_screenshot, fake_screenshot)
