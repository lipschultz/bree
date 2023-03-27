from difflib import SequenceMatcher
from itertools import zip_longest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytesseract

from pin_the_tail.image import Image
from pin_the_tail.location import Region
from pin_the_tail.ocr import OCRMatch, OCRMatcher

RESOURCES_DIR = Path(__file__).parent / "resources"


ANY_IMAGE_FILEPATH = RESOURCES_DIR / "wiki-python-text.png"
ANY_IMAGE_TEXT = "Python (programming language)\n\n \n\nFrom Wikipedia, the free encyclopedia\n(Redirected from Python (Programming Language))"
ANY_IMAGE_RAW_TESSERACT_OUTPUT = pd.DataFrame(
    [
        {
            "level": 1,
            "page_num": 1,
            "block_num": 0,
            "par_num": 0,
            "line_num": 0,
            "word_num": 0,
            "left": 0,
            "top": 0,
            "width": 1313,
            "height": 817,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 2,
            "page_num": 1,
            "block_num": 1,
            "par_num": 0,
            "line_num": 0,
            "word_num": 0,
            "left": 26,
            "top": 29,
            "width": 447,
            "height": 32,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 3,
            "page_num": 1,
            "block_num": 1,
            "par_num": 1,
            "line_num": 0,
            "word_num": 0,
            "left": 26,
            "top": 29,
            "width": 447,
            "height": 32,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 4,
            "page_num": 1,
            "block_num": 1,
            "par_num": 1,
            "line_num": 1,
            "word_num": 0,
            "left": 26,
            "top": 29,
            "width": 447,
            "height": 32,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 1,
            "par_num": 1,
            "line_num": 1,
            "word_num": 1,
            "left": 26,
            "top": 29,
            "width": 98,
            "height": 32,
            "conf": 96.839996,
            "text": "Python",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 1,
            "par_num": 1,
            "line_num": 1,
            "word_num": 2,
            "left": 135,
            "top": 29,
            "width": 195,
            "height": 32,
            "conf": 96.485741,
            "text": "(programming",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 1,
            "par_num": 1,
            "line_num": 1,
            "word_num": 3,
            "left": 340,
            "top": 29,
            "width": 133,
            "height": 32,
            "conf": 96.132133,
            "text": "language)",
        },
        {
            "level": 2,
            "page_num": 1,
            "block_num": 2,
            "par_num": 0,
            "line_num": 0,
            "word_num": 0,
            "left": 26,
            "top": 59,
            "width": 1287,
            "height": 21,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 3,
            "page_num": 1,
            "block_num": 2,
            "par_num": 1,
            "line_num": 0,
            "word_num": 0,
            "left": 26,
            "top": 59,
            "width": 1287,
            "height": 21,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 4,
            "page_num": 1,
            "block_num": 2,
            "par_num": 1,
            "line_num": 1,
            "word_num": 0,
            "left": 26,
            "top": 59,
            "width": 1287,
            "height": 21,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 2,
            "par_num": 1,
            "line_num": 1,
            "word_num": 1,
            "left": 26,
            "top": 59,
            "width": 1287,
            "height": 21,
            "conf": 95.0,
            "text": " ",
        },
        {
            "level": 2,
            "page_num": 1,
            "block_num": 3,
            "par_num": 0,
            "line_num": 0,
            "word_num": 0,
            "left": 27,
            "top": 84,
            "width": 384,
            "height": 36,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 3,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 0,
            "word_num": 0,
            "left": 27,
            "top": 84,
            "width": 384,
            "height": 36,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 4,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 1,
            "word_num": 0,
            "left": 27,
            "top": 84,
            "width": 294,
            "height": 15,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 1,
            "word_num": 1,
            "left": 27,
            "top": 84,
            "width": 36,
            "height": 12,
            "conf": 96.981003,
            "text": "From",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 1,
            "word_num": 2,
            "left": 69,
            "top": 84,
            "width": 79,
            "height": 15,
            "conf": 94.515457,
            "text": "Wikipedia,",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 1,
            "word_num": 3,
            "left": 155,
            "top": 84,
            "width": 24,
            "height": 12,
            "conf": 94.887207,
            "text": "the",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 1,
            "word_num": 4,
            "left": 185,
            "top": 84,
            "width": 30,
            "height": 12,
            "conf": 95.936913,
            "text": "free",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 1,
            "word_num": 5,
            "left": 220,
            "top": 84,
            "width": 101,
            "height": 15,
            "conf": 96.515205,
            "text": "encyclopedia",
        },
        {
            "level": 4,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 2,
            "word_num": 0,
            "left": 50,
            "top": 106,
            "width": 361,
            "height": 14,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 2,
            "word_num": 1,
            "left": 50,
            "top": 106,
            "width": 79,
            "height": 12,
            "conf": 96.697075,
            "text": "(Redirected",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 2,
            "word_num": 2,
            "left": 135,
            "top": 106,
            "width": 32,
            "height": 11,
            "conf": 96.729462,
            "text": "from",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 2,
            "word_num": 3,
            "left": 174,
            "top": 106,
            "width": 47,
            "height": 14,
            "conf": 95.819839,
            "text": "Python",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 2,
            "word_num": 4,
            "left": 227,
            "top": 106,
            "width": 99,
            "height": 14,
            "conf": 93.306213,
            "text": "(Programming",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 3,
            "par_num": 1,
            "line_num": 2,
            "word_num": 5,
            "left": 332,
            "top": 106,
            "width": 79,
            "height": 14,
            "conf": 92.09182,
            "text": "Language))",
        },
        {
            "level": 2,
            "page_num": 1,
            "block_num": 4,
            "par_num": 0,
            "line_num": 0,
            "word_num": 0,
            "left": 27,
            "top": 145,
            "width": 1197,
            "height": 18,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 3,
            "page_num": 1,
            "block_num": 4,
            "par_num": 1,
            "line_num": 0,
            "word_num": 0,
            "left": 27,
            "top": 145,
            "width": 1197,
            "height": 18,
            "conf": -1.0,
            "text": np.nan,
        },
        {
            "level": 4,
            "page_num": 1,
            "block_num": 4,
            "par_num": 1,
            "line_num": 1,
            "word_num": 0,
            "left": 27,
            "top": 145,
            "width": 1197,
            "height": 18,
            "conf": -1.0,
            "text": np.nan,
        },
    ]
)
ANY_IMAGE_TEXT_POSITIONS = [
    OCRMatch(0, 6, Region(26, 29, 98, 32), 0.96839996),
    OCRMatch(6, 7, Region(124, 29, 11, 32), None),
    OCRMatch(7, 19, Region(135, 29, 195, 32), 0.96485741),
    OCRMatch(19, 20, Region(330, 29, 10, 32), None),
    OCRMatch(20, 29, Region(340, 29, 133, 32), 0.96132133),
    OCRMatch(29, 31, Region(473, 29, -447, 32), None),
    OCRMatch(31, 32, Region(26, 59, 1287, 21), 0.950),
    OCRMatch(32, 34, Region(1313, 59, -1286, 21), None),
    OCRMatch(34, 38, Region(27, 84, 36, 12), 0.96981003),
    OCRMatch(38, 39, Region(63, 84, 6, 12), None),
    OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
    OCRMatch(49, 50, Region(148, 84, 7, 15), None),
    OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),  # "the"
    OCRMatch(53, 54, Region(179, 84, 6, 12), None),
    OCRMatch(54, 58, Region(185, 84, 30, 12), 0.95936913),
    OCRMatch(58, 59, Region(215, 84, 5, 12), None),
    OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
    OCRMatch(71, 72, Region(321, 84, -271, 15), None),
    OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
    OCRMatch(83, 84, Region(129, 106, 6, 12), None),
    OCRMatch(84, 88, Region(135, 106, 32, 11), 0.96729462),
    OCRMatch(88, 89, Region(167, 106, 7, 11), None),
    OCRMatch(89, 95, Region(174, 106, 47, 14), 0.95819839),
    OCRMatch(95, 96, Region(221, 106, 6, 14), None),
    OCRMatch(96, 108, Region(227, 106, 99, 14), 0.93306213),
    OCRMatch(108, 109, Region(326, 106, 6, 14), None),
    OCRMatch(109, 119, Region(332, 106, 79, 14), 0.9209182),
]


