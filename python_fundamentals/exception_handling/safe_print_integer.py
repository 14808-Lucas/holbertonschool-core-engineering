#!/usr/bin/env python3
"""Module that safely prints an integer."""


def safe_print_integer(value):
    try:
        print("{:d}".format(value))
        return True
    except (ValueError, TypeError):
        return False
