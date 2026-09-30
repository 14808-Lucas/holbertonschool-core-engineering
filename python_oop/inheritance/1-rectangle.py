#!/usr/bin/env python3
"""Define the Rectangle class, a subclass of BaseGeometry."""
BaseGeometry = __import__('base_geometry').BaseGeometry


class Rectangle(BaseGeometry):
    """A rectangle defined by a private width and height."""

    def __init__(self, width, height):
        """Initialize a Rectangle after validating its dimensions.

        Args:
            width (int): the width, a positive integer.
            height (int): the height, a positive integer.
        """
        self.integer_validator("width", width)
        self.integer_validator("height", height)
        self.__width = width
        self.__height = height