def assert_ocr_match_equal(match1, match2, confidence_tolerance=1e-8):
    assert isinstance(match1, OCRMatch)
    assert isinstance(match2, OCRMatch)
    assert match1.index_start == match2.index_start
    assert match1.index_end == match2.index_end
    assert match1.region == match2.region

    assert (match1.confidence is None and match2.confidence is None) or abs(
        match1.confidence - match2.confidence
    ) < confidence_tolerance


class TestOCRMatcher:
    @staticmethod
    def test_interface_with_pytesseract():
        any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
        any_image_text = (RESOURCES_DIR / "wiki-python-text.txt").read_text()

        matcher = OCRMatcher(any_image._get_numpy_image())

        assert SequenceMatcher(None, matcher.text, any_image_text).ratio() > 0.75
        assert set(matcher._df.columns) >= {
            "page_num",
            "block_num",
            "par_num",
            "left",
            "line_num",
            "text",
            "top",
            "width",
            "height",
        }

    @staticmethod
    def test_loading_image_with_text():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)

        matcher = OCRMatcher(any_image._get_numpy_image())

        pytesseract.image_to_data.assert_called_once_with(
            any_image._get_numpy_image(), lang=None, output_type=pytesseract.Output.DATAFRAME
        )
        assert matcher.text == ANY_IMAGE_TEXT
        for actual, expected in zip_longest(matcher._ocr_segments, ANY_IMAGE_TEXT_POSITIONS):
            assert_ocr_match_equal(actual, expected)


