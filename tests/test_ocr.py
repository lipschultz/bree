from pathlib import Path

from bree.image import Image, Region
from bree.ocr import OCRMatcher, OCRMatch

RESOURCES_DIR = Path(__file__).parent / 'resources'


class TestFind:
    @staticmethod
    def test_finding_complete_single_word():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find('the') == OCRMatch(50, 53, Region(155, 84, 24, 12), 94.887207)

    @staticmethod
    def test_finding_partial_single_word_finds_entire_words_bounding_box():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find('he') == OCRMatch(50, 53, Region(155, 84, 24, 12), 94.887207)

    @staticmethod
    def test_finding_complete_single_word_with_preceding_space():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find(' the') == OCRMatch(49, 53, Region(148, 84, 31, 15), 94.887207)

    @staticmethod
    def test_finding_complete_single_word_with_space_before_and_after():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find(' the ') == OCRMatch(49, 54, Region(148, 84, 37, 15), 94.887207)

    @staticmethod
    def test_finding_two_words():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find('Wikipedia, the') == OCRMatch(39, 53, Region(69, 84, 110, 15), 94.515457)

    @staticmethod
    def test_finding_complete_single_word_on_second_line():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find('(Redirected') == OCRMatch(72, 83, Region(50, 106, 79, 12), 96.697075)

    @staticmethod
    def test_finding_two_words_on_separate_lines():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        matcher = OCRMatcher(any_image._get_numpy_image())

        assert matcher.find('encyclopedia\n(Redirected') == OCRMatch(59, 83, Region(50, 84, 271, 34), 96.515205)
