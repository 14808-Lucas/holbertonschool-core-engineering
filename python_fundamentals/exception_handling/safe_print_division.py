#!/usr/bin/env python3
"""Module that safely divides two integers."""


def safe_print_division(a, b):
    resuly = None
    try:
        result = a / b
    except (ZeroDivisionError, TypeError):
        result = None
    finally:
        print("Inside result: {}".format(result))
    return result
