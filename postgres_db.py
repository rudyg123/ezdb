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
        }
        
        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cur = self.conn.cursor()
            self.conn.commit()

        except psycopg2.DatabaseError, err:
            return err
        
    #connect to existing named database
    #-still need to implement user db authentication
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

        #print "Connected to database {}.".format(self.dbname)

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

    def display_table_struct(self, table_name):
        #get number of table columns select count(*) from information_schema.columns where table_name='x';
        sql_string = "SELECT column_name, data_type, collation_name, is_nullable, column_default FROM information_schema.columns WHERE table_name ='{}';".format(table_name)
        sql_string = "SELECT * FROM information_schema.columns WHERE table_name ='{}';".format(table_name)
        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            fields = self.cur.fetchall()
        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred:\n" + str(err)

        sql_string = "SELECT COUNT(*) FROM information_schema.columns WHERE table_name ='{}';".format(table_name)
        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            numcols = self.cur.fetchall()
            field_row = []
            table_struct = []

            #print "{} Table Structure:".format(table_name)
            for row in fields:
                for c in range(numcols):
                    field_row.append(row[c])
                table_struct.append(field_row)
                #print "   ", row[0], row[1], row[2], row[3], row[4]
            return table_struct

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred:\n" + str(err)

    def delete_table(self, table_name):

        sql_string = "DROP TABLE {};".format(str(table_name))

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "The following problem occurred during deletion:\n" + str(err)

    def browse_table(self, table):

        sql_string = "SELECT * from {}".format(table) + ";"

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            try:
                browse_results_data = self.cur.fetchall()
                browse_results = []

                for row in browse_results_data:
                    browse_results.append(row)
                return "success", browse_results
            except psycopg2.DatabaseError, err:
                self.conn.rollback()
                return "error", err

        except psycopg2.DatabaseError, err:
            self.conn.rollback()
            return "error", err

    def view_table_struct(self, table):

        sql_string = "SELECT * from information_schema.columns WHERE table_name = '{}'".format(table) + ";"

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
            try:
                struct_results_data = self.cur.fetchall()
                struct_results = []

                for row in struct_results_data:
                    struct_results.append(row)
                return "success", struct_results
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

            except psycopg2.DatabaseError, err:
                if str(err) == "no results to fetch":
                    sql_results.append("Operation completed successfully")
                    return "success", sql_results
                else:
                    return "error", err

        except psycopg2.DatabaseError, err:
            return "error", err


    '''
    def get_collation(self, dbname):

        self.dbname = dbname
        sql_string = "SELECT '" + str(self.dbname) + "', datcollate FROM pg_database;"

        try:
            self.cur.execute(sql_string)
        except psycopg2.DatabaseError, err:
            return "The following problem occurred during collation retrieval:\n" + str(err)

        collate_data = self.cur.fetchall()
        collatelist = []

        for row in collate_data:
            collatelist.append(row[0])

        return collatelist
    '''

