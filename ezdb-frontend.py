#!/usr/bin/env python

import npyscreen
import postgres_db as pdb
import mysql_db as mdb


# ActionForm includes "Cancel" in addition to "OK"
class Initial(npyscreen.ActionForm):
    sessionType, db = None, None

    def create(self):
        # Title text
        self.nextrely += 3  # Move down
        self.nextrelx += 24  # Move right (centered))
        self.add(npyscreen.FixedText, value="                _  _     ", editable=False)
        self.add(npyscreen.FixedText, value="               | || |    ", editable=False)
        self.add(npyscreen.FixedText, value="  ___  ____  __| || |__  ", editable=False)
        self.add(npyscreen.FixedText, value=" / _ \|_  / / _` || '_ \ ", editable=False)
        self.add(npyscreen.FixedText, value="|  __/ / / | (_| || |_) |", editable=False)
        self.add(npyscreen.FixedText, value=" \___|/___| \__,_||_.__/ ", editable=False)

        # Add session options and save the selected value
        self.nextrely += 1  # Move down
        self.nextrelx += 2  # Move right (centered)
        self.add(npyscreen.FixedText, value="Choose Database Type:", editable=False)
        self.db = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["postgreSQL", "MySQL"],
                           scroll_exit=True)

        # Help menu guidance
        self.nextrely += 3
        self.nextrelx -= 17
        self.add(npyscreen.FixedText, value="Note: Press ctrl+q from any screen to open the help window.", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Select the database type with which you'd like to interact this session. This application " \
                   "supports MySQL and PostgreSQL database systems."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def on_ok(self):
        # For debugging:
        # npyscreen.notify_confirm("You selected " + str(self.db.value[0]))
        self.parentApp.dbtype = self.db.value[0]
        self.parentApp.setNextForm("ConnectDBMS")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=2)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class ConnectDBMS(npyscreen.ActionForm):
    storedConnections, result, dbtype = (None,)*3

    def create(self):
        # Set default DBMS connection values
        # For debugging:
        # npyscreen.notify_confirm("The value of dbtype in ConnectDBMS is " + str(dbtype))
        if self.parentApp.dbtype == 0:
            self.add(npyscreen.FixedText, value="Enter PostgreSQL Database System Connection Settings:", editable=False)
            self.parentApp.port = '5432'
            self.parentApp.username = 'postgres'
            self.parentApp.password = 'password'
        elif self.parentApp.dbtype == 1:
            self.add(npyscreen.FixedText, value="Enter MySQL Database System Connection Settings:", editable=False)
            self.parentApp.port = '3306'
            self.parentApp.username = 'root'
            self.parentApp.password = 'password'

        self.nextrely += 2  # Move down
        self.parentApp.host = self.add(npyscreen.TitleText, name="Hostname:", value="127.0.0.1")
        self.nextrely += 1  # Move down
        self.parentApp.port = self.add(npyscreen.TitleText, name="Port:", value=self.parentApp.port)
        self.nextrely += 1  # Move down
        self.parentApp.username = self.add(npyscreen.TitleText, name="Username:", value=self.parentApp.username)
        self.nextrely += 1  # Move down
        self.parentApp.password = self.add(npyscreen.TitleText, name="Password:", value=self.parentApp.password)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Enter the connection settings for the database system with which you'd like to interact. The " \
                   "initial settings are the default settings for local databases."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def on_ok(self):
        self.result = None

        # Connect to DBMS
        if self.parentApp.dbtype == 0:
            self.parentApp.dbms = pdb.Postgres_Database()
            self.result = self.parentApp.dbms.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value,
                                                           self.parentApp.port.value, self.parentApp.username.value,
                                                           self.parentApp.password.value)

        elif self.parentApp.dbtype == 1:
            self.parentApp.dbms = mdb.MySQL_Database()
            self.result = self.parentApp.dbms.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value,
                                                           self.parentApp.port.value, self.parentApp.username.value,
                                                           self.parentApp.password.value)

        if self.result is not None:
            npyscreen.notify_confirm("There was a problem connecting to the database system:\n" + str(self.result))
            self.result = None
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        else:
            self.parentApp.setNextForm("DatabaseWindow")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class DatabaseWindow(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit, dbList, dbtype_str = (None,)*9

    def create(self):

        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1, scroll_exit=True)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=15)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=25)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=34)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=45)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)


        self.dbList = self.parentApp.dbms.list_databases()

        self.nextrely += 1  # Move down

        if self.parentApp.dbtype == 0:
            self.dbtype_str = "PostgreSQL"
        elif self.parentApp.dbtype == 1:
            self.dbtype_str = "MySQL"

        self.add(npyscreen.TitleSelectOne, w_id="wActiveDB", max_height=10,
                 name="{} Databases:".format(self.dbtype_str), value=[0], values=self.dbList, scroll_exit=True)

        # Database button options
        self.nextrely += 1  # Move down
        self.add(OpenDBButton, name="Open Database")

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewDB_name", name="New Database Name:", relx=4,
                 begin_entry_at=22, use_two_lines=False)

        self.add(CreateDBButton, name="Create")

        self.nextrely += 1  # Move down
        self.add(DeleteDBButton, name="Delete Database")

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")

    def while_waiting(self):
        self.get_widget("wActiveDB").display()