class TestFindingBoundingBoxes:
    @staticmethod
    def test_finding_complete_single_word():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("the")

        assert result[0] == 50
        assert result[1] == 53
        for actual, expected in zip_longest(result[2], [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)]):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_complete_single_word_using_regex():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("[tT]he", regex=True)

        assert result[0] == 50
        assert result[1] == 53
        for actual, expected in zip_longest(result[2], [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)]):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_complete_single_word_with_start_offset():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("the", start=20)

        assert result[0] == 50
        assert result[1] == 53
        for actual, expected in zip_longest(result[2], [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)]):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_complete_single_word_using_regex_with_start_offset():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("[tT]he", regex=True, start=20)

        assert result[0] == 50
        assert result[1] == 53
        for actual, expected in zip_longest(result[2], [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)]):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_latter_part_of_single_word_finds_entire_words_bounding_box():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("he")

        assert result[0] == 51
        assert result[1] == 53
        for actual, expected in zip_longest(result[2], [OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)]):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_beginning_part_of_single_word_finds_entire_words_bounding_box():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("(Red")

        assert result[0] == 72
        assert result[1] == 76
        for actual, expected in zip_longest(result[2], [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)]):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_complete_single_word_with_preceding_space():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes(" the")

        assert result[0] == 49
        assert result[1] == 53
        for actual, expected in zip_longest(
            result[2],
            [OCRMatch(49, 50, Region(148, 84, 7, 15), None), OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207)],
        ):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_complete_single_word_with_space_before_and_after():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes(" the ")

        assert result[0] == 49
        assert result[1] == 54
        for actual, expected in zip_longest(
            result[2],
            [
                OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                OCRMatch(53, 54, Region(179, 84, 6, 12), None),
            ],
        ):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_two_words():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("Wikipedia, the")

        assert result[0] == 39
        assert result[1] == 53
        for actual, expected in zip_longest(
            result[2],
            [
                OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
            ],
        ):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_complete_single_word_on_second_line():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("(Redirected")

        assert result[0] == 72
        assert result[1] == 83
        for actual, expected in zip_longest(
            result[2],
            [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)],
        ):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_specifying_end_before_token_found_fails_to_find_token():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("(Redirected", end=50)

        assert result[0] == -1
        assert result[1] == -1
        assert result[2] == []

    @staticmethod
    def test_specifying_end_before_token_found_fails_to_find_token_using_regex():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes(r"\([rR]edirected", regex=True, end=50)

        assert result[0] == -1
        assert result[1] == -1
        assert result[2] == []

    @staticmethod
    def test_finding_two_words_on_separate_lines():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("encyclopedia\n(Redirected")

        assert result[0] == 59
        assert result[1] == 83
        for actual, expected in zip_longest(
            result[2],
            [
                OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
                OCRMatch(71, 72, Region(321, 84, -271, 15), None),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
            ],
        ):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_finding_needle_with_regex_pattern():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes(r"encyclopedia\s+\(Redirected", regex=True)

        assert result[0] == 59
        assert result[1] == 83
        for actual, expected in zip_longest(
            result[2],
            [
                OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
                OCRMatch(71, 72, Region(321, 84, -271, 15), None),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
            ],
        ):
            assert_ocr_match_equal(actual, expected)

    @staticmethod
    def test_failing_to_find_needle():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("NOT IN TEXT")

        assert result[0] == -1
        assert result[1] == -1
        assert result[2] == []

    @staticmethod
    def test_failing_to_find_needle_using_regex():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("NOT IN TEXT", regex=True)

        assert result[0] == -1
        assert result[1] == -1
        assert result[2] == []

    @staticmethod
    def test_specifying_start_after_token_found_fails_to_find_token():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("Wikipedia", start=100)

        assert result[0] == -1
        assert result[1] == -1
        assert result[2] == []

    @staticmethod
    def test_specifying_start_after_token_found_fails_to_find_token_using_regex():
        any_image = Image(ANY_IMAGE_FILEPATH)
        pytesseract.image_to_data = MagicMock(return_value=ANY_IMAGE_RAW_TESSERACT_OUTPUT)
        matcher = OCRMatcher(any_image._get_numpy_image())

        result = matcher.find_bounding_boxes("Wikipedia", start=100, regex=True)

        assert result[0] == -1
        assert result[1] == -1
        assert result[2] == []

    @staticmethod
    def test_finding_all_when_there_are_no_results_returns_empty_list():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(return_value=(-1, -1, []))

            assert matcher.find_bounding_boxes_all("NOT IN TEXT") == []

    @staticmethod
    def test_finding_all_when_there_is_one_result_returns_list_with_one_result():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                side_effect=[
                    (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)]),
                    (-1, -1, []),
                ]
            )

            assert matcher.find_bounding_boxes_all("Wikipedia") == [
                (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)]),
            ]

    @staticmethod
    def test_finding_all_when_there_is_one_result_but_multiple_boxes_returns_list_with_one_result():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                side_effect=[
                    (
                        39,
                        53,
                        [
                            OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                            OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                            OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                        ],
                    ),
                    (-1, -1, []),
                ]
            )

            assert matcher.find_bounding_boxes_all("Wikipedia") == [
                (
                    39,
                    53,
                    [
                        OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                        OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                        OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                    ],
                ),
            ]

    @staticmethod
    def test_finding_all_when_there_are_many_results():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                side_effect=[
                    (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 90)]),
                    (72, 83, [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)]),
                    (-1, -1, []),
                ]
            )

            assert matcher.find_bounding_boxes_all("Wikipedia") == [
                (3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 90)]),
                (72, 83, [OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075)]),
            ]


