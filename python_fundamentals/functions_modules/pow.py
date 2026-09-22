#!/usr/bin/env python3
""" module that computes a raised to the power of b manually."""


def pow(a, b):
    result = 1
    for i in range(b):
        result = result * a
    return result
