"""This module establishes and closes Oracle database connections.
"""
import cx_Oracle
import api_key


def connect():
    """Establish connection to Oracle database

    Returns:
        (connection, cursor): Tuple of connection and cursor.
    """
    # connection = cx_Oracle.connect(api_key.USERNAME, api_key.PASSWORD, cx_Oracle.makedsn(api_key.IPADDRESS, api_key.PORTNUMBER, api_key.DSN))
    connection = cx_Oracle.connect(api_key.USERNAME, api_key.PASSWORD, "ORCL")
    cursor = connection.cursor()
    return (connection, cursor)


def commitandclose(con, cur=None):
    """Commit changes and close connection and cursor.

    Args:
        con (connection): Oracle connection object
        cur (cursor): Oracle cursor object
    """
    con.commit()
    if cur is not None:
        cur.close()
    con.close()