class TestFind:
    @staticmethod
    def test_failing_to_find_needle():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher._parsed_text = ANY_IMAGE_TEXT
            matcher._ocr_segments = ANY_IMAGE_TEXT_POSITIONS
            matcher.find_bounding_boxes = MagicMock(return_value=(-1, -1, []))

            assert matcher.find("NOT IN TEXT") is None
            matcher.find_bounding_boxes.assert_called_once_with("NOT IN TEXT", None, None, False, 0)

    @staticmethod
    def test_finding_one_bounding_box_where_indices_match_text_result_indices():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                return_value=(1, 8, [OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)])
            )

            assert matcher.find("IN TEXT") == OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)

    @staticmethod
    def test_finding_one_bounding_box_where_indices_dont_match_text_result_indices():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                return_value=(3, 7, [OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90)])
            )

            assert matcher.find("N TEX") == OCRMatch(3, 7, Region(155, 84, 24, 12), 0.90)

    @staticmethod
    def test_finding_bounding_boxes_on_same_line():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                return_value=(
                    39,
                    53,
                    [
                        OCRMatch(39, 49, Region(69, 84, 79, 15), 0.94515457),
                        OCRMatch(49, 50, Region(148, 84, 7, 15), None),
                        OCRMatch(50, 53, Region(155, 84, 24, 12), 0.94887207),
                    ],
                )
            )

            assert matcher.find("Wikipedia, the") == OCRMatch(39, 53, Region(69, 84, 110, 15), 0.94515457)

    @staticmethod
    def test_finding_bounding_boxes_across_lines():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find_bounding_boxes = MagicMock(
                return_value=(
                    59,
                    83,
                    [
                        OCRMatch(59, 71, Region(220, 84, 101, 15), 0.96515205),
                        OCRMatch(71, 72, Region(321, 84, -271, 15), None),
                        OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
                    ],
                )
            )

            assert matcher.find("encyclopedia\n(Redirected") == OCRMatch(59, 83, Region(50, 84, 271, 34), 0.96515205)

    @staticmethod
    def test_finding_all_when_there_are_no_results_returns_empty_list():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find = MagicMock(return_value=None)

            assert matcher.find_all("NOT IN TEXT") == []

    @staticmethod
    def test_finding_all_when_there_is_one_result_returns_list_with_one_result():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find = MagicMock(
                side_effect=[
                    OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
                    None,
                ]
            )

            assert matcher.find_all("Wikipedia") == [
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
            ]

    @staticmethod
    def test_finding_all_when_there_are_many_results():
        with patch("pin_the_tail.ocr.OCRMatcher.process"):
            any_image = Image(RESOURCES_DIR / "wiki-python-text.png")
            matcher = OCRMatcher(any_image._get_numpy_image())
            matcher.find = MagicMock(
                side_effect=[
                    OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
                    OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
                    None,
                ]
            )

            assert matcher.find_all("Wikipedia") == [
                OCRMatch(1, 8, Region(155, 84, 24, 12), 0.90),
                OCRMatch(72, 83, Region(50, 106, 79, 12), 0.96697075),
            ]
