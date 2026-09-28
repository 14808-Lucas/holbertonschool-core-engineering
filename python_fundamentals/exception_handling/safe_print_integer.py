#!/usr/bin/env python3
"""Module that safely prints an integer."""


def safe_print_integer(value):
    """Print value with "{:d}".format() if it is an integer."""


    try:
        print("{:d}".format(value))
        return True
    except (ValueError, TypeError):
        return False
