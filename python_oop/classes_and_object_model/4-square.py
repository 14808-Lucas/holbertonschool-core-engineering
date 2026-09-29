#!/usr/bin/env python3
"""Module that defines a Square class with a validated size property."""


class Square:
    """Represents a square."""

    def __init__(self, size=0):
        """Initialize a new Square."""
        self.size = size

    @property
    def size(self):
        """Get the length of one side of the square."""
        return self.__size

    @size.setter
    def size(self, value):
        """Set the length of one side of the square.

        Raises:
            TypeError: If value is not an integer.
            ValueError: If value is less than 0.
        """
        if not isinstance(value, int):
            raise TypeError("size must be an integer")
        if value < 0:
            raise ValueError("size must be >= 0")
        self.__size = value

    def area(self):
        """Return the current area of the square."""
        return self.__size * self.__size
