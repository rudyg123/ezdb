#!/usr/bin/env python
# encoding: utf-8

'''
CS419 ezdb backend main file - used to launch backend functions.
Uses postgres_db.py and mysql_db.py files.
Group 15: Rudy Gonzalez, Bobby Hines
'''

import postgres_db as pdb
import mysql_db as mdb


'''postgresql test functions'''
mypostgres = pdb.Postgres_Database()
mypostgres.connect_DBMS('postgresql', 'localhost', '5432', 'postgres', 'password')
mypostgres.connect_database('testdb')
#mypostgres.create_database('gooddb')
#mypostgres.delete_database('gooddb')
mypostgres.list_databases()
#mypostgres.list_database_tables()
#producer = Table(mypostgres,'producer','id','int')
#mypostgres.display_table_struct('actor')
#mypostgres.delete_table('producer')
#mypostgres.list_database_tables()

#mypostgres.close_database()

'''mysql test functions'''
#my_mysql = mdb.MySQL_Database('mysql', 'localhost', '3306', 'root', 'password')
#my_mysql.connect_database('testdb_mysql')

#my_mysql.list_databases()
#my_mysql.list_database_tables()

#mypostgres.close_database()
#my_mysql.close_database()
#my_mysql.create_database('testdb4')
#my_mysql.delete_database('testdb02_mysql')
#my_mysql.list_databases()
#mdb.MySQL_Table(my_mysql,'director','name','varchar(30)')
#my_mysql.display_table_struct('director')
#director = Table(my_mysql,'director','id','int')
#actor.create_table()
#my_mysql.delete_table('actor')
#my_mysql.list_database_tables()

#mypostgres.list_databases()
#displaytable()
