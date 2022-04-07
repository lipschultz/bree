from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, call

import pytest

from bree.image import Image, OutOfBoundsError, MatchedRegionInImage, Screen, RegionInImage
from bree.location import Region

RESOURCES_DIR = Path(__file__).parent / 'resources'


class TestImage:
    @staticmethod
    def test_height():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')

        assert any_image.height == 817

    @staticmethod
    def test_width():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')

        assert any_image.width == 1313

    @staticmethod
    def test_getting_child_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 100, 400)

        child_image = any_image.get_child_region(region)

        expected_child_image = any_image._get_numpy_image()[30:430, 10:110, :]
        actual_child_image = child_image._get_numpy_image()

        assert (expected_child_image == actual_child_image).all()

    @staticmethod
    def test_getting_child_image_where_left_is_negative_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(-1, 30, 100, 400)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_child_image_where_top_is_negative_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, -1, 100, 400)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_child_image_where_right_exceeds_bounds_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 10_000, 400)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_child_image_where_bottom_exceeds_bounds_raises_out_of_bounds_error():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 100, 40_000)

        with pytest.raises(OutOfBoundsError):
            any_image.get_child_region(region)

    @staticmethod
    def test_getting_text():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        mock_ocr_matcher = MagicMock()
        mock_ocr_matcher.text = 'any value'
        any_image._get_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        actual = any_image.get_text()

        any_image._get_ocr_matcher.assert_called_once()
        assert actual == 'any value'

    @staticmethod
    def test_getting_ocr_matcher_for_same_language_only_creates_it_once():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        mock_ocr_matcher = MagicMock()
        any_image._create_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        any_image._get_ocr_matcher('eng', '\n', '\n\n')
        any_image._get_ocr_matcher('eng', '\n', '\n\n')

        any_image._create_ocr_matcher.assert_called_once()

    @staticmethod
    def test_getting_ocr_matcher_for_different_language_creates_different_matchers():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        mock_ocr_matcher = MagicMock()
        any_image._create_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        any_image._get_ocr_matcher('eng', '\n', '\n\n')
        any_image._get_ocr_matcher('asd', '\n', '\n\n')

        assert any_image._create_ocr_matcher.call_count == 2
        any_image._create_ocr_matcher.assert_has_calls([
            call('eng', '\n', '\n\n'),
            call('asd', '\n', '\n\n'),
        ])

    @staticmethod
    def test_finding_all_instances_of_an_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')

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
    def test_finding_best_match_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')

        found = any_image.find_image(needle)

        assert found.parent_image == any_image
        assert found.region == Region(x=1046, y=142, width=30, height=19)

    @staticmethod
    def test_wait_until_image_appears_returns_empty_list_when_needle_not_found_in_image():
        any_image = Image(RESOURCES_DIR / 'the.png')
        needle = Image(RESOURCES_DIR / 'wiki-python-text.png')
        any_image.find_image_all = MagicMock(return_value=[])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            found = any_image.wait_until_image_appears(needle, 0.8, 10, match_method='ANY-METHOD', scans_per_second=20)

            assert found == []
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ] * 200)
            assert any_image.find_image_all.call_count == 200
            sleep_patch.assert_has_calls([
                call(1/20)
            ] * 200)
            assert sleep_patch.call_count == 200

    @staticmethod
    def test_wait_until_image_appears_returns_found_region_when_needle_found_in_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            found = any_image.wait_until_image_appears(needle, 0.8, 10, match_method='ANY-METHOD', scans_per_second=20)

            assert found == [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)]
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ])
            assert any_image.find_image_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_image_appears_returns_found_region_when_needle_found_in_image_eventually():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(side_effect=[
            [],
            [],
            [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)],
        ])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            found = any_image.wait_until_image_appears(needle, 0.8, 10, match_method='ANY-METHOD', scans_per_second=20)

            assert found == [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)]
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ] * 3)
            assert any_image.find_image_all.call_count == 3
            assert sleep_patch.call_count == 2

    @staticmethod
    def test_wait_until_image_appears_scans_once_when_timeout_is_zero():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            found = any_image.wait_until_image_appears(needle, 0.8, 0, match_method='ANY-METHOD', scans_per_second=20)

            assert found == [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)]
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ])
            assert any_image.find_image_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_image_appears_scans_once_when_scans_per_second_is_zero():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            found = any_image.wait_until_image_appears(needle, 0.8, 10, match_method='ANY-METHOD', scans_per_second=0)

            assert found == [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)]
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ])
            assert any_image.find_image_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_image_vanishes_returns_true_when_needle_not_found_in_image():
        any_image = Image(RESOURCES_DIR / 'the.png')
        needle = Image(RESOURCES_DIR / 'wiki-python-text.png')
        any_image.find_image_all = MagicMock(return_value=[])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_image_vanishes(
                needle,
                0.8,
                10,
                match_method='ANY-METHOD',
                scans_per_second=20
            )

            assert vanished is True
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ])
            assert any_image.find_image_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_image_vanishes_returns_false_when_needle_found_in_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_image_vanishes(
                needle,
                0.8,
                10,
                match_method='ANY-METHOD',
                scans_per_second=20
            )

            assert vanished is False
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ] * 200)
            assert any_image.find_image_all.call_count == 200
            sleep_patch.assert_has_calls([
                call(1/20)
            ] * 200)
            assert sleep_patch.call_count == 200

    @staticmethod
    def test_wait_until_image_vanishes_returns_true_when_needle_eventually_leaves_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(side_effect=[
            [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)],
            [MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)],
            [],
        ])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_image_vanishes(
                needle,
                0.8,
                10,
                match_method='ANY-METHOD',
                scans_per_second=20
            )

            assert vanished is True
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ] * 3)
            assert any_image.find_image_all.call_count == 3
            sleep_patch.assert_has_calls([
                call(1/20)
            ] * 2)
            assert sleep_patch.call_count == 2

    @staticmethod
    def test_wait_until_image_vanishes_scans_once_when_timeout_is_zero():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(return_value=[])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_image_vanishes(
                needle,
                0.8,
                10,
                match_method='ANY-METHOD',
                scans_per_second=20
            )

            assert vanished is True
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ])
            assert any_image.find_image_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_wait_until_image_vanishes_scans_once_when_scans_per_second_is_zero():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.find_image_all = MagicMock(return_value=[])

        with mock.patch('bree.image.pyautogui.sleep', return_value=None, new_callable=MagicMock) as sleep_patch:
            vanished = any_image.wait_until_image_vanishes(
                needle,
                0.8,
                10,
                match_method='ANY-METHOD',
                scans_per_second=20
            )

            assert vanished is True
            any_image.find_image_all.assert_has_calls([
                call(needle, 0.8, match_method='ANY-METHOD')
            ])
            assert any_image.find_image_all.call_count == 1
            sleep_patch.assert_not_called()

    @staticmethod
    def test_contains_image_returns_false_when_needle_not_found_in_image():
        any_image = Image(RESOURCES_DIR / 'the.png')
        needle = Image(RESOURCES_DIR / 'wiki-python-text.png')
        any_image.wait_until_image_appears = MagicMock(return_value=[])

        found = any_image.contains_image(needle, 0.8, 10, scans_per_second=99)

        assert found is False
        any_image.wait_until_image_appears.assert_called_once_with(needle, 0.8, 10, scans_per_second=99)

    @staticmethod
    def test_contains_image_returns_true_when_needle_found_in_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.wait_until_image_appears = MagicMock(
            return_value=[MatchedRegionInImage(any_image, Region(0, 0, 1, 1), 1.0)]
        )

        found = any_image.contains_image(needle, 0.8, 10, scans_per_second=99)

        assert found is True
        any_image.wait_until_image_appears.assert_called_once_with(needle, 0.8, 10, scans_per_second=99)

    @staticmethod
    def test_in_returns_false_when_needle_image_not_found_in_image():
        any_image = Image(RESOURCES_DIR / 'the.png')
        needle = Image(RESOURCES_DIR / 'wiki-python-text.png')
        any_image.contains_image = MagicMock(return_value=False)

        found = needle in any_image

        assert found is False
        any_image.contains_image.assert_called_once_with(needle, timeout=0)

    @staticmethod
    def test_in_returns_true_when_needle_image_found_in_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')
        any_image.contains_image = MagicMock(return_value=True)

        found = needle in any_image

        assert found is True
        any_image.contains_image.assert_called_once_with(needle, timeout=0)


