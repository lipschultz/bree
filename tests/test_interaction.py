# pylint: disable=too-few-public-methods,too-many-public-methods

from unittest import mock
from unittest.mock import call

import pytest

from pin_the_tail import interaction


class TestSpecialKey:
    @staticmethod
    @pytest.mark.parametrize(
        "other_value",
        [
            "donkey",
            interaction.SpecialKey.ALT,
        ],
    )
    def test_special_key_plus_single_value_returns_list_of_both(other_value):
        # Act
        actual = interaction.SpecialKey.ESCAPE + other_value

        # Assert
        assert actual == interaction.KeysToPress([interaction.SpecialKey.ESCAPE, other_value])

    @staticmethod
    @pytest.mark.parametrize(
        "other_value",
        [
            ["donkey", interaction.SpecialKey.ALT],
            interaction.KeysToPress(["donkey", interaction.SpecialKey.ALT]),
        ],
    )
    def test_special_key_plus_collection_returns_list_of_both(other_value):
        # Act
        actual = interaction.SpecialKey.ESCAPE + other_value

        # Assert
        assert actual == interaction.KeysToPress([interaction.SpecialKey.ESCAPE, "donkey", interaction.SpecialKey.ALT])

    @staticmethod
    @pytest.mark.parametrize(
        "other_value",
        [
            "donkey",
            interaction.SpecialKey.ALT,
        ],
    )
    def test_single_value_plus_special_key_returns_list_of_both(other_value):
        # Act
        actual = other_value + interaction.SpecialKey.ESCAPE

        # Assert
        assert actual == interaction.KeysToPress([other_value, interaction.SpecialKey.ESCAPE])

    @staticmethod
    @pytest.mark.parametrize(
        "other_value",
        [
            ["donkey", interaction.SpecialKey.ALT],
            interaction.KeysToPress(["donkey", interaction.SpecialKey.ALT]),
        ],
    )
    def test_collection_plus_special_value_returns_list_of_both(other_value):
        # Act
        actual = other_value + interaction.SpecialKey.ESCAPE

        # Assert
        assert actual == interaction.KeysToPress(["donkey", interaction.SpecialKey.ALT, interaction.SpecialKey.ESCAPE])

    @staticmethod
    def test_press_and_release():
        # Arrange
        with mock.patch("pin_the_tail.interaction.pyautogui.press") as press_patch:
            # Act
            interaction.SpecialKey.ESCAPE.press_and_release()

            # Assert
            press_patch.assert_called_once_with("escape")

    @staticmethod
    def test_write():
        # Arrange
        with mock.patch("pin_the_tail.interaction.pyautogui.press") as press_patch:
            # Act
            interaction.SpecialKey.ESCAPE.write()  # pylint: disable=no-member

            # Assert
            press_patch.assert_called_once_with("escape")

    @staticmethod
    def test_press():
        # Arrange
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            # Act
            interaction.SpecialKey.ESCAPE.press()

            # Assert
            key_down_patch.assert_called_once_with("escape")

    @staticmethod
    def test_release():
        # Arrange
        with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
            # Act
            interaction.SpecialKey.ESCAPE.release()

            # Assert
            key_up_patch.assert_called_once_with("escape")

    @staticmethod
    def test_hold():
        # Arrange
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
                # Act
                with interaction.SpecialKey.ESCAPE.hold():
                    key_down_patch.assert_called_once_with("escape")
                    key_up_patch.assert_not_called()

                key_down_patch.assert_called_once_with("escape")
                key_up_patch.assert_called_once_with("escape")


