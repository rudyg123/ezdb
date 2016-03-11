#!/usr/bin/env python
# encoding: utf-8

'''
CS419 postgres_db.py file
Group 15: Rudy Gonzalez, Bobby Hines
'''


import psycopg2
import psycopg2.errorcodes
import psycopg2.extras

#http://initd.org/psycopg/docs/usage.html
#required editing pg_hba.conf file in path etc/postgresql/9.3/main from peer to trust

class Postgres_Database(object):
        
    '''initializes database class variables and connect to root dbms'''
    #def __init__(self, dbtype='postgreSQL', host='localhost', port='', user='postgres', password='password'):
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
            'dbname': self.dbname,
            'user': self.user,
            'password': self.password,
        }
        
        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cur = self.conn.cursor()
            self.conn.commit()

        except psycopg2.DatabaseError, err:
            return err
        
    # connect to existing named database
    def connect_database(self, dbname):

        self.dbname = dbname
        self.conn_config['dbname'] = self.dbname

        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cur = self.conn.cursor()
            self.conn.commit()

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred during connection:\n" + str(err)

    def list_databases(self):

        sql_string = "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';"

        try:
            self.cur.execute(sql_string)
            self.conn.commit()

            dblist_data = self.cur.fetchall()
            self.conn.commit()

            dblist = []

            for row in dblist_data:
                dblist.append(row[0])

            return dblist

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred:\n" + str(err)

    def create_database(self, dbname):

        self.dbname = dbname

        try:
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            sql_string = "CREATE DATABASE {}".format(self.dbname)
            self.cur.execute(sql_string)
            self.conn.commit()
            return "{} postgreSQL database created.".format(self.dbname)

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
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
            'dbname': 'postgres'
        }

        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.conn.commit()
            self.cur = self.conn.cursor()

            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            sql_string = "DROP DATABASE %s" % self.dbname
            self.cur.execute(sql_string)
            self.conn.commit()
            return "{} postgreSQL database deleted.".format(self.dbname)

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred during deletion:\n" + str(err)

    def list_database_tables(self):

        sql_string = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"

        try:
            self.cur.execute(sql_string)
            self.conn.commit()

            tablelist_data = self.cur.fetchall()

            tablelist = []

            for row in tablelist_data:
                tablelist.append(row[0])

            return tablelist

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred during table retrieval:\n" + str(err)

    def delete_table(self, table_name):

        sql_string = "DROP TABLE {};".format(str(table_name))

        try:
            self.cur.execute(sql_string)
            self.conn.commit()

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred during deletion:\n" + str(err)

    def browse_table(self, table):

        sql_string = "SELECT * from {}".format(table)

        try:
            self.cur.execute(sql_string + " LIMIT 0;")
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

            except psycopg2.DatabaseError, err:
                self.conn.rollback()
                return "error", err

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "error", err

    def view_table_struct(self, table):

        sql_string = "SELECT column_name, data_type, character_maximum_length, collation_name, is_nullable," \
                     " column_default from INFORMATION_SCHEMA.COLUMNS where table_name ='{}'".format(table)

        try:
            self.cur.execute(sql_string + " LIMIT 0;")
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

            except psycopg2.DatabaseError, err:
                self.conn.rollback()
                return "error", err

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "error", err

    def create_table(self, sql):

        sql_string = sql

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            return "success", " "

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "error", err

    def execute_SQL(self, sql):

        sql_string = sql
        col_titles = []
        row_count = 0

        try:
            if "select" in sql_string.lower():

                self.cur.execute(sql_string + " LIMIT 0;")
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

            except psycopg2.DatabaseError, err:
                if str(err) == "no results to fetch":
                    return "success", sql_results, col_titles, row_count
                else:
                    return "error", err

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
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

            except psycopg2.DatabaseError, err:
                self.conn.rollback()
                return "error", err

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "error", err

    def get_userlist(self):

        sql_string = "SELECT usename FROM pg_user WHERE usename != 'postgres'"

        try:

            self.cur.execute(sql_string + ";")
            self.conn.commit()

            try:
                user_results_data = self.cur.fetchall()
                user_results = []

                for row in user_results_data:
                    user_results.append(row[0])

                return user_results

            except psycopg2.DatabaseError, err:
                self.conn.rollback()
                return err

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return err