class TablesWindow(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=15)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=25)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=34)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=45)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.nextrely += 1  # Move down
        self.add(npyscreen.FixedText, value="Here is the TABLES window", editable=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.BoxTitle, w_id="wTables_box", name="{} Tables".format(self.parentApp.active_db),
                 values=self.parentApp.tableList, max_width=25, max_height=8, scroll_exit=True)

        self.nextrely += 1  # Move down
        self.add(ViewTableStructButton, name="View Table Structure", rely=6, relx=27, max_width=22)
        self.add(BrowseTableButton, name="Browse Table", rely=6, relx=52, max_width=12)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewTable_name", name="New Table Name:",
                 relx=29, max_width=35, use_two_lines=False)

        self.add(BuildTableButton, name="Build", relx=27, max_width=35)

        self.nextrely += 1  # Move down
        self.add(DeleteTableButton, name="Delete Table", relx=27, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.BoxTitle, w_id="wTableResults_box", name="Table Results",
                 values=self.parentApp.table_results, max_width=75, max_height=9, scroll_exit=True)

        # self.nextrely += 1  # Move down
        # self.add(npyscreen.GridColTitles, w_id="w_TableGrid", col_titles=self.parentApp.tablefield_cols, relx=1)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    # PEP8 Ignore (external library naming convention)
    def beforeEditing(self):
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class TableCreatePostgreSQLForm(npyscreen.ActionForm):

    def create(self):
        postgresql_field_type_list = ['CHAR', 'VARCHAR', 'TEXT', 'BIT', 'VARBIT', 'SMALLINT', 'INT', 'BIGINT',
                                      'SMALLSERIAL', 'SERIAL', 'BIGSERIAL', 'NUMERIC', 'DOUBLE PRECISION', 'REAL',
                                      'MONEY', 'BOOL', 'DATE', 'TIMESTAMP', 'TIMESTAMP WITH TIME ZONE', 'TIME',
                                      'TIME WITH TIME ZONE', 'BYTEA']

        postgresql_field_collat_list = [None, 'en_US.utf8', 'C', 'POSIX', 'C.UTF-8', 'en_AG', 'en_AG.utf8',
                                        'en_AU.utf8', 'en_AU.utf8', 'en_BW.utf8', 'en_BW.utf8', 'en_CA.utf8',
                                        'en_CA.utf8', 'en_DK.utf8', 'en_DK.utf8', 'en_GB.utf8', 'en_GB.utf8',
                                        'en_HK.utf8', 'en_HK.utf8', 'en_IE.utf8', 'en_IE.utf8', 'en_IN', 'en_IN.utf8',
                                        'en_NG', 'en_NG.utf8', 'en_NZ.utf8', 'en_NZ.utf8', 'en_PH.utf8', 'en_SG.utf8',
                                        'en_SG.utf8', 'en_ZA.utf8', 'en_ZA.utf8', 'en_ZM', 'en_ZM.utf8', 'en_ZW.utf8',
                                        'en_ZW.utf8']

        postgresql_field_constraint_list = [None, 'PRIMARY KEY', 'UNIQUE']

        self.add(npyscreen.TitleText, w_id="wField_name", name="Field Name: ", max_width=35, begin_entry_at=15,
                 use_two_lines=False)
        self.add(npyscreen.TitleSelectOne, w_id="wField_type", max_height=4, name="Type: ", value=[0],
                 values=postgresql_field_type_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wField_length_or_val", name="Length/Value: ", max_width=35,
                 begin_entry_at=15, use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wCollation", max_height=4, name="Collation: ", value=[0],
                 values=postgresql_field_collat_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wConstraint", max_height=4, name="Constraint: ", value=[0],
                 values=postgresql_field_constraint_list, rely=2, relx=40, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.SelectOne, w_id="wNot_null", values=["Not Required", "Required"], value=[0],
                 max_width=20, max_height=4, relx=40)

        # self.add(npyscreen.Checkbox, w_id="wAuto_increment", name="Auto Increment?", relx=40)
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wDefault", name="Default: ", max_width=35, relx=40)

        self.nextrely += 2  # Move down
        self.add(AddFieldButton, name="Add Field", relx=40, max_width=13)
        self.add(CreateTableButton, name="Create Table", relx=40, max_width=13)

    def on_ok(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")

    def on_cancel(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")


class TableCreateMySQLForm(npyscreen.ActionForm):

    def create(self):
        mysql_field_type_list = ['CHAR','VARCHAR','TINYTEXT','TEXT','LONGTEXT',
                                 'TINYINT','SMALLINT','MEDIUMINT','INT','BIGINT','FLOAT','DOUBLE',
                                 'DATE','DECIMAL','DATETIME','TIMESTAMP','TIME','YEAR',
                                 'TINYBLOB','BLOB','MEDIUMBLOB','LONGBLOB',
                                 'ENUM','SET','BIT','BOOL','BINARY','VARBINARY']

        mysql_field_collat_list = [None,
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

        mysql_field_attrib_list = [None, 'binary','unsigned','unsigned zerofill','on update current_timestamp']
        mysql_field_constraint_list = [None, 'PRIMARY KEY','UNIQUE','INDEX']
        mysql_engine_list = ['InnoDB','MyISAM','MRG_MYISAM','CSV','MEMORY','BLACKHOLE','PERFORMANCE_SCHEMA','ARCHIVE']

        self.add(npyscreen.TitleText, w_id="wField_name", name="Field Name: ", max_width=35, relx=2,
                 use_two_lines=False)

        self.add(npyscreen.TitleSelectOne, w_id="wField_type", max_height=5, name="Type: ", value=[0],
                 values=mysql_field_type_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wField_length_or_val", name="Length/Value: ", max_width=35,
                 use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wCollation", max_height=4, name="Collation: ", value=[0],
                 values=mysql_field_collat_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wAttribute", max_height=5, name="Attribute: ", value=[0],
                 values=mysql_field_attrib_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wConstraint", max_height=4, name="Constraint: ", value=[0],
                 values=mysql_field_constraint_list, rely=2, relx=40, max_width=37)

        self.nextrely += 1  # Move down
        self.add(npyscreen.SelectOne, w_id="wNot_null", values=["Not Required", "Required"], value=[0],
                 max_width=20, max_height=2, relx=40)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wDefault", name="Default: ", max_width=25, relx=40)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wAuto_increment", name="Auto Increment: ", values=["No", "Yes"], value=[0],
                 max_width=37, max_height=2, relx=40, use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wStorage_engine", max_height=4, name="Engine: ", value=[0],
                 values=mysql_engine_list, relx=40, max_width=35)

        self.nextrely += 1  # Move down
        self.add(AddFieldButton, name="Add Field", relx=40, max_width=13)
        self.add(CreateTableButton, name="Create Table", relx=40, max_width=13)

    def on_ok(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")

    def on_cancel(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")


class QueryWindow(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=15)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=25)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=34)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=45)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1,
                                 relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the QUERY window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


class RawSQLWindow(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=15)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=25)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=34)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=45)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.nextrely += 1  # Move down
        self.add(npyscreen.MultiLineEditableBoxed, w_id="wSQL_command", name="Enter SQL Command", max_height=6,
                 max_width=75, edit=True, scroll_exit=True)

        self.add(SQLButton, w_id="wSQLButton", name="Send Command", relx=34)
        self.nextrely += 1  # Move down

        self.add(npyscreen.BoxTitle, w_id="wSQLresults_box", name="SQL Results", values=self.parentApp.sql_results,
                 max_width=75, max_height=11, scroll_exit=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


class ExportWindow(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=15)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=25)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=34)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=45)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the EXPORT window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


