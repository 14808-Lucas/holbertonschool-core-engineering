#!/usr/bin/env python3
"""Program that imports add  and prints a formatted sum."""
from add_0 import add


if __name__ == "__main__":
    a = 1
    b = 2
    print("{} + {} = {}".format(a, b, add(a, b)))
