import enum
from contextlib import contextmanager
from typing import Iterable, Optional, SupportsIndex, Tuple, Union

import pyautogui

from pin_the_tail.image import NeedleNotFoundError, NeedleType, Screen
from pin_the_tail.location import Point

NumberType = Union[int, float]
KeyType = Union[str, "SpecialKey"]


def is_iterable(obj, str_is_iterable=False, bytes_is_iterable=False):
    if isinstance(obj, str):
        return str_is_iterable

    if isinstance(obj, bytes):
        return bytes_is_iterable

    try:
        iter(obj)
        return True
    except TypeError:
        return False


class MouseButton(enum.Enum):
    RIGHT = "right"
    LEFT = "left"
    CENTER = "center"


class SpecialKey(enum.Enum):
    ALT = "alt"
    CAPSLOCK = "capslock"
    ESCAPE = "escape"

    def __add__(self, other) -> "KeysToPress":
        if isinstance(other, (str, SpecialKey)):
            return KeysToPress([self, other])

        if isinstance(other, list):
            other = KeysToPress(other)

        if isinstance(other, KeysToPress):
            new_value = KeysToPress([self])
            new_value.extend(other)
            return new_value

        return NotImplemented

    def __radd__(self, other) -> "KeysToPress":
        if isinstance(other, (str, SpecialKey)):
            return KeysToPress([other, self])

        if isinstance(other, list):
            other = KeysToPress(other)

        if isinstance(other, KeysToPress):
            new_value = KeysToPress(other)
            new_value.append(self)
            return new_value

        return NotImplemented

    def press_and_release(self) -> None:
        pyautogui.press(self.value)

    write = press_and_release

    def press(self) -> None:
        pyautogui.keyDown(self.value)

    def release(self) -> None:
        pyautogui.keyUp(self.value)

    @contextmanager
    def hold(self):
        self.press()
        yield
        self.release()


# Typing a subclass of list: https://stackoverflow.com/questions/54913988/python-typing-for-a-subclass-of-list
class KeysToPress(list):
    def __init__(self, items: Iterable[KeyType] = ()):
        super().__init__()
        self.extend(items)

    def _validate_value(self, item) -> KeyType:
        if isinstance(item, (str, SpecialKey)):
            return item
        raise TypeError(
            f"{self.__class__.__name__} only stores str and SpecialKey; received {item!r} (type={type(item)})"
        )

    def append(self, item: KeyType) -> None:
        super().append(self._validate_value(item))

    def extend(self, items: Iterable[KeyType]) -> None:
        if isinstance(items, self.__class__):
            super().extend(items)
        else:
            items_to_extend = [self._validate_value(item) for item in items]
            super().extend(items_to_extend)

    def __getitem__(self, item: Union[SupportsIndex, slice]) -> Union[KeyType, "KeysToPress"]:
        retval = super().__getitem__(item)
        if isinstance(item, slice):
            return self.__class__(retval)
        return retval

    def __setitem__(self, index: Union[SupportsIndex, slice], item: KeyType) -> None:
        super().__setitem__(index, self._validate_value(item))

    def insert(self, index: SupportsIndex, item: KeyType) -> None:
        super().insert(index, self._validate_value(item))

    def __add__(self, other: Iterable[KeyType]) -> "KeysToPress":
        try:
            iter(other)
        except TypeError:
            return NotImplemented
        else:
            retval = KeysToPress(self)
            retval.extend(other)
            return retval

    def __radd__(self, other) -> "KeysToPress":
        try:
            iter(other)
        except TypeError:
            return NotImplemented
        else:
            retval = KeysToPress(other)
            retval.extend(self)
            return retval

    def __iadd__(self, other: Iterable[KeyType]) -> "KeysToPress":
        try:
            iter(other)
        except TypeError:
            return NotImplemented
        else:
            self.extend(other)
            return self

    def write(self, typing_speed: NumberType = 300 / 60) -> None:
        if not isinstance(typing_speed, (int, float)):
            raise TypeError(
                f"typing_speed must be a positive number; received {typing_speed!r} (type={type(typing_speed)})"
            )

        if typing_speed <= 0:
            raise ValueError(f"typing_speed must be a number greater than zero; received {typing_speed!r}")

        interval = 1 / typing_speed

        for i, item in enumerate(self):
            if isinstance(item, str):
                pyautogui.write(item, interval=interval)
            elif isinstance(item, SpecialKey):
                pyautogui.press(item.value)
            else:
                raise TypeError(f"Unrecognized type; received {item!r} (type={type(item)})")

            if i != len(self) - 1:
                pyautogui.sleep(interval)

    def press(self) -> None:
        """
        Press and hold down the keys.  This is useful for doing key combinations.

        If any element is a string with multiple characters, then each individual character will be held down.  If a
        character appears more than once (e.g. "e" in "meet"), it will only be held down once.
        """
        unique_keys = set()  # type: set[Union[str, SpecialKey]]
        for item in self:
            if isinstance(item, str):
                unique_keys.update(item)
            elif isinstance(item, SpecialKey):
                unique_keys.add(item.value)
            else:
                raise TypeError(f"Unrecognized type; received {item!r} (type={type(item)})")

        for key in unique_keys:
            pyautogui.keyDown(key)

    def release(self) -> None:
        """
        Release the keys that have been pressed and held down.  This is useful when finishing key combinations.

        If any element is a string with multiple characters, then each individual character will be released.  If a
        character appears more than once (e.g. "e" in "meet"), it will only be released once (because it's only being
        held down once).
        """
        unique_keys = set()  # type: set[Union[str, SpecialKey]]
        for item in self:
            if isinstance(item, str):
                unique_keys.update(item)
            elif isinstance(item, SpecialKey):
                unique_keys.add(item.value)
            else:
                raise TypeError(f"Unrecognized type; received {item!r} (type={type(item)})")

        for key in unique_keys:
            pyautogui.keyUp(key)

    @contextmanager
    def hold(self):
        """
        Press and hold the keys for the duration of the context manager, releasing them at the end.  This is useful when
        finishing key combinations.

        If any element is a string with multiple characters, then each individual character will be released.  If a
        character appears more than once (e.g. "e" in "meet"), it will only be released once (because it's only being
        held down once).
        """
        self.press()
        yield
        self.release()


