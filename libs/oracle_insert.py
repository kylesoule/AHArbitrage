"""This module provides INSERT functionality.
"""
import api_items
from oracle_connect import connect, commitandclose
from oracle_common import doall


def insertbulk(sql):
    """Efficient, bulk insert of data.

    Args:
        sql (list): List of values to be inserted.
    """
    # TODO: Count number of inputs
    connection, cursor = connect()
    cursor.prepare("INSERT INTO PROUDMOORE_A VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20)")
    cursor.executemany(None, sql)
    commitandclose(connection)


def insertsql(sql):
    """Wrapper for doall(). Executes SQL statement and closes connections.

    Args:
        sql (string): Description
    """
    doall(sql)


def insertitemclassdata():
    """Temporary function to insert item class/subclass data into Oracle.
    """
    classes = api_items.getitemclassdata()

    for c in classes:
        for s in classes[c]:
            names = classes[c][s]
            table = "ITEM_CLASSES"
            fields = "(CLASS, SUBCLASS, CLASS_NAME, SUBCLASS_NAME"
            sql = "INSERT INTO {t} {f} VALUES ({c}, {sc}, '{cn}', '{scn}')".format(t=table, f=fields, c=c, sc=s, cn=names[0], scn=names[1])
            insertsql(sql)
