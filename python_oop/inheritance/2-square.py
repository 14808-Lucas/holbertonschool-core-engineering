#!/usr/bin/env python3
"""Define the Square class with its own string representation."""
Rectangle = __import__('2-rectangle').Rectangle


class Square(Rectangle):
    """A square, a rectangle whose width and height are equal."""

    def __init__(self, size):
        """Initialize a Square after validating its size.

        Args:
            size (int): the side length, a positive integer.
        """
        self.integer_validator("size", size)
        self.__size = size
        super().__init__(size, size)

    def area(self):
        """Return the area of the square."""
        return self.__size * self.__size

    def __str__(self):
        """Return the description [Square] <width>/<height>."""
        return "[Square] {}/{}".format(self.__size, self.__size)
