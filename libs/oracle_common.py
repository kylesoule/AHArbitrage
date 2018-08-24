"""This module provides common functionality.
"""
from oracle_connect import connect, commitandclose


def doall(sql):
    """Executes SQL statement and closes connection.

    Args:
        sql (TYPE): Description
    """
    connection, cursor = connect()
    cursor.execute(sql)
    commitandclose(connection, cursor)


def executesql(sql):
    """Executes SQL statement then returns connection and cursor.

    Args:
        sql (sql): SQL query.

    Returns:
        (connection, cursor): Connection and cursor objects.
    """
    connection, cursor = connect()
    cursor.execute(sql)
    return (connection, cursor)
