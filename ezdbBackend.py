#!/usr/bin/env python

import mysql.connector
from mysql.connector import errorcode

__author__ = 'bobby'


def connectMySQL(hostname, port, dbName, username, password):
    # Call mysql.connector to attempt to open a connection
    # Return success or failure depending on results
    returnStatus = "Failure"

    try:
        dbConnection = mysql.connector.connect(host=hostname, port=port, database=dbName, user=username,
                                               password=password)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
            return returnStatus
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
            return returnStatus
        else:
            print(err)
            return returnStatus
    else:
        returnStatus = "Success"
        return returnStatus
        dbConnection.close()
