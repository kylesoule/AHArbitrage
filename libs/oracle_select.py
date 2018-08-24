"""This module provides SELECT functionality.
"""
from oracle_connect import connect, commitandclose


def countrecords(table):
    """Prints count of records in table.

    Args:
        table (string): Table name.
    """
    connection, cursor = connect()
    cursor.execute("SELECT COUNT(*) FROM {table}".format(table = table))
    for results in cursor:
        print(results)
    cursor.close()
    connection.close()


def priceinformation(item):
    """Returns price information on item.

    Args:
        item (int / string): Description

    Returns:
        list: Result of select.
    """
    connection, cursor = connect()
    cursor.execute("SELECT * FROM PROUDMOORE_A WHERE ITEM = {item}".format(item=str(item)))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


def snapshotexists(timestamp):
    """Returns true/false if timestamp snapshot exists.

    Args:
        timestamp (int / string): Unix timestamp in milliseconds.

    Returns:
        bool: True if timestamp exists otherwise False.
    """
    connection, cursor = connect()
    cursor.execute("SELECT UNIQUE TSTAMP FROM PROUDMOORE_A WHERE TSTAMP = {timestamp}".format(timestamp=str(timestamp)))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result is None:
        return False
    else:
        return True


def snapshotlist():
    """Returns list of unique snapshots timestamps.

    Returns:
        list: List of snapshot timestamps.
    """
    connection, cursor = connect()
    cursor.execute("SELECT UNIQUE TSTAMP FROM PROUDMOORE_A")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    snapshots = []

    for tstamp in results:
        snapshots.append(tstamp[0])
    return snapshots
