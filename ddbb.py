import os
import sys
import pandas as pd
import mysql.connector


# Load environment variables
DDBB_USER = os.getenv("USERDB")
DDBB_PASS = os.getenv("PASSDB")
DDBB_NAME = os.getenv("NAMEDB")
DDBB_HOST = os.getenv("BACKEND")
DDBB_HOST_2 = os.getenv("BACKEND")

def ddbb_connect():
    try:
        db = mysql.connector.connect(
            user=DDBB_USER,
            password=DDBB_PASS,
            host=DDBB_HOST,
            db=DDBB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Something went wrong: {err}")
        raise IOError(str(err))

    if db.is_connected():
        print(f"Connected to {DDBB_NAME} database")
        return db

def execute_query(query):
    db = ddbb_connect()
    cursor = db.cursor()
    cursor.execute(query)

    df = pd.DataFrame(cursor.fetchall(),
                      columns=cursor.column_names)

    cursor.close()
    db.close()
    return df


def get_run_work_desc(source, product, runs, contact = 400):
    runs_list_str = ",".join([str(run) for run in runs])

    query = f"""SELECT run_id, wrk_id, run_desc
    FROM mshop_runs, mshop_works
    WHERE run_id = wrk_run
    AND run_contact = {contact}
    AND run_type = '{product}'
    AND run_source = '{source}'
    AND run_id IN ({runs_list_str})"""

    df = execute_query(query = query)
    return df