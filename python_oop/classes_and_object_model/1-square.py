#!/usr/bin/env python3
"""Module that defines a Square class with a private size attribute."""


class Square:
    """Represents a square."""

    def __init__(self, size):
        """Initialize a a new Square.

        Args:
        size: The length of one side of the square."""
        self.__size = size
