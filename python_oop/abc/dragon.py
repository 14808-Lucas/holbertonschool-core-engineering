#!/usr/bin/env python3
"""Demonstrates mixins by giving a Dragon swimming and flying abilities."""


class SwimMixin:
    """Mixin that adds swimming behavior to a class."""

    def swim(self):
        """Print that the creature swims."""
        print("The creature swims!")


class FlyMixin:
    """Mixin that adds flying behavior to a class."""

    def fly(self):
        """Print that the creature flies."""
        print("The creature flies!")


class Dragon(SwimMixin, FlyMixin):
    """A dragon that can swim, fly and roar."""

    def roar(self):
        """Print that the dragon roars."""
        print("The dragon roars!")
