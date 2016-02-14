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
mypostgres.connect_database('postgres')
dberror = mypostgres.create_database('testdb')
#print dberror
#mypostgres.delete_database('gooddb')
#pdb_dblist = mypostgres.list_databases()
#print pdb_dblist

#pdb_tablelist = mypostgres.list_database_tables()
#print pdb_tablelist
#pdb.Postgres_Table(mypostgres,'test_table01','id','int')
#pdb.Postgres_Table(mypostgres,'test_table02','id','int')
#pdb.Postgres_Table(mypostgres,'test_table03','id','int')
#pdb_tablelist = mypostgres.list_database_tables()
#print pdb_tablelist
results = mypostgres.display_table_struct('actor')
for i in results:
    print i
#msg = mypostgres.delete_table('test_table01')
#print msg
#mypostgres.list_database_tables()

#mypostgres.close_database()

'''mysql test functions'''
#my_mysql = mdb.MySQL_Database()
#my_mysql.connect_DBMS('mysql', 'localhost', '3306', 'root', 'password')
#my_mysql.connect_database('testdb_mysql')

#dblist=my_mysql.list_databases()
#print dblist

#tablelist = my_mysql.list_database_tables()
#print tablelist

#mypostgres.close_database()
#my_mysql.close_database()
#dberror = my_mysql.create_database('testdb')
#print dberror
#my_mysql.delete_database('testdb02_mysql')
#my_mysql.list_databases()
#mdb.MySQL_Table(my_mysql,'director','name','varchar(30)')
#my_mysql.display_table_struct('actor')
#director = Table(my_mysql,'director','id','int')
#actor.create_table()
#my_mysql.delete_table('actor')
#my_mysql.list_database_tables()

#mypostgres.list_databases()
#displaytable()
