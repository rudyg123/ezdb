#!/usr/bin/env python
# encoding: utf-8

'''
CS419 mysql_db.py file
Group 15: Rudy Gonzalez, Bobby Hines
'''

import mysql.connector
from mysql.connector import errorcode

class MySQL_Database(object):

    '''initializes database class variables and connect to root dbms'''
    def __init__(self, dbtype, host, port, user, password):
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

        try:

            sql_string = "CREATE DATABASE {}".format(self.dbname)
            self.cur.execute(sql_string)
            print "{} MySQL database created.".format(self.dbname)

        except mysql.connector.Error, err:
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
            self.conn = mysql.connector.connect(**self.conn_config)
            self.cur = self.conn.cursor()

            sql_string = "DROP DATABASE {}".format(self.dbname)
            self.cur.execute(sql_string)
            print "{} MySQL database deleted.".format(self.dbname)

        except mysql.connector.Error, err:
            print "There was a problem deleting the database"
            print 'Error %s' % err

    def list_database_tables(self):

        sql_string = "SHOW TABLES;"
        try:
            self.cur.execute(sql_string)
        except mysql.connector.Error, err:
            print(err)

        rows = self.cur.fetchall()
        print "{} Database Tables:".format(self.dbname)
        for row in rows:
            print "   ", row[0]
        print "\n"

    def display_table_struct(self, table_name):

        sql_string = "DESCRIBE {};".format(table_name)

        try:
            self.cur.execute(sql_string)
        except mysql.connector.Error, err:
            print(err)

        rows = self.cur.fetchall()

        print "{} Table Structure:".format(table_name)
        for row in rows:
            print "   ", row[0], row[1], row[2], row[3], row[4]
        print "\n"

    def delete_table(self, table_name):

        sql_string = "DROP TABLE {};".format(table_name)

        try:
            self.cur.execute(sql_string)
        except mysql.connector.Error, err:
            print(err)