class TestChildImage:
    @staticmethod
    def test_height():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.height == 400

    @staticmethod
    def test_width():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.width == 100

    @staticmethod
    def test_getting_region_for_child():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.region == region

    @staticmethod
    def test_getting_absolute_region_for_child():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(region)

        assert child_image.absolute_region == region

    @staticmethod
    def test_getting_grandchild_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        expected_child_image = any_image._get_numpy_image()[35:100+35, 13:20+13, :]
        actual_child_image = grandchild_image._get_numpy_image()

        assert (expected_child_image == actual_child_image).all()

    @staticmethod
    def test_getting_region_for_grandchild():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        assert grandchild_image.region == grandchild_region

    @staticmethod
    def test_getting_absolute_region_for_grandchild():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_left(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_left_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_above(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_above_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_right(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_right_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_below(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_raw_region_below_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_left(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_left_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_above(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_above_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_right(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_right_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_below(size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
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
        ]
    )
    def test_getting_region_below_for_grandchild(self, size, absolute, expected_region):
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)
        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        actual_region = grandchild_image.region_below(size, absolute)

        assert actual_region == RegionInImage(any_image if absolute else child_image, expected_region)


class TestScreen:

    @staticmethod
    def test_getting_ocr_matcher_for_same_language_creates_it_each_time():
        any_image = Screen()
        mock_ocr_matcher = MagicMock()
        any_image._create_ocr_matcher = MagicMock(return_value=mock_ocr_matcher)

        any_image._get_ocr_matcher('eng', '\n', '\n\n')
        any_image._get_ocr_matcher('eng', '\n', '\n\n')

        assert any_image._create_ocr_matcher.call_count == 2
        any_image._create_ocr_matcher.assert_has_calls([
            call('eng', '\n', '\n\n'),
            call('eng', '\n', '\n\n'),
        ])
