#!/usr/bin/env python3
"""Module that prints a string converted to uppercase."""


def uppercase(str):
    result = ""
    for c in str:
        if ord('a') <= ord(c) <= ord('z'):
            result = "{}{}".format(result, chr(ord(c) - 32))
        else:
            result = "{}{}".format(result, c)
    print(result)