class MySQL_Table(object):

    mysql_field_type_list = ['CHAR','VARCHAR','TINYTEXT','TEXT','LONGTEXT',
                             'TINYINT','SMALLINT','MEDIUMINT','INT','BIGINT','FLOAT','DOUBLE',
                             'DATE','DECIMAL','DATETIME','TIMESTAMP','TIME','YEAR',
                             'TINYBLOB','BLOB','MEDIUMBLOB','LONGBLOB',
                             'ENUM','SET','BIT','BOOL','BINARY','VARBINARY']

    mysql_field_collat_list = [
        'armscii8_bin','armscii8_general_ci','ascii_bin','ascii_general_ci','big5_bin','big5_chinese_ci','binary',
        'cp1250_bin','cp1250_croatian_ci','cp1250_czech_cs','cp1250_general_ci','cp1250_polish_ci','cp1251_bin',
        'cp1251_bulgarian_ci','cp1251_general_ci','cp1251_general_cs','cp1251_ukranian_ci','cp1256_bin',
        'cp1256_general_ci','cp1257_bin','cp1257_general_ci','cp1257_lithuanian_ci','cp850_bin','cp850_general_ci',
        'cp852_bin','cp852_general_ci','cp866_bin','cp866_general_ci','cp932_bin','cp932_japanese_ci','dec8_bin',
        'dec8_swedish_ci','eucjpms_bin','eucjpms_japanese_ci','euckr_bin','euckr_korean_ci','gb2312_bin',
        'gb2312_chinese_ci','gbk_bin','gbk_chinese_ci','geostd8_bin','geostd8_general_ci','greek_bin','greek_general_ci',
        'hebrew_bin','hebrew_general_ci','hp8_bin','hp8_english_ci','keybcs2_bin','keybcs2_general_ci','koi8r_bin',
        'koi8r_general_ci','latin1_bin','latin1_danish_ci','latin1_general_ci','latin1_general_cs','latin1_german1_ci',
        'latin1_german2_ci','latin1_spanish_ci','latin1_swedish_ci','latin2_bin','latin2_croatian_ci','latin2_czech_cs',
        'latin2_general_ci','latin2_hungarian_ci','latin5_bin','latin5_turkish_ci','latin7_bin','latin7_estonian_cs',
        'latin7_general_ci','latin7_general_cs','macce_bin','macce_general_ci','macroman_bin','macroman_general_ci',
        'sjis_bin','sjis_japanese_ci','swe7_bin','swe7_swedish_ci','tis620_bin','tis620_thai_ci','ucs2_bin',
        'ucs2_czech_ci','ucs2_danish_ci','ucs2_esperanto_ci','ucs2_estonian_ci','ucs2_general_ci',
        'ucs2_general_mysql500_ci','ucs2_hungarian_ci','ucs2_icelandic_ci','ucs2_latvian_ci','ucs2_lithuanian_ci',
        'ucs2_persian_ci','ucs2_polish_ci','ucs2_roman_ci','ucs2_romanian_ci','ucs2_sinhala_ci','ucs2_slovak_ci',
        'ucs2_slovenian_ci','ucs2_spanish_ci','ucs2_spanish2_ci','ucs2_swedish_ci','ucs2_turkish_ci','ucs2_unicode_ci',
        'ujis_bin','ujis_japanese_ci','utf8_bin','utf8_czech_ci','utf8_danish_ci', 'utf8_esperanto_ci',
        'utf8_estonian_ci','utf8_general_ci','utf8_general_mysql500_ci','utf8_hungarian_ci','utf8_icelandic_ci',
        'utf8_latvian_ci','utf8_lithuanian_ci','utf8_persian_ci','utf8_polish_ci','utf8_roman_ci','utf8_romanian_ci',
        'utf8_sinhala_ci','utf8_slovak_ci','utf8_slovenian_ci','utf8_spanish_ci','utf8_spanish2_ci','utf8_swedish_ci',
        'utf8_turkish_ci','utf8_unicode_ci','utf8mb4_bin','utf8mb4_czech_ci','utf8mb4_danish_ci', 'utf8mb4_esperanto_ci',
        'utf8mb4_estonian_ci','utf8mb4_general_ci','utf8mb4_hungarian_ci','utf8mb4_icelandic_ci','utf8mb4_latvian_ci',
        'utf8mb4_lithuanian_ci','utf8mb4_persian_ci','utf8mb4_polish_ci','utf8mb4_roman_ci','utf8mb4_romanian_ci',
        'utf8mb4_sinhala_ci','utf8mb4_slovak_ci','utf8mb4_slovenian_ci','utf8mb4_spanish_ci','utf8mb4_spanish2_ci',
        'utf8mb4_swedish_ci','utf8mb4_turkish_ci','utf8mb4_unicode_ci','utf16_bin','utf16_czech_ci','utf16_danish_ci',
        'utf16_esperanto_ci','utf16_estonian_ci','utf16_general_ci','utf16_hungarian_ci','utf16_icelandic_ci',
        'utf16_latvian_ci','utf16_lithuanian_ci','utf16_persian_ci','utf16_polish_ci','utf16_roman_ci','utf16_romanian_ci',
        'utf16_sinhala_ci','utf16_slovak_ci','utf16_slovenian_ci','utf16_spanish_ci','utf16_spanish2_ci',
        'utf16_swedish_ci','utf16_turkish_ci','utf16_unicode_ci','utf32_bin','utf32_czech_ci','utf32_danish_ci',
        'utf32_esperanto_ci','utf32_estonian_ci','utf32_general_ci','utf32_hungarian_ci','utf32_icelandic_ci',
        'utf32_latvian_ci','utf32_lithuanian_ci','utf32_persian_ci','utf32_polish_ci','utf32_roman_ci',
        'utf32_romanian_ci','utf32_sinhala_ci','utf32_slovak_ci','utf32_slovenian_ci','utf32_spanish_ci',
        'utf32_spanish2_ci','utf32_swedish_ci','utf32_turkish_ci','utf32_unicode_ci']

    mysql_field_attrib_list = ['binary','unsigned','unsigned zerofill','on update current_timestamp']
    mysql_field_constraint_list = ['PRIMARY KEY','UNIQUE','INDEX']
    mysql_engine_list = ['InnoDB','MyISAM','MRG_MYISAM','CSV','MEMORY','BLACKHOLE','PERFORMANCE_SCHEMA','ARCHIVE']

    def __init__(self,db,table_name, field_name, field_type):
        self.db = db
        self.table_name = table_name
        self.table_storage_eng = 'innoDB'
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
        except mysql.connector.Error, err:
            print(err)