class AdminWindow(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = (None,)*7

    def create(self):
        self.tabDatabases = self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                     rely=1)
        self.tabTables = self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                  relx=15)
        self.tabQuery = self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1, relx=25)
        self.tabRawSQL = self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                  relx=34)
        self.tabExport = self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                  relx=45)
        self.tabAdmin = self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the ADMIN window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


class ExitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=2)
        if exiting:
            self.parent.parentApp.switchForm(None)
        else:
            # Clears the notification and just goes back to the original form
            npyscreen.blank_terminal()
        return


class OpenDBButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        self.parent.parentApp.dbms.connect_database(self.parent.parentApp.active_db)
        self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()

        self.parent.parentApp.switchForm("TablesWindow")
        return self.parent.parentApp.tableList


class CreateDBButton(npyscreen.ButtonPress):
    newDB_name = None

    def whenPressed(self):
        self.newDB_name = self.parent.get_widget("wNewDB_name").value
        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " + str(self.newDB_name) + "?",
                                                 "Confirm Creation", editw=2)
        if create_confirm:
            servermsg = self.parent.parentApp.dbms.create_database(self.newDB_name)
            npyscreen.notify_confirm(servermsg)
            self.parent.parentApp.switchForm("DatabaseWindow")
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        self.parent.get_widget("wActiveDB").display()


