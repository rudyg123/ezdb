#!/usr/bin/env python
# encoding: utf-8

'''
CS419 mysql_db.py file
Group 15: Rudy Gonzalez, Bobby Hines
'''

import mysql.connector
from mysql.connector import errorcode
import urllib2

class MySQL_Database(object):

    '''initializes database class variables and connect to root dbms'''
    #def __init__(self, dbtype='MySQL', host='localhost', port='', user='root', password='password', activedb=False):
    def __init__(self):
        self.dbtype = None
        self.host = None
        self.port = None
        self.user = None
        self.password = None

        self.dbname = None

    def connect_DBMS(self, dbtype, host, port, user, password):
        
        self.dbtype = dbtype
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.dbname = ''

        self.cur = ''
        self.conn = ''

        self.conn_config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
            'database': ''
        }
        
        try:
            self.conn = mysql.connector.connect(**self.conn_config)
            self.cur = self.conn.cursor(buffered=True)

        except mysql.connector.Error, err:
            return err


    '''connect to existing named database
    -still need to implement user db authentication'''
    def connect_database(self, dbname):

        self.dbname = dbname

        self.conn_config['database'] = self.dbname
        try:
            self.conn = mysql.connector.connect(**self.conn_config)
            self.cur = self.conn.cursor(buffered=True)

        except mysql.connector.Error, err:
            return err

    def list_databases(self):

        #sql command to only show user created databases exlusive of system databases
        sql_string = "SELECT schema_name FROM INFORMATION_SCHEMA.SCHEMATA WHERE schema_name not in" \
                     "('information_schema','mysql','performance_schema');"
        try:
            self.cur.execute(sql_string)

            dblist_data = self.cur.fetchall()
            dblist = []

            for row in dblist_data:
                dblist.append(row[0])

            return dblist

        except mysql.connector.Error, err:
            return err

    def create_database(self, dbname):

        self.dbname = dbname

        try:

            sql_string = "CREATE DATABASE {}".format(self.dbname)
            self.cur.execute(sql_string)
            return "{} MySQL database created.".format(self.dbname)

        except mysql.connector.Error, err:
            return "The following problem occurred during creation:\n" + str(err)


    def delete_database(self, dbname):

        self.dbname = dbname

        if self.conn:
            self.conn.close() #close db connection

        #connect to dbms as root
        self.conn_config.clear()
        self.conn_config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
        }

        try:
            self.conn = mysql.connector.connect(**self.conn_config)
            self.cur = self.conn.cursor()

            sql_string = "DROP DATABASE {}".format(self.dbname)
            self.cur.execute(sql_string)
            return "{} MySQL database deleted.".format(self.dbname)

        except mysql.connector.Error, err:
            return "The following problem occurred during deletion:\n" + str(err)

    def list_database_tables(self):

        sql_string = "SHOW TABLES;"
        try:
            self.cur.execute(sql_string)
            tablelist_data = self.cur.fetchall()

            tablelist = []

            for row in tablelist_data:
                tablelist.append(row[0])

            return tablelist

        except mysql.connector.Error, err:
            return err

    def browse_table(self, table):

        sql_string = "SELECT * from {}".format(table) + ";"

        try:
            self.cur.execute(sql_string)
            try:
                browse_results_data = self.cur.fetchall()
                browse_results = []

                for row in browse_results_data:
                    browse_results.append(row)
                return "success", browse_results
            except mysql.connector.Error, err:
                return "error", err

        except mysql.connector.Error, err:
            return "error", err

    def view_table_struct(self, table):

        sql_string = "DESCRIBE {};".format(table)

        try:
            self.cur.execute(sql_string)
            try:
                struct_results_data = self.cur.fetchall()
                struct_results = []

                for row in struct_results_data:
                    struct_results.append(row)
                return "success", struct_results

            except mysql.connector.Error, err:
                return "error", err

        except mysql.connector.Error, err:
            return "error", err

    def delete_table(self, table):

        sql_string = "DROP TABLE {};".format(table)

        try:
            self.cur.execute(sql_string)
        except mysql.connector.Error, err:
            return err

    def create_table(self, sql):

        sql_string = sql

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            return "success", " "

        except mysql.connector.Error, err:
            return "error", err

    def execute_SQL(self, sql):

        sql_string = sql + ";"

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            sql_results = []

            try:
                sql_results_data = self.cur.fetchall()

                if sql_results_data:
                    for row in sql_results_data:
                        sql_results.append(row)
                    return "success", sql_results

                else:
                    sql_results.append("No results to display")
                    return "success", sql_results

            except mysql.connector.Error, err:
                if str(err) == "No result set to fetch from.":
                    sql_results.append("Operation completed successfully")
                    return "success", sql_results
                else:
                    return "error", err

        except mysql.connector.Error, err:
            return "error", err

