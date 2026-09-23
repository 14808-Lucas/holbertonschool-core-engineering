#!/usr/bin/env python3
"""Module that prints a matrix of integers."""


def print_matrix_integer(matrix=[[]]):
    for row in matrix:
        line = ""
        for i in range(len(row)):
            if i > 0:
                line = "{}{}".format(line, " ")
            line = "{}{:d}".format(line, row[i])
        print(line)