class DeleteDBButton(npyscreen.ButtonPress):
    def whenPressed(self):
        # self.parent.parentApp.dbms.connect_database()
        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " +
                                                 str(self.parent.parentApp.active_db) +
                                                 "?", "Confirm Deletion", editw=2)
        if delete_confirm:
            servermsg = self.parent.parentApp.dbms.delete_database(self.parent.parentApp.active_db)
            npyscreen.notify_confirm(servermsg)
            self.parent.parentApp.switchForm("DatabaseWindow")
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        self.parent.get_widget("wActiveDB").display()


class ViewTableStructButton(npyscreen.ButtonPress):
    selected_table, results = (None,)*2

    def whenPressed(self):
        if self.parent.get_widget("wTables_box").value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.get_widget("wTables_box").value]
            self.results = self.parent.parentApp.dbms.view_table_struct(self.selected_table)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))

        elif self.results[0] == 'success':
            self.parent.parentApp.table_results = self.results[1]
            self.parent.parentApp.switchForm("TablesWindow")
            return


class BrowseTableButton(npyscreen.ButtonPress):
    selected_table, results = (None,)*2

    def whenPressed(self):
        if self.parent.get_widget("wTables_box").value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.get_widget("wTables_box").value]
            self.results = self.parent.parentApp.dbms.browse_table(self.selected_table)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))

        elif self.results[0] == 'success':
            self.parent.parentApp.table_results = self.results[1]
            self.parent.parentApp.switchForm("TablesWindow")
            return


class BuildTableButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.get_widget("wNewTable_name").value == '':
            npyscreen.notify_confirm("Please enter the name of the table to be created first")
            return

        else:
            self.parent.parentApp.table_name = self.parent.get_widget("wNewTable_name").value

            if self.parent.parentApp.dbtype == 0:
                self.parent.parentApp.switchForm("TableCreatePostgreSQLForm")
            elif self.parent.parentApp.dbtype == 1:
                self.parent.parentApp.switchForm("TableCreateMySQLForm")


class AddFieldButton(npyscreen.ButtonPress):
    field_string, field_name, field_type, collation, constraint, not_null, default = (None,)*7

    def whenPressed(self):
        self.field_string = ""

        self.field_name = self.parent.get_widget("wField_name").value
        self.field_type = self.parent.get_widget("wField_type").get_selected_objects()[0]

        if self.parent.get_widget("wField_length_or_val").value:
            self.field_type += "("
            self.field_type += str(self.parent.get_widget("wField_length_or_val").value)
            self.field_type += ")"

        self.field_string += (self.field_name + " " + self.field_type)

        if self.parent.get_widget("wCollation").get_selected_objects()[0] is not None:
            self.collation = "COLLATE '" + str(self.parent.get_widget("wCollation").get_selected_objects()[0]) + "'"
            self.field_string += (" " + self.collation)

        if self.parent.get_widget("wConstraint").get_selected_objects()[0] is not None:
            self.constraint = self.parent.get_widget("wConstraint").get_selected_objects()[0]
            self.field_string += (" " + self.constraint)

        if self.parent.get_widget("wNot_null").value[0] == 1:
            self.not_null = "NOT NULL"
        else:
            self.not_null = "NULL"

        self.field_string += (" " + self.not_null)

        if self.parent.get_widget("wDefault").value:
            self.default = "DEFAULT '" + str(self.parent.get_widget("wDefault").value) + "'"
            self.field_string += (" " + self.default)

        add_confirm = npyscreen.notify_yes_no("Add the following field?\n" + self.field_string, editw=2)
        if add_confirm:
            self.parent.parentApp.field_string_array.append(self.field_string + ", ")
            self.parent.parentApp.switchForm("TableCreatePostgreSQLForm")

        else:
            return


class CreateTableButton(npyscreen.ButtonPress):
    results = None

    def whenPressed(self):
        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " +
                                                 str(self.parent.parentApp.table_name) + "?", "Confirm Creation",
                                                 editw=2)

        if create_confirm:
            create_table_string = "CREATE TABLE {} ".format(self.parent.parentApp.table_name) + "("
            for field in self.parent.parentApp.field_string_array:
                create_table_string += field
            create_table_string = create_table_string[:-2]
            create_table_string += ")"

            #npyscreen.notify_confirm(create_table_string)

            self.results = self.parent.parentApp.dbms.execute_SQL(create_table_string)

            if self.results[0] == 'error':
                if self.results[1] == 'no results to fetch':
                    npyscreen.notify_confirm("Table {} successfully created".format(self.parent.parentApp.table_name))

                else:
                    npyscreen.notify_confirm(str(self.results[1]))
                    self.parent.parentApp.field_string_array = []
                    return

            elif self.results[0] == 'success':
                npyscreen.notify_confirm("Table {} successfully created".format(self.parent.parentApp.table_name))

            self.parent.parentApp.field_string_array = []
            self.parent.parentApp.table_results = []
            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()

            self.parent.parentApp.switchForm("TablesWindow")

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class DeleteTableButton(npyscreen.ButtonPress):
    selected_table = None

    def whenPressed(self):
        if self.parent.get_widget("wTables_box").value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.get_widget("wTables_box").value]

        delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(self.selected_table) + "?",
                                                 "Confirm Deletion", editw=2)
        if delete_confirm:
            servermsg = self.parent.parentApp.dbms.delete_table(self.selected_table)
            if servermsg:
                npyscreen.notify_confirm(servermsg)

            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()
            self.parent.parentApp.switchForm("TablesWindow")
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class SQLButton(npyscreen.ButtonPress):
    sql_command, results = (None,)*2

    def whenPressed(self):
        self.sql_command = self.parent.get_widget("wSQL_command").values[0]
        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_command)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))

        elif self.results[0] == 'success':
            self.parent.parentApp.sql_results = self.results[1]
            self.parent.parentApp.switchForm("RawSQLWindow")
            return


class TabDatabaseButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("DatabaseWindow")
        return


class TabTablesButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.parentApp.active_db is None:
            npyscreen.notify_confirm("You must first open a database before accessing the Tables view")
            return

        else:
            self.parent.parentApp.switchForm("TablesWindow")


class TabQueryButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryWindow")
        return


class TabRawSQLButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("RawSQLWindow")
        return


class TabExportButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("ExportWindow")
        return


class TabAdminButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("AdminWindow")
        return

#for testing
class Nav_Bar(npyscreen.Form):

    def create(self):

            self.add(TabDatabaseButton, w_id="wDatabaseTab", name="Databases", value="DatabaseWindow",
                                 rely=1, max_height=1, scroll_exit=True)
            self.add(TabTablesButton, w_id="wTablesTab", name="Tables", value="TablesWindow", rely=1,
                                      relx=15, max_height=1)
            self.add(TabQueryButton, w_id="wQueryTab", name="Query", value="QueryWindow", rely=1,
                                     relx=25, max_height=1)
            self.add(TabRawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQLWindow", rely=1,
                                      relx=34, max_height=1)
            self.add(TabExportButton, w_id="wExportTab", name="Export", value="ExportWindow", rely=1,
                                      relx=45, max_height=1)
            self.add(TabAdminButton, w_id="wAdminTab", name="Admin", value="AdminWindow", rely=1,
                                     relx=55, max_height=1)
            self.add(ExitButton, name="Exit", rely=1, relx=64, max_height=1)


# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):
    dbtype, host, port, username, password, dbms, active_db, tableList, active_table = (None,)*9

    # Table creation global variables
    field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = (None,)*6

    field_autoincrement, field_primarykey, field_unique, field_index = (False,)*4
    # User friendly way of saying if Null is okay for this field
    field_optional = True

    tablefield_cols, sql_results, table_results, table_struct_results, field_string_array = ([],)*5

    def onStart(self):
        # Declare all the forms that will be used within the app
        self.addFormClass("MAIN", Initial, name="Welcome to ezdb")
        self.addFormClass("ConnectDBMS", ConnectDBMS, name="ezdb >> DBMS Connection Page")
        self.addFormClass("DatabaseWindow", DatabaseWindow, name="ezdb >> Database Page")
        self.addFormClass("TablesWindow", TablesWindow, name="ezdb >> Tables Page")
        self.addFormClass("QueryWindow", QueryWindow, name="ezdb >> Query Page")
        self.addFormClass("RawSQLWindow", RawSQLWindow, name="ezdb >> Raw SQL Page")
        self.addFormClass("ExportWindow", ExportWindow, name="ezdb >> Export Page")
        self.addFormClass("AdminWindow", AdminWindow, name="ezdb >> Admin Page")
        self.addFormClass("TableCreatePostgreSQLForm", TableCreatePostgreSQLForm, name="ezdb >> Build/Create Table")
        self.addFormClass("TableCreateMySQLForm", TableCreateMySQLForm, name="ezdb >> Build/Create Table")
        # for testing:
        # self.addForm("Nav_Bar", Nav_Bar)

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()
