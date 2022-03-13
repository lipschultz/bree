from pathlib import Path

import pytest

from bree.image import Image, Region, OutOfBoundsError

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
        assert all(score >= 0.99 for _, score in found)
        actual = {image.region for image, _ in found}
        assert expected == actual

    @staticmethod
    def test_finding_best_match_image():
        any_image = Image(RESOURCES_DIR / 'wiki-python-text.png')
        needle = Image(RESOURCES_DIR / 'the.png')

        found = any_image.find_image(needle)

        assert found.parent_image == any_image
        assert found.region == Region(x=1046, y=142, width=30, height=19)


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
