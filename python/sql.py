import sqlite3
import pandas as pd
import peewee as pw


DEFAULT_DB = "../data/sqlite/BridleCrew"

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def dataframe_from_query(query, db=DEFAULT_DB):
    conn = create_connection(db)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df