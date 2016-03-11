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

    def connect_DBMS(self, dbtype, host, port, dbname, user, password):
        
        self.dbtype = dbtype
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

        self.cur = ''
        self.conn = ''

        self.conn_config = {
            'host': self.host,
            'port': self.port,
            'database': self.dbname,
            'user': self.user,
            'password': self.password,
        }
        
        try:
            self.conn = mysql.connector.connect(**self.conn_config)
            self.conn.commit()
            self.cur = self.conn.cursor(buffered=True)

        except mysql.connector.Error, err:
            return err


    '''connect to existing named database'''

    def connect_database(self, dbname):

        self.dbname = dbname

        self.conn_config['database'] = self.dbname
        try:
            self.conn = mysql.connector.connect(**self.conn_config)

            self.cur = self.conn.cursor(buffered=True)

        except mysql.connector.Error, err:
            return err

    def list_databases(self):

        # sql command to only show user created databases exlusive of system databases
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
            self.conn.commit()

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
            self.conn.commit()

            return "{} MySQL database deleted.".format(self.dbname)

        except mysql.connector.Error, err:
            self.conn.rollback()
            return "The following problem occurred during deletion:\n" + str(err)

    def list_database_tables(self):

        sql_string = "SHOW TABLES;"
        try:

            self.cur.execute(sql_string)
            self.conn.commit()
            tablelist_data = self.cur.fetchall()

            tablelist = []

            for row in tablelist_data:
                tablelist.append(row[0])

            return tablelist

        except mysql.connector.Error, err:
            return err

    def browse_table(self, table):

        sql_string = "SELECT * from {}".format(table)

        try:
            self.cur.execute(sql_string + " LIMIT 0;")
            self.conn.commit()
            col_titles = [desc[0] for desc in self.cur.description]

            self.cur.execute(sql_string + ";")
            self.conn.commit()

            try:
                browse_results_data = self.cur.fetchall()
                browse_results = []
                row_count = 0

                for row in browse_results_data:
                    browse_results.append(row)
                    row_count += 1
                return "success", browse_results, col_titles, row_count

            except mysql.connector.Error, err:
                return "error", err, "", ""

        except mysql.connector.Error, err:
            return "error", err, "", ""

    def view_table_struct(self, table):

        sql_string = "SELECT column_name, data_type, character_maximum_length, collation_name, is_nullable," \
                     " extra, column_default from INFORMATION_SCHEMA.COLUMNS where table_name ='{}'".format(table)

        try:

            self.cur.execute(sql_string + " LIMIT 0;")
            self.conn.commit()
            col_titles = [desc[0] for desc in self.cur.description]

            self.cur.execute(sql_string + ";")
            self.conn.commit()

            try:
                table_struct_results_data = self.cur.fetchall()
                table_struct_results = []
                row_count = 0

                for row in table_struct_results_data:
                    table_struct_results.append(row)
                    row_count += 1

                return "success", table_struct_results, col_titles, row_count

            except mysql.connector.Error, err:
                return "error", err, "", ""

        except mysql.connector.Error, err:
            return "error", err, "", ""

    def delete_table(self, table):

        sql_string = "DROP TABLE {};".format(table)

        try:
            self.cur.execute(sql_string)
            self.conn.commit()

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

        sql_string = sql
        col_titles = []
        row_count = 0

        try:
            if "select" in sql_string.lower() and "outfile" not in sql_string.lower() and "grant" \
                    not in sql_string.lower():

                self.cur.execute(sql_string + " LIMIT 0;")
                self.conn.commit()
                col_titles = [desc[0] for desc in self.cur.description]

            self.cur.execute(sql_string + ";")
            self.conn.commit()

            sql_results = []

            try:

                sql_results_data = self.cur.fetchall()

                if sql_results_data:
                    row_count = 0
                    for row in sql_results_data:
                        sql_results.append(row)
                        row_count += 1

                    return "success", sql_results, col_titles, row_count

                else:
                    return "success", sql_results, col_titles, row_count

            except mysql.connector.Error, err:

                if str(err) == "No result set to fetch from.":
                    return "success", sql_results, col_titles, row_count
                else:
                    return "error", err, "", ""

        except mysql.connector.Error, err:
            return "error", err

    def get_table_fields(self, table):

        sql_string = "SELECT column_name from INFORMATION_SCHEMA.COLUMNS where table_name ='{}'".format(table)

        try:

            self.cur.execute(sql_string + ";")
            self.conn.commit()

            try:
                table_fields_results_data = self.cur.fetchall()
                table_fields_results = []

                for row in table_fields_results_data:
                    table_fields_results.append(row)

                return "success", table_fields_results

            except mysql.connector.Error, err:

                self.conn.rollback()
                return "error", err

        except mysql.connector.Error, err:

            self.conn.rollback()
            return "error", err

    def get_userlist(self, table):

        sql_string = "SELECT user from mysql.user WHERE user != 'root' AND user != 'debian-sys-maint'"

        try:

            self.cur.execute(sql_string + ";")
            self.conn.commit()

            try:
                user_results_data = self.cur.fetchall()
                user_results = []

                for row in user_results_data:
                    user_results.append(row)

                return "success", user_results

            except mysql.connector.Error, err:

                self.conn.rollback()
                return "error", err

        except mysql.connector.Error, err:

            self.conn.rollback()
            return "error", err