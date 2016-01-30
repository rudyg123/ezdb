__author__ = 'rudy'

#import curses
import psycopg2
import psycopg2.errorcodes
import psycopg2.extras
import mysql.connector
from mysql.connector import errorcode
import npyscreen

'''
def curses_setup():
    screen = curses.initscr()
    screen.addstr(10, 20, "ezdb", curses.A_BLINK)
    screen.refresh()
    screen.getch()
    curses.endwin()
'''
#http://initd.org/psycopg/docs/usage.html
#required editing pg_hba.conf file in path etc/postgresql/9.3/main from peer to trust

class Database:

    '''initializes database class variables and connect to root dbms'''
    def __init__(self, dbtype, user, password, host):
        self.dbtype = dbtype
        self.dbname = ''
        self.user = user
        self.password = password
        self.host = host

        self.cur = ''
        self.conn = ''

        self.conn_config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
        }

        if self.dbtype == 'postgresql':

            try:
                self.conn = psycopg2.connect(**self.conn_config)
                self.cur = self.conn.cursor()

            except psycopg2.errorcodes, err:
                print errorcodes.lookup(err.pgcode)
                return

        elif self.dbtype == 'mysql':

            try:
                self.conn = mysql.connector.connect(**self.conn_config)
                self.cur = self.conn.cursor()

            except mysql.connector.Error, err:

                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Invalid username and/or password.")
                else:
                    print("There was a problem connecting to the DBMS.")
                return

        print "Connected to {} DBMS.".format(self.dbtype)

    '''connect to existing named database
    -still need to implement user db authentication'''
    def connect_database(self, dbname):

        self.dbname = dbname

        if self.dbtype == 'postgresql':

            self.conn_config['dbname'] = self.dbname

            try:
                self.conn = psycopg2.connect(**self.conn_config)
                self.cur = self.conn.cursor()

            except psycopg2.errorcodes, err:
                print errorcodes.lookup(err.pgcode)
                return

        elif self.dbtype == 'mysql':

            self.conn_config['database'] = self.dbname
            try:
                self.conn = mysql.connector.connect(**self.conn_config)
                self.cur = self.conn.cursor()

            except mysql.connector.Error, err:

                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Invalid username and/or password")

                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist.")

                else:
                    print(err)

                return

        print "Connected to database {}.".format(self.dbname)

    def list_databases(self):

        if self.dbtype == "postgresql":
            sql_string = "SELECT datname FROM pg_database WHERE datistemplate = false;"

            try:
                self.cur.execute(sql_string)
            except psycopg2.errorcodes, err:
                print errorcodes.lookup(err.pgcode)
                return

        elif self.dbtype == "mysql":
            sql_string = "SHOW DATABASES;"
            try:
                self.cur.execute(sql_string)
            except mysql.connector.Error, err:
                print(err)

        rows = self.cur.fetchall()
        print "{} Databases:".format(self.dbtype)
        for row in rows:
            print "   ", row[0]
        print "\n"

    def create_database(self, dbname):

        self.dbname = dbname

        if self.dbtype == "postgresql":

            try:
                self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                sql_string = "CREATE DATABASE {}".format(self.dbname)
                self.cur.execute(sql_string)
                print "{} postgreSQL database created.".format(self.dbname)

            except psycopg2.errorcodes, err:
                print "There was a problem creating the database"
                print 'Error %s' % err

        elif self.dbtype == "mysql":

            try:

                sql_string = "CREATE DATABASE {}".format(self.dbname)
                self.cur.execute(sql_string)
                print "{} MySQL database created.".format(self.dbname)

            except mysql.connector.Error, err:
                print "There was a problem creating the database"
                print 'Error %s' % err


    def delete_database(self):

        if self.conn:
            self.conn.close() #close db connection

        #connect to dbms as root
        self.conn_config.clear()
        self.conn_config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
        }


        if self.dbtype == "postgresql":
            try:
                self.conn = psycopg2.connect(**self.conn_config)
                self.cur = self.conn.cursor()

                self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                sql_string = "DROP DATABASE %s" % self.dbname
                self.cur.execute(sql_string)
                print "{} postgreSQL database deleted.".format(self.dbname)

            except psycopg2.DatabaseError, e:
                print "There was a problem deleting the database"
                print 'Error %s' % e

        elif self.dbtype == "mysql":
            try:
                self.conn = mysql.connector.connect(**self.conn_config)
                self.cur = self.conn.cursor()

                sql_string = "DROP DATABASE {}".format(self.dbname)
                self.cur.execute(sql_string)
                print "{} MySQL database deleted.".format(self.dbname)

            except mysql.connector.Error, err:
                print "There was a problem deleting the database"
                print 'Error %s' % err

'''
def error_handler(dbname, error):
    print "There was a problem connecting to the database"
    print 'Error %s' % error
    print("Database does not exist.")
    createdb_input = raw_input("Do want to create database {} now? Type 'yes' to confirm: ".format(dbname))
    if createdb_input == "yes":
        Database.create_database(mypostgres)
'''


'''
def displaytable():
    sql_string = "SELECT * FROM actor;"
    cur.execute(sql_string)
    rows = cur.fetchall()
    for row in rows:
        print "   ", row[0], row[1], row[2]
'''
#curses_setup()

'''postgresql test functions'''
#mypostgres = Database('postgresql', 'postgres', 'password', 'localhost')

#mypostgres.connect_database('testdb')
#mypostgres.create_database('gooddb')
#mypostgres.delete_database()
#mypostgres.list_databases()
#mypostgres.close_database()

'''mysql test functions'''
my_mysql = Database('mysql', 'root', 'password', 'localhost')
#my_mysql.connect_database('testdb_mysql')
my_mysql.list_databases()

#mypostgres.close_database()
#my_mysql.close_database()
my_mysql.create_database('testdb4')
my_mysql.list_databases()

#deletedb('mysql', 'testdb_mysql3')

#displaytable()
