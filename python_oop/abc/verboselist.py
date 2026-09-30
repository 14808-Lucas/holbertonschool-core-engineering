#!/usr/bin/env python3
"""Defines VerboseList, a list that announces changes to its contents."""


class VerboseList(list):
    """A list that prints a message when items are added or removed."""

    def append(self, item):
        """Add an item to the end of the list, then announce it."""
        super().append(item)
        print("Added [{}] to the list.".format(item))

    def extend(self, iterable):
        """Add every item from an iterable, then announce how many."""
        items = list(iterable)
        super().extend(items)
        print("Extended the list with [{}] items.".format(len(items)))

    def remove(self, item):
        """Announce the removal of an item, then remove it."""
        if item in self:
            print("Removed [{}] from the list.".format(item))
        super().remove(item)

    def pop(self, index=-1):
        """Announce the item at index, then pop and return it."""
        item = self[index]
        print("Popped [{}] from the list.".format(item))
        return super().pop(index)
