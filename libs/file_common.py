"""Provides common file manipulation functions.
"""
import csv


def appendtofile(data, filename):
    """Appends data to filename

    Args:
        data (str): Data to append to filename
        filename (str): Full path of filename
    """
    with open(filename, "a") as file:
        file.write("{data}\n".format(data=data))


def writetofile(data, filename):
    """Appends data to filename

    Args:
        data (str): Data to append to filename
        filename (str): Full path of filename
    """
    with open(filename, "w") as file:
        file.write("{data}\n".format(data=data))


def readcsv(filename, delimiter=',', quotechar='"'):
    """Read CSV file data into a list.

    Args:
        filename (str): Full path of file.
        delimiter (str, optional): Delimiter
        quotechar (str, optional): Quote character

    Returns:
        list: List of lines from CSV file
    """
    data = []
    with open(filename, newline='') as csvfile:
        lines = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        for line in lines:
            data.append(line)

    return data


def getretrieveditemlist(filename, delimiter=','):
    """Returns a list of items already retrieved.

    Args:
        filename (str): Filename containing items retrieved
        delimiter (str, optional): Delimiter used in file

    Returns:
        TYPE: Description
    """
    retrieved = []
    data = readcsv(filename, delimiter=delimiter)
    for line in data:
        retrieved.append(line[0])   # Item ID

    return retrieved