class TestKeysToPress:
    @staticmethod
    def test_creating_empty_instance():
        # Act
        actual = interaction.KeysToPress()

        # Assert
        assert actual == []

    @staticmethod
    def test_creating_with_valid_values():
        # Act
        actual = interaction.KeysToPress(["a", "string", interaction.SpecialKey.ESCAPE, "a"])

        # Assert
        assert actual == ["a", "string", interaction.SpecialKey.ESCAPE, "a"]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_creating_with_invalid_values_raises_exception(value):
        # Act & Assert
        with pytest.raises(TypeError):
            interaction.KeysToPress([value])

    @staticmethod
    @pytest.mark.parametrize("value", ["a", "string", interaction.SpecialKey.ESCAPE])
    def test_appending_valid_value(value):
        # Arrange
        subject = interaction.KeysToPress()

        # Act
        subject.append(value)

        # Assert
        assert subject == [value]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_appending_invalid_value_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress()

        # Act & Assert
        with pytest.raises(TypeError):
            subject.append(value)

        assert subject == []

    @staticmethod
    @pytest.mark.parametrize("value", ["a", "string", interaction.SpecialKey.ESCAPE])
    def test_appending_value_already_in_list_is_allowed(value):
        # Arrange
        subject = interaction.KeysToPress(["a", "string", interaction.SpecialKey.ESCAPE])

        # Act
        subject.append(value)

        # Assert
        assert subject == ["a", "string", interaction.SpecialKey.ESCAPE, value]

    @staticmethod
    @pytest.mark.parametrize("value", ["a", "string", interaction.SpecialKey.ESCAPE])
    def test_extending_valid_values(value):
        # Arrange
        subject = interaction.KeysToPress([])

        # Act
        subject.extend([value])

        # Assert
        assert subject == [value]

    @staticmethod
    @pytest.mark.parametrize("value", ["a", "string", interaction.SpecialKey.ESCAPE])
    def test_extending_values_onto_populated_list(value):
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ALT])

        # Act
        subject.extend([value])

        # Assert
        assert subject == ["the", interaction.SpecialKey.ALT, value]

    @staticmethod
    @pytest.mark.parametrize(
        "values",
        [
            ("a", "string", interaction.SpecialKey.ESCAPE),
            ["a", "string", interaction.SpecialKey.ESCAPE],
            (value for value in ("a", "string", interaction.SpecialKey.ESCAPE)),
        ],
    )
    def test_extending_values_from_different_iterable_objects(values):
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ALT])

        # Act
        subject.extend(values)

        # Assert
        assert subject == ["the", interaction.SpecialKey.ALT, "a", "string", interaction.SpecialKey.ESCAPE]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_extending_invalid_value_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress()

        # Act & Assert
        with pytest.raises(TypeError):
            subject.extend([value])

        assert subject == []

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_extending_with_mix_of_valid_and_invalid_values_raises_exception_and_doesnt_extend_any_values(value):
        # Arrange
        subject = interaction.KeysToPress()

        # Act & Assert
        with pytest.raises(TypeError):
            subject.extend(["valid", "values"] + [value])

        assert subject == []

    @staticmethod
    @pytest.mark.parametrize("value", ["a", "string", interaction.SpecialKey.ESCAPE])
    def test_setting_valid_value(value):
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ALT])

        # Act
        subject[1] = value

        # Assert
        assert subject == ["the", value]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_setting_invalid_value_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ALT])

        # Act & Assert
        with pytest.raises(TypeError):
            subject[1] = value

        assert subject == ["the", interaction.SpecialKey.ALT]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_setting_invalid_value_using_slice_raises_exception_and_doesnt_set_any_values(value):
        # Arrange
        subject = interaction.KeysToPress(["a", "valid", "string", interaction.SpecialKey.ALT])

        # Act & Assert
        with pytest.raises(TypeError):
            subject[1:3] = [value, value]

        assert subject == ["a", "valid", "string", interaction.SpecialKey.ALT]

    @staticmethod
    def test_slicing_returns_object_of_same_type():
        # Arrange
        subject = interaction.KeysToPress(["a", "valid", "string", interaction.SpecialKey.ALT])

        # Act
        actual = subject[1:3]

        # Assert
        assert isinstance(actual, interaction.KeysToPress)
        assert actual == interaction.KeysToPress(["valid", "string"])

    @staticmethod
    @pytest.mark.parametrize("value", ["a", "string", interaction.SpecialKey.ESCAPE])
    def test_inserting_valid_value(value):
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ALT])

        # Act
        subject.insert(1, value)

        # Assert
        assert subject == ["the", value, interaction.SpecialKey.ALT]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_inserting_invalid_value_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ALT])

        # Act & Assert
        with pytest.raises(TypeError):
            subject.insert(1, value)

        assert subject == ["the", interaction.SpecialKey.ALT]

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            ("a", "string", interaction.SpecialKey.ESCAPE),
            ["a", "string", interaction.SpecialKey.ESCAPE],
            (value for value in ("a", "string", interaction.SpecialKey.ESCAPE)),
        ],
    )
    def test_adding_iterable_of_valid_value_appends_it(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act
        actual = subject + value

        # Assert
        assert actual == ["original", "a", "string", interaction.SpecialKey.ESCAPE]
        assert isinstance(actual, interaction.KeysToPress)
        assert subject == ["original"]

    @staticmethod
    def test_adding_special_key_appends_it():
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act
        actual = subject + interaction.SpecialKey.ESCAPE

        # Assert
        assert actual == ["original", interaction.SpecialKey.ESCAPE]
        assert isinstance(actual, interaction.KeysToPress)
        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize("value", [[1], [None], [[]]])
    def test_adding_invalid_values_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act & Assert
        with pytest.raises(TypeError):
            subject + value

        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_adding_iterable_of_valid_and_invalid_values_raises_exception_and_doesnt_add_any_values(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act & Assert
        with pytest.raises(TypeError):
            subject + ["valid", "values", value]

        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            ("a", "string", interaction.SpecialKey.ESCAPE),
            ["a", "string", interaction.SpecialKey.ESCAPE],
            (value for value in ("a", "string", interaction.SpecialKey.ESCAPE)),
        ],
    )
    def test_reverse_adding_iterable_of_valid_value_appends_it(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act
        actual = value + subject

        # Assert
        assert actual == ["a", "string", interaction.SpecialKey.ESCAPE, "original"]
        assert isinstance(actual, interaction.KeysToPress)
        assert subject == ["original"]

    @staticmethod
    def test_reverse_adding_special_key_appends_it():
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act
        actual = interaction.SpecialKey.ESCAPE + subject

        # Assert
        assert actual == [interaction.SpecialKey.ESCAPE, "original"]
        assert isinstance(actual, interaction.KeysToPress)
        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize("value", [[1], [None], [[]]])
    def test_reverse_adding_invalid_values_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act & Assert
        with pytest.raises(TypeError):
            value + subject

        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_reverse_adding_iterable_of_valid_and_invalid_values_raises_exception_and_doesnt_add_any_values(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act & Assert
        with pytest.raises(TypeError):
            ["valid", "values", value] + subject

        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            ("a", "string", interaction.SpecialKey.ESCAPE),
            ["a", "string", interaction.SpecialKey.ESCAPE],
            (value for value in ("a", "string", interaction.SpecialKey.ESCAPE)),
        ],
    )
    def test_inplace_adding_iterable_of_valid_value_appends_it(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act
        subject += value

        # Assert
        assert subject == ["original", "a", "string", interaction.SpecialKey.ESCAPE]

    @staticmethod
    def test_inplace_adding_special_key_appends_it():
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act
        subject += interaction.SpecialKey.ESCAPE

        # Assert
        assert subject == ["original", interaction.SpecialKey.ESCAPE]

    @staticmethod
    @pytest.mark.parametrize("value", [[1], [None], [[]]])
    def test_inplace_adding_invalid_values_raises_exception(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act & Assert
        with pytest.raises(TypeError):
            subject += value

        assert subject == ["original"]

    @staticmethod
    @pytest.mark.parametrize("value", [1, None, []])
    def test_inplace_adding_iterable_of_valid_and_invalid_values_raises_exception_and_doesnt_add_any_values(value):
        # Arrange
        subject = interaction.KeysToPress(["original"])

        # Act & Assert
        with pytest.raises(TypeError):
            subject += ["valid", "values", value]

        assert subject == ["original"]


class TestKeysToPressWriting:
    @staticmethod
    @pytest.mark.parametrize("items", [["a"], ["repeated characters"], ["a", "repeated characters", "collection"]])
    def test_writing_valid_strings(items):
        # Arrange
        subject = interaction.KeysToPress(items)

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.write") as write_patch:
            with mock.patch("pin_the_tail.interaction.pyautogui.sleep") as sleep_patch:
                subject.write()

        # Assert
        assert write_patch.call_count == len(items)
        write_patch.assert_has_calls([call(item, interval=60 / 300) for item in items])

        assert sleep_patch.call_count == len(items) - 1
        if sleep_patch.call_count > 0:
            sleep_patch.assert_has_calls([call(60 / 300) for _ in range(sleep_patch.call_count - 1)])

    @staticmethod
    @pytest.mark.parametrize(
        "items",
        [
            [interaction.SpecialKey.ESCAPE],
            [interaction.SpecialKey.ESCAPE, interaction.SpecialKey.ALT],
            [interaction.SpecialKey.ESCAPE, interaction.SpecialKey.ESCAPE, interaction.SpecialKey.ALT],
        ],
    )
    def test_writing_valid_special_keys(items):
        # Arrange
        subject = interaction.KeysToPress(items)

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.press") as press_patch:
            with mock.patch("pin_the_tail.interaction.pyautogui.sleep") as sleep_patch:
                subject.write()

        # Assert
        assert press_patch.call_count == len(items)
        press_patch.assert_has_calls([call(item.value) for item in items])

        assert sleep_patch.call_count == len(items) - 1
        if sleep_patch.call_count > 0:
            sleep_patch.assert_has_calls([call(60 / 300) for _ in range(sleep_patch.call_count - 1)])

    @staticmethod
    def test_writing_mix_of_strings_and_keys():
        # Arrange
        items = ["a", interaction.SpecialKey.ESCAPE, "repeated characters", interaction.SpecialKey.ALT]
        subject = interaction.KeysToPress(items)

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.write") as write_patch:
            with mock.patch("pin_the_tail.interaction.pyautogui.press") as press_patch:
                with mock.patch("pin_the_tail.interaction.pyautogui.sleep") as sleep_patch:
                    subject.write()

        # Assert
        assert write_patch.call_count == 2
        write_patch.assert_has_calls([call("a", interval=60 / 300), call("repeated characters", interval=60 / 300)])

        assert press_patch.call_count == 2
        press_patch.assert_has_calls([call("escape"), call("alt")])

        assert sleep_patch.call_count == 3
        sleep_patch.assert_has_calls([call(60 / 300)] * 3)

    @staticmethod
    def test_writing_uses_the_typing_speed_when_provided():
        # Arrange
        items = ["a", interaction.SpecialKey.ESCAPE, "repeated characters"]
        subject = interaction.KeysToPress(items)

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.write") as write_patch:
            with mock.patch("pin_the_tail.interaction.pyautogui.press"):
                with mock.patch("pin_the_tail.interaction.pyautogui.sleep") as sleep_patch:
                    subject.write(16)

        # Assert
        assert write_patch.call_count == 2
        write_patch.assert_has_calls([call("a", interval=1 / 16), call("repeated characters", interval=1 / 16)])

        assert sleep_patch.call_count == 2
        sleep_patch.assert_has_calls([call(1 / 16)] * 2)

    @staticmethod
    @pytest.mark.parametrize("typing_speed", [None, "16", ""])
    def test_writing_raises_type_error_when_typing_speed_isnt_number(typing_speed):
        # Arrange
        subject = interaction.KeysToPress(["a", "string"])

        # Act & Assert
        with pytest.raises(TypeError):
            subject.write(typing_speed)

    @staticmethod
    @pytest.mark.parametrize("typing_speed", [0, -1, -0.5])
    def test_writing_raises_value_error_when_typing_speed_isnt_positive_number(typing_speed):
        # Arrange
        subject = interaction.KeysToPress(["a", "string"])

        # Act & Assert
        with pytest.raises(ValueError):
            subject.write(typing_speed)

    @staticmethod
    def test_writing_empty_list_doesnt_crash_or_sleep_or_write_anything():
        # Arrange
        subject = interaction.KeysToPress([])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.write") as write_patch:
            with mock.patch("pin_the_tail.interaction.pyautogui.press") as press_patch:
                with mock.patch("pin_the_tail.interaction.pyautogui.sleep") as sleep_patch:
                    subject.write(16)

        # Assert
        write_patch.assert_not_called()
        press_patch.assert_not_called()
        sleep_patch.assert_not_called()


class TestKeysToPressPress:
    @staticmethod
    def test_pressing_empty_list_doesnt_crash_or_press_anything():
        # Arrange
        subject = interaction.KeysToPress([])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            subject.press()

        # Assert
        key_down_patch.assert_not_called()

    @staticmethod
    def test_pressing_each_character_in_string():
        # Arrange
        subject = interaction.KeysToPress(["the"])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            subject.press()

        # Assert
        assert key_down_patch.call_count == 3
        key_down_patch.assert_has_calls([call("t"), call("h"), call("e")], any_order=True)

    @staticmethod
    def test_pressing_characters_in_separate_strings():
        # Arrange
        subject = interaction.KeysToPress(["the", "car"])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            subject.press()

        # Assert
        assert key_down_patch.call_count == 6
        key_down_patch.assert_has_calls(
            [call("t"), call("h"), call("e"), call("c"), call("a"), call("r")], any_order=True
        )

    @staticmethod
    @pytest.mark.parametrize(
        "keys", [[interaction.SpecialKey.ESCAPE], [interaction.SpecialKey.ESCAPE, interaction.SpecialKey.ALT]]
    )
    def test_pressing_special_keys(keys):
        # Arrange
        subject = interaction.KeysToPress(keys)

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            subject.press()

        # Assert
        assert key_down_patch.call_count == len(keys)
        key_down_patch.assert_has_calls([call(key.value) for key in keys], any_order=True)

    @staticmethod
    def test_duplicate_keys_are_only_pressed_once():
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ESCAPE, "cat", interaction.SpecialKey.ESCAPE])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyDown") as key_down_patch:
            subject.press()

        # Assert
        assert key_down_patch.call_count == 6
        key_down_patch.assert_has_calls(
            [call("t"), call("h"), call("e"), call("c"), call("a"), call(interaction.SpecialKey.ESCAPE.value)],
            any_order=True,
        )


