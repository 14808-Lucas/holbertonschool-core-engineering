#!/usr/bin/env python3
"""Defines an abstract Animal class and its concrete subclasses."""
from abc import ABC, abstractmethod


class Animal(ABC):
    """Abstract base class that every animal must extend."""

    @abstractmethod
    def sound(self):
        """Return the sound the animal makes."""
        pass


class Dog(Animal):
    """A dog, which is a concrete Animal."""

    def sound(self):
        """Return the sound a dog makes."""
        return "Bark"


class Cat(Animal):
    """A cat, which is a concrete Animal."""

    def sound(self):
        """Return the sound a cat makes."""
        return "Meow"
