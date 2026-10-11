#!/usr/bin/env python3
"""Module that defines a fuction to read a text file."""


def read_file(filename=""):
    with open(filename, encoding="utf-8") as f:
        print(f.read(), end="")
