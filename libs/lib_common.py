"""Provides basic and generic functions.
"""
import pprint
import datetime


def joinmixedtypes(data, separator):
    """Separate iterable data and allow mixed types.

    Args:
        data (iter): Iterable data
        separator (str): Separator

    Returns:
        str: Joined data by separator.
    """
    result = ""
    for item in data:
        if result == "":
            result = str(item)
        else:
            result += separator + str(item)

    return result


def prettyprint(data):
    """Pretty print dictionary or list.

    Args:
        data (dict or list): Data to be printed
    """
    pprint.pprint(data)


def converttimestamp(ts, um="ms"):
    """Convert timestamps to datetime.

    Args:
        ts (int): Unix timestamp in milliseconds (or other um)
        um (str, optional): Unit of measure (ms or s)

    Returns:
        datetime: datetime object with timestamp time
    """
    if um == "ms":
        return datetime.datetime.fromtimestamp(ts / 1000.0)  # Millisecond convert
    else:
        return datetime.datetime.fromtimestamp(ts)  # Assume seconds

# Returns a human-readable time


def prettytime(ts, um="ms"):
    """Returns a human-readable time from Unix timestamp (ms)

    Args:
        ts (int): Unit timestamp in millseconds (or other um)
        um (str, optional): Unit of measure (ms or s)

    Returns:
        str: String with formatted datetime
    """
    return converttimestamp(ts, um).strftime('%Y-%m-%d %H:%M:%S')
