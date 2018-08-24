"""This module provides DELETE functionality.
"""
from oracle_connect import connect, commitandclose
from oracle_common import doall


def removeall(table):
    """Delete everything in table.

    Args:
        table (string): Table name.
    """
    doall("DELETE FROM {table}".format(table=table))
