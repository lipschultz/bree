from pathlib import Path

import pytest

from bree.image import Image, Region, OutOfBoundsError

RESOURCES_DIR = Path(__file__).parent / 'resources'


class TestImage:
    @staticmethod
    def test_height():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')

        assert any_image.height == 913

    @staticmethod
    def test_width():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')

        assert any_image.width == 1920

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
    def test_finding_all_instances_of_an_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')

        found = list(any_image.find_image_all(needle))

        expected = {
            Region(x=1260, y=240, width=31, height=17): 1.0,
            Region(x=641, y=391, width=31, height=17): 0.9904767,
            Region(x=918, y=391, width=31, height=17): 0.9926504,
            Region(x=543, y=507, width=31, height=17): 0.99047655,
        }

        assert len(found) == len(expected)
        for child_image, score in found:
            assert child_image.parent_image == any_image
            assert child_image.region in expected
            assert score == pytest.approx(expected[child_image.region])

    @staticmethod
    def test_finding_best_match_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')

        found = any_image.find_image(needle)

        assert found.parent_image == any_image
        assert found.region == Region(x=1260, y=240, width=31, height=17)


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
    def test_getting_child_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        child_region = Region(10, 30, 100, 400)
        child_image = any_image.get_child_region(child_region)

        grandchild_region = Region(3, 5, 20, 100)
        grandchild_image = child_image.get_child_region(grandchild_region)

        expected_child_image = any_image._get_numpy_image()[35:100+35, 13:20+13, :]
        actual_child_image = grandchild_image._get_numpy_image()

        assert (expected_child_image == actual_child_image).all()
