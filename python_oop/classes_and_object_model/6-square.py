#!/usr/bin/env python3
"""Module that defines a Square class with size, position and printing."""


class Square:
    """Represents a square."""

    def __init__(self, size=0, position=(0, 0)):
        """Initialize a new Square.

        Args:
            size: The length of one side of the square (default 0).
            position: A tuple (x, y) offset for printing (default (0, 0)).
        """
        self.size = size
        self.position = position

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

    @property
    def position(self):
        """Get the (x, y) printing offset of the square."""
        return self.__position

    @position.setter
    def position(self, value):
        """Set the (x, y) printing offset of the square.

        Raises:
            TypeError: If value is not a tuple of 2 positive integers.
        """
        if (not isinstance(value, tuple) or len(value) != 2 or
                not all(isinstance(n, int) and n >= 0 for n in value)):
            raise TypeError("position must be a tuple of 2 positive integers")
        self.__position = value

    def area(self):
        """Return the current area of the square."""
        return self.__size ** 2

    def my_print(self):
        """Print the square with #, using its position (empty line if 0)."""
        print(self)

    def __str__(self):
        """Return the square drawn with #, or an empty string if size is 0."""
        if self.__size == 0:
            return ""
        row = " " * self.__position[0] + "#" * self.__size
        return "\n" * self.__position[1] + "\n".join([row] * self.__size)