class Mouse:
    def __init__(self, default_move_speed: int = 244, screen_reference: Optional[Screen] = None):
        """

        Args:
            default_move_speed: pixels per second
            screen_reference:
        """
        self.default_move_speed = default_move_speed
        self.screen = screen_reference or Screen()

    @property
    def current_location(self) -> Point:
        """Return the current location of the mouse."""
        return Point.from_tuple(pyautogui.position())

    def move_to(
        self,
        location: Union[Tuple[int, int], Point, NeedleType, Iterable[NeedleType]],
        *,
        speed: Optional[int] = None,
        duration: Optional[NumberType] = None,
    ) -> None:
        """
        Move the mouse to the specified location.

        ``location`` can be a specific location on the screen or a needle to search for on the screen.

        Raises ``NeedleNotFoundError`` if the location is a needle and cannot be found on the screen.
        """
        if speed is not None and duration is not None:
            raise ValueError(
                f"No more than one of `speed` and `duration` may be `None`.  Received: {speed=}, {duration=}"
            )

        if isinstance(location, tuple):
            location = Point.from_tuple(location)
        elif not isinstance(location, Point):
            region = self.screen.find(location)
            if region is None:
                raise NeedleNotFoundError(location, self.screen)
            location = region.center

        if duration is None:
            speed = speed or self.default_move_speed
            duration = self.current_location.distance_to(location) / speed

        pyautogui.moveTo(location.x, location.y, duration)

    @staticmethod
    def button_string_to_enum(button: str) -> MouseButton:
        """
        Convert a string representation of a mouse button into a ``MouseButton`` instance.
        """
        return MouseButton[button.upper()]

    def click(self, button: Union[MouseButton, str] = MouseButton.LEFT, n_clicks: int = 1) -> None:
        """
        Click the specified mouse button ``n_clicks`` number of times.
        """
        if isinstance(button, str):
            button = self.button_string_to_enum(button)

        pyautogui.click(button=button.value, clicks=n_clicks)

    def button_press(self, button: Union[MouseButton, str]) -> None:
        if isinstance(button, str):
            button = self.button_string_to_enum(button)

        pyautogui.mouseDown(button.value)

    def button_release(self, button: Union[MouseButton, str]) -> None:
        if isinstance(button, str):
            button = self.button_string_to_enum(button)

        pyautogui.mouseUp(button.value)

    @contextmanager
    def button_hold(self, button: Union[MouseButton, str]):
        self.button_press(button)
        yield
        self.button_release(button)

    def scroll_vertical(self, amount: int) -> None:
        pyautogui.vscroll(amount)

    def scroll_horizontal(self, amount: int) -> None:
        pyautogui.hscroll(amount)


class Keyboard:
    def __init__(self, default_typing_speed: NumberType = 300 / 60):
        """
        Args:
            default_typing_speed: Number of characters per second
        """
        self.default_typing_speed = default_typing_speed

    def write(self, keys: Union[KeyType, Iterable[KeyType]], typing_speed: Optional[NumberType] = None) -> None:
        """
        Type the specified keys at a given characters per second.

        ``keys`` can be a single character, string, or ``SpecialKey``, or it can be a ``KeysToPress`` instance which is
        a list of strings and ``SpecialKey``s.

        ``typing_speed`` is the characters per second to type at.  There will be a ``1 / typing_speed`` pause between
        each character in a string and between each element in the ``KeysToPress`` list.  There is no pause at the end.
        It defaults to ``None``, meaning it will use the ``default_typing_speed`` set in the constructor.

        This is a blocking call.
        """
        if isinstance(keys, (str, SpecialKey)):
            keys = [keys]

        if not isinstance(keys, KeysToPress):
            if is_iterable(keys):
                keys = KeysToPress(keys)
            else:
                raise TypeError(f"Unsupported type for keys; received {keys!r} (type={type(keys)})")

        if typing_speed is None:
            typing_speed = self.default_typing_speed

        keys.write(typing_speed)

    def key_press(self, keys: Union[KeyType, KeysToPress]) -> None:
        """
        Press the key(s) down, but do not release it.  Useful for doing key combinations.

        If ``keys`` is a string with multiple characters, each individual character will be pressed.
        """
        if isinstance(keys, KeyType):
            keys = KeysToPress([keys])

        keys.press()

    def key_release(self, keys: Union[KeyType, KeysToPress]) -> None:
        """
        Release the key(s) specified, which should currently be pressed by the ``key_press`` method.

        If ``keys`` is a string with multiple characters, each individual character will be released.
        """
        if isinstance(keys, KeyType):
            keys = KeysToPress([keys])

        keys.release()

    @contextmanager
    def key_hold(self, keys: Union[KeyType, KeysToPress]):
        """
        Press and hold the keys for the duration of the context manager, releasing them at the end.  This is useful when
        finishing key combinations.
        """
        if isinstance(keys, KeyType):
            keys = KeysToPress([keys])

        yield from keys.hold()