class TestKeysToPressRelease:
    @staticmethod
    def test_releasing_without_first_pressing_doesnt_crash():
        # Arrange
        subject = interaction.KeysToPress(["a", interaction.SpecialKey.ESCAPE])

        # Act
        subject.release()

        # No exception raised is a success

    @staticmethod
    def test_releasing_empty_list_doesnt_crash_or_release_anything():
        # Arrange
        subject = interaction.KeysToPress([])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
            subject.release()

        # Assert
        key_up_patch.assert_not_called()

    @staticmethod
    def test_releasing_each_character_in_string():
        # Arrange
        subject = interaction.KeysToPress(["the"])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
            subject.release()

        # Assert
        assert key_up_patch.call_count == 3
        key_up_patch.assert_has_calls([call("t"), call("h"), call("e")], any_order=True)

    @staticmethod
    def test_releasing_characters_in_separate_strings():
        # Arrange
        subject = interaction.KeysToPress(["the", "car"])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
            subject.release()

        # Assert
        assert key_up_patch.call_count == 6
        key_up_patch.assert_has_calls(
            [call("t"), call("h"), call("e"), call("c"), call("a"), call("r")], any_order=True
        )

    @staticmethod
    @pytest.mark.parametrize(
        "keys", [[interaction.SpecialKey.ESCAPE], [interaction.SpecialKey.ESCAPE, interaction.SpecialKey.ALT]]
    )
    def test_releasing_special_keys(keys):
        # Arrange
        subject = interaction.KeysToPress(keys)

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
            subject.release()

        # Assert
        assert key_up_patch.call_count == len(keys)
        key_up_patch.assert_has_calls([call(key.value) for key in keys], any_order=True)

    @staticmethod
    def test_duplicate_keys_are_only_released_once():
        # Arrange
        subject = interaction.KeysToPress(["the", interaction.SpecialKey.ESCAPE, "cat", interaction.SpecialKey.ESCAPE])

        # Act
        with mock.patch("pin_the_tail.interaction.pyautogui.keyUp") as key_up_patch:
            subject.release()

        # Assert
        assert key_up_patch.call_count == 6
        key_up_patch.assert_has_calls(
            [call("t"), call("h"), call("e"), call("c"), call("a"), call(interaction.SpecialKey.ESCAPE.value)],
            any_order=True,
        )


class TestKeysToPressHold:
    @staticmethod
    def test_hold_calls_press_then_release():
        # Arrange
        subject = interaction.KeysToPress(["any", "text"])
        subject.press = mock.MagicMock()
        subject.release = mock.MagicMock()

        # Act & Assert
        with subject.hold():
            subject.press.assert_called_once_with()
            subject.release.assert_not_called()

        subject.press.assert_called_once_with()
        subject.release.assert_called_once_with()
