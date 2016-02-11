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
        
        '''
        self.cur = ''
        self.conn = ''

        self.conn_config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
        }

        self.activedb = activedb
        
        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cur = self.conn.cursor()
            self.conn.commit()

        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return
        '''
        
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

        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return
        
    #connect to existing named database
    #-still need to implement user db authentication
    def connect_database(self, dbname):

        self.dbname = dbname
        self.conn_config['dbname'] = self.dbname

        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cur = self.conn.cursor()
            self.conn.commit()

        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return

        #print "Connected to database {}.".format(self.dbname)

    def list_databases(self):

        sql_string = "SELECT datname FROM pg_database WHERE datistemplate = false;"

        try:
            self.cur.execute(sql_string)
            self.conn.commit()
        except psycopg2.errorcodes, err:

            return err.lookup(err.pgcode)

        dblist_data = self.cur.fetchall()
        self.conn.commit()

        dblist = []

        for row in dblist_data:
            dblist.append(row[0])

        return dblist


    def create_database(self, dbname):

        self.dbname = dbname

        try:
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            sql_string = "CREATE DATABASE {}".format(self.dbname)
            self.cur.execute(sql_string)
            print "{} postgreSQL database created.".format(self.dbname)

        except psycopg2.errorcodes, err:
            print "There was a problem creating the database"
            print 'Error %s' % err

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
            print "{} postgreSQL database deleted.".format(self.dbname)

        except psycopg2.errorcodes, err:
            print "There was a problem deleting the database"
            print 'Error %s' % err

    def list_database_tables(self):

        sql_string = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"

        try:
            self.cur.execute(sql_string)
        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return

        rows = self.cur.fetchall()
        print "{} Database Tables:".format(self.dbname)
        for row in rows:
            print "   ", row[0]
        print "\n"

    def display_table_struct(self, table_name):

        sql_string = "SELECT column_name, data_type, collation_name, is_nullable, column_default FROM information_schema.columns WHERE table_name ='{}';".format(table_name)

        try:
            self.cur.execute(sql_string)
        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return

        rows = self.cur.fetchall()

        print "{} Table Structure:".format(table_name)
        for row in rows:
            print "   ", row[0], row[1], row[2], row[3], row[4]
        print "\n"

    def delete_table(self, table_name):

        sql_string = "DROP TABLE {};".format(table_name)

        try:
            self.cur.execute(sql_string)
        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return


class Postgres_Table(object):

    #postgresql table form dropdown values
    postgresql_field_type_list = ['CHAR','VARCHAR','TEXT','BIT','VARBIT','SMALLINT','INT','BIGINT','SMALLSERIAL',
                                  'SERIAL','BIGSERIAL','NUMERIC','DOUBLE PRECISION','REAL','MONEY','BOOL',
                                  'DATE','TIMESTAMP','TIMESTAMP WITH TIME ZONE','TIME','TIME WITH TIME ZONE','BYTEA']

    postgresql_field_collat_list = ['C','POSIX','C.UTF-8','en_AG','en_AG.utf8','en_AU.utf8','en_AU.utf8','en_BW.utf8',
                                    'en_BW.utf8','en_CA.utf8','en_CA.utf8','en_DK.utf8','en_DK.utf8','en_GB.utf8',
                                    'en_GB.utf8','en_HK.utf8','en_HK.utf8','en_IE.utf8','en_IE.utf8','en_IN',
                                    'en_IN.utf8','en_NG','en_NG.utf8','en_NZ.utf8','en_NZ.utf8','en_PH.utf8',
                                    'en_PH.utf8','en_SG.utf8','en_SG.utf8','en_US.utf8','en_US.utf8','en_ZA.utf8',
                                    'en_ZA.utf8','en_ZM','en_ZM.utf8','en_ZW.utf8','en_ZW.utf8']

    postgresql_field_constraint_list = ['PRIMARY KEY','UNIQUE']


    def __init__(self,db,table_name, field_name, field_type):
        self.db = db
        self.table_name = table_name
        self.table_comment = ''

        self.field_name = field_name
        self.field_type = field_type
        self.field_length_or_val = ''
        self.field_collation = ''
        self.field_attrib = ''
        self.field_nullval = 'NULL'
        self.field_default = ''
        self.field_autoincrement = ''
        self.field_primarykey = ''
        self.field_unique = ''
        self.field_index = ''
        self.field_fulltext = ''

        sql_string = "CREATE TABLE {}({} {});".format(self.table_name, self.field_name, self.field_type)

        try:
            self.db.cur.execute(sql_string)
            self.db.conn.commit()
        except psycopg2.errorcodes, err:
            print err.lookup(err.pgcode)
            return

