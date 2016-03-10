#!/usr/bin/env python

import npyscreen
import postgres_db as pdb
import mysql_db as mdb
import time
import math

# ActionForm includes "Cancel" in addition to "OK"
class Initial(npyscreen.ActionForm, npyscreen.SplitForm):
    sessionType, db = None, None

    def create(self):
        # Title text
        self.nextrely += 5  # Move down
        self.nextrelx += 45  # Move right (centered))
        self.add(npyscreen.FixedText, value="                _  _     ", editable=False)
        self.add(npyscreen.FixedText, value="               | || |    ", editable=False)
        self.add(npyscreen.FixedText, value="  ___  ____  __| || |__  ", editable=False)
        self.add(npyscreen.FixedText, value=" / _ \|_  / / _` || '_ \ ", editable=False)
        self.add(npyscreen.FixedText, value="|  __/ / / | (_| || |_) |", editable=False)
        self.add(npyscreen.FixedText, value=" \___|/___| \__,_||_.__/ ", editable=False)

        # Add session options and save the selected value
        self.nextrely += 4  # Move down
        self.nextrelx += 2  # Move right (centered)
        self.add(npyscreen.FixedText, value="Choose Database Type:", editable=False)
        self.db = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["postgreSQL", "MySQL"],
                           scroll_exit=True)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

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


class ConnectDBMS(npyscreen.ActionForm, npyscreen.SplitForm):
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

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

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


class DatabaseWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True, color="VERYGOOD")

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45)

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.dbList = self.parentApp.dbms.list_databases()

        self.nextrely += 1  # Move down

        if self.parentApp.dbtype == 0:
            self.dbtype_str = "PostgreSQL"
        elif self.parentApp.dbtype == 1:
            self.dbtype_str = "MySQL"

        self.db_box = self.add(npyscreen.BoxTitle, w_id="wDatabases_box", name="{} Databases".format(self.dbtype_str),
                 values=self.parentApp.dbms.list_databases(), max_width=30, max_height=17, scroll_exit=True)

        # Database button options
        self.nextrely += 1  # Move down
        self.add(OpenDBButton, name="Open Database")

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewDB_name", name="New Database Name:", relx=4,
                 begin_entry_at=22, use_two_lines=False)

        self.add(CreateDBButton, name="Create")

        self.nextrely += 1  # Move down
        self.add(DeleteDBButton, name="Delete Database")

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Select an available database instance from the list, and choose \"Open Database\" to begin " \
                   "interaction. If no instances are available, create a new one or contact your database administer."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class TablesWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31,
                 color="VERYGOOD")

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45)

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.nextrely += 1  # Move down
        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), relx=3, color="VERYGOOD",
                 editable=False)

        self.nextrely += 1  # Move down
        self.tablebox = self.add(npyscreen.BoxTitle, w_id="wTables_box", name="Tables", values=self.parentApp.tableList,
                                 max_width=25, max_height=11, scroll_exit=True)

        self.nextrely += 1  # Move down
        self.add(BrowseTableButton, name="Browse Table", rely=6, relx=30, max_width=12)

        self.nextrely += 1  # Move down
        self.add(ViewTableStructButton, name="View Table Structure", relx=30, max_width=22)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewTable_name", name="New Table Name:",
                 relx=32, max_width=35, use_two_lines=False)

        self.add(BuildTableButton, name="Build", relx=30, max_width=35)

        self.nextrely += 1  # Move down
        self.add(DeleteTableButton, name="Delete Table", relx=30, max_width=35)

        self.nextrely += 3  # Move down

        self.gridbox_results = self.add(Grid_Box_Results, max_height=14, values=self.parentApp.query_results,
                                        default_column_number=10, w_id="wGrid_Box_Results",
                                        contained_widget_arguments = {"col_titles": self.parentApp.col_titles},
                                        col_margin=1, column_width=20, name="Table Results")

        self.numrecords = self.add(npyscreen.FixedText, value="{} Records Found".format(self.parentApp.num_records),
                                   relx=4, rely=31, max_width=20, editable=False)

        self.numpages = self.add(npyscreen.FixedText,
                                 value="Page {} of {}".format(self.parentApp.page_num, self.parentApp.num_pages),
                                 relx=51, rely=31, editable=False, max_width=17, hidden=True)

        self.prevpage = self.add(PrevPage_Button, name="Prev Page", rely=31, relx=90, max_width=9, hidden=True)
        self.nextpage = self.add(NextPage_Button, name="Next Page", rely=31, relx=103, max_width=9, hidden=True)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Select an available table from the list and choose \"View Table Structure\" to view the table's " \
                   "fields and their associated constraints. Similarly, you can select a table and choose " \
                   "\"Browse Table\" to view rows (data) within the table. To define and add a new table to the " \
                   "current database instance, specify a name for the new table and choose \"Build\". Choosing " \
                   "\"Delete Table\" will permanently remove the currently selected table and all of its contents " \
                   "from the database instance."
        npyscreen.notify_confirm(help_msg, title='Help Menu')

    # PEP8 Ignore (external library naming convention)
    def beforeEditing(self):

        # init page values
        self.parentApp.row_start = 1  #sets the start row range
        self.parentApp.row_end = 10  #sets the end row range
        self.parentApp.per_page = 10  #sets the number of rows displayed per page result
        self.parentApp.page_num = 1
        self.parentApp.num_pages = 0

        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.tablebox.display()

        # clear grid widget results and num records on page load
        self.parentApp.col_titles = []
        self.gridbox_results.entry_widget.col_titles = self.parentApp.col_titles
        self.parentApp.query_results = []
        self.gridbox_results.values = self.parentApp.query_results
        self.gridbox_results.display()

        self.parentApp.num_records = 0
        self.numrecords.value = "{} Records Found".format(self.parentApp.num_records)
        self.numrecords.display()

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class TableCreatePostgreSQLForm(npyscreen.ActionForm, npyscreen.SplitForm):

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

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Enter in a name for a field (column) you would like to add to the new table. Choose a field " \
                   "type for the type of information you would like the field to contain, for example \"VARCHAR\" " \
                    "for text strings or  \"INT\" for integers. Add constraints as desired, for example " \
                   "\"REQUIRED\" means a row cannot be added with a blank entry for field, and \"PRIMARY KEY\" marks" \
                   "the data in this field as the primary key for references to this table. Finally, you can add " \
                   "additional fields as needed before creating the table, or if you're ready to create, choose " \
                   "\"CREATE TABLE\"."

        npyscreen.notify_confirm(help_msg, title='Help Menu')

    def on_ok(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")

    def on_cancel(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")


class TableCreateMySQLForm(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):
        mysql_field_type_list = ['CHAR','VARCHAR','TINYTEXT','TEXT','MEDIUMTEXT','LONGTEXT',
                                 'TINYINT','SMALLINT','MEDIUMINT','INT','BIGINT','FLOAT','DOUBLE',
                                 'DECIMAL','NUMERIC', 'REAL','DATE','DATETIME','TIMESTAMP','TIME','YEAR',
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

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Enter in a name for a field (column) you would like to add to the new table. Choose a field " \
                   "type for the type of information you would like the field to contain, for example \"VARCHAR\" " \
                    "for text strings or  \"INT\" for integers. Add constraints as desired, for example " \
                   "\"REQUIRED\" means a row cannot be added with a blank entry for field, and \"PRIMARY KEY\" marks" \
                   "the data in this field as the primary key for references to this table. Finally, you can add " \
                   "additional fields as needed before creating the table, or if you're ready to create, choose " \
                   "\"CREATE TABLE\"."
        npyscreen.notify_confirm(help_msg, title='Help Menu')

    def on_ok(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")

    def on_cancel(self):
        self.parentApp.field_string_array = []
        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()
        self.parentApp.setNextForm("TablesWindow")


class QueryWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    # Data structure for managing user input for each table column

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45, color="VERYGOOD")

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), rely=3, relx=3,
                 color="LABEL", editable=False)

        # Sub-nav for action type

        self.add(QuerySelectBtn, name="SELECT", value="QueryWindow", color="VERYGOOD", rely=3, relx=37)

        self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow", rely=3, relx=49)

        self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow", rely=3, relx=61)

        self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow", rely=3, relx=73)

        #label variables for selected table/fields
        self.table1_selected, self.table2_selected, self.table3_selected, self.field1_selected, \
        self.field2_selected, self.field3_selected = (None,)*6

        self.nextrely += 1  # Move down

        ''' TABLE 1 COLUMN '''
        self.nextrelx = 3  # Padding
        self.add(QB_TableBox01, name="Tables", values=self.parentApp.tableList, max_width=22, max_height=7,
                 scroll_exit=True)

        self.label_table1 = self.add(npyscreen.FixedText, w_id="wLabel_table1_selected", value="None",
                 relx=4, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field_box1 = self.add(QB_FieldBox01, w_id="wField_list1", name="Fields", values=self.parentApp.field_list1,
                                   max_width=22, max_height=6, scroll_exit=True)

        self.label_field1 = self.add(npyscreen.FixedText, w_id="wLabel_field1_selected", value="None",
                 relx=4, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.tbl1_criteria1 = self.add(npyscreen.TitleText, w_id="wTbl1_criteria1", name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.condition1 = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl1_criteria2 = self.add(npyscreen.TitleText, w_id="wTbl1_Criteria2", name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.condition2 = self.add(npyscreen.SelectOne, max_height=2, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.tbl1_criteria3 = self.add(npyscreen.TitleText, w_id="wTbl1_Criteria3", name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.tbl1_sort = self.add(npyscreen.SelectOne, max_height=3, value=[0], max_width=14,
                                  values=["NO SORT", "ASC", "DESC"], scroll_exit=True)

        ''' TABLE 2 COLUMN '''
        self.nextrely = 5

        self.add(QB_TableBox02, name="Tables", values=self.parentApp.tableList, relx=30, max_width=22, max_height=7,
                 scroll_exit=True)

        self.label_table2 = self.add(npyscreen.FixedText, w_id="wLabel_table2_selected", value="None",
                 relx=31, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field_box2 = self.add(QB_FieldBox02, w_id="wField_list2", name="Fields", values=self.parentApp.field_list2,
                                   relx=30, max_width=22, max_height=6, scroll_exit=True)

        self.label_field2 = self.add(npyscreen.FixedText, w_id="wLabel_field2_selected", value="None",
                 relx=31, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.tbl2_criteria1 = self.add(npyscreen.TitleText, w_id="wCriteria1", relx=30, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.tbl2_criteria2 = self.add(npyscreen.TitleText, w_id="wCriteria2", relx=30, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.tbl2_criteria3 = self.add(npyscreen.TitleText, w_id="wCriteria3", relx=30, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.tbl2_sort = self.add(npyscreen.SelectOne, max_height=3, relx=30, value=[0], max_width=14,
                                  values=["NO SORT", "ASC", "DESC"], scroll_exit=True)

        ''' TABLE 3 COLUMN '''
        self.nextrely = 5

        self.add(QB_TableBox03, name="Tables", values=self.parentApp.tableList, relx=57, max_width=22, max_height=7,
                 scroll_exit=True)

        self.label_table3 = self.add(npyscreen.FixedText, w_id="wLabel_table3_selected", value="None",
                 relx=58, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field_box3 = self.add(QB_FieldBox03, w_id="wField_list3", name="Fields", values=self.parentApp.field_list3,
                                   relx=57, max_width=22, max_height=6, scroll_exit=True)

        self.label_field3 = self.add(npyscreen.FixedText, w_id="wLabel_field3_selected", value="None",
                 relx=58, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.tbl3_criteria1 = self.add(npyscreen.TitleText, w_id="wCriteria1", relx=57, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.tbl3_criteria2 = self.add(npyscreen.TitleText, w_id="wCriteria2", relx=57, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.tbl3_criteria3 = self.add(npyscreen.TitleText, w_id="wCriteria3", relx=57, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.tbl3_sort = self.add(npyscreen.SelectOne, max_height=3, relx=57, value=[0], max_width=14,
                                  values=["NO SORT", "ASC", "DESC"], scroll_exit=True)

        self.nextrely = 5
        self.query_box = self.add(Boxed_SQL_Query, name="SQL Query", w_id="wSQL_query", relx=84, max_height=22, max_width=33,
                 editable=True, scroll_exit=True)

        self.nextrely += 1
        self.add(QB_SQL_Build_Button, w_id="wSQL_Build_Button", relx=93, max_width=12, name="Build Query")
        self.nextrely += 1
        self.add(QB_SQL_Send_Button, w_id="wSQL_Send_Button", relx=93, max_width=12, name="Send Query")

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the SELECT form to query the database for stored data."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryInsertWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45, color="VERYGOOD")

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), rely=3, relx=3,
                 color="LABEL", editable=False)

        # Sub-nav for action type

        self.add(QuerySelectBtn, name="SELECT", value="QueryWindow", rely=3, relx=37)

        self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow", rely=3, relx=49, color="VERYGOOD")

        self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow", rely=3, relx=61)

        self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow", rely=3, relx=73)

        self.add(QB_InsertTableBox, name="Select Table", values=self.parentApp.tableList, max_width=30, max_height=22,
                 relx=3, rely=6, scroll_exit=True)

        self.insertfield_box = self.add(QB_InsertFieldBox, w_id="wInsertField_list", name="Choose Fields: ",
                                        max_width=30, max_height=22,
                                        contained_widget_arguments={"values": ""},
                                        relx=36, rely=6, scroll_exit=True)

        self.add(QueryInsert_LoadFieldsButton, name="Load Fields", relx=44, rely=29, max_width=12)

        self.label_field01 = self.add(npyscreen.FixedText, value="", relx=70, rely=7, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field02 = self.add(npyscreen.FixedText, value="", relx=70, rely=8, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field03 = self.add(npyscreen.FixedText, value="", relx=70, rely=9, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field04 = self.add(npyscreen.FixedText, value="", relx=70, rely=10, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field05 = self.add(npyscreen.FixedText, value="", relx=70, rely=11, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field06 = self.add(npyscreen.FixedText, value="", relx=70, rely=12, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field07 = self.add(npyscreen.FixedText, value="", relx=70, rely=13, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field08 = self.add(npyscreen.FixedText, value="", relx=70, rely=14, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field09 = self.add(npyscreen.FixedText, value="", relx=70, rely=15, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field10 = self.add(npyscreen.FixedText, value="", relx=70, rely=16, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field11 = self.add(npyscreen.FixedText, value="", relx=70, rely=17, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field12 = self.add(npyscreen.FixedText, value="", relx=70, rely=18, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field13 = self.add(npyscreen.FixedText, value="", relx=70, rely=19, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field14 = self.add(npyscreen.FixedText, value="", relx=70, rely=20, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field15 = self.add(npyscreen.FixedText, value="", relx=70, rely=21, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field16 = self.add(npyscreen.FixedText, value="", relx=70, rely=22, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field17 = self.add(npyscreen.FixedText, value="", relx=70, rely=23, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field18 = self.add(npyscreen.FixedText, value="", relx=70, rely=24, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field19 = self.add(npyscreen.FixedText, value="", relx=70, rely=25, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field20 = self.add(npyscreen.FixedText, value="", relx=70, rely=26, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.insertfield01 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=7, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield02 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=8, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield03 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=9, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield04 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=10, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield05 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=11, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield06 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=12, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield07 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=13, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield08 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=14, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield09 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=15, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield10 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=16, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield11 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=17, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield12 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=18, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield13 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=19, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield14 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=20, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield15 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=21, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield16 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=22, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield17 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=23, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield18 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=24, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield19 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=25, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.insertfield20 = self.add(npyscreen.TitleText, name=" ", relx=87, rely=26, max_width=30, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.add(QueryInsertButton, name="Insert Values", relx=84, rely=29, max_width=12)

    def beforeEditing(self):

        self.parentApp.tableList = self.parentApp.dbms.list_database_tables()

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the INSERT form to add rows to the database."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryUpdateWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45, color="VERYGOOD")

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), rely=3, relx=3,
                 color="LABEL", editable=False)

        # Sub-nav for action type

        self.add(QuerySelectBtn, name="SELECT", value="QueryWindow", rely=3, relx=37)

        self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow", rely=3, relx=49)

        self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow", rely=3, relx=61, color="VERYGOOD")

        self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow", rely=3, relx=73)

        self.nextrely += 1  # Move down

        ''' TABLE '''

        self.add(QBUpdate_TableBox, name="Tables", values=self.parentApp.tableList, max_width=25, max_height=8,
                 relx=14, rely=5, scroll_exit=True)

        self.label_table = self.add(npyscreen.FixedText, value="Unselected", relx=15,
                                    rely=13, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)


        ''' FIELD CHOOSER BOX '''
        self.updatefield_box = self.add(QB_UpdateFieldBox, name="Choose Fields",
                                        max_width=25, max_height=8,
                                        contained_widget_arguments={"values": ""},
                                        relx=41, rely=5, scroll_exit=True)

        ''' FIELD CRITERIA 1 COLUMN '''

        self.field_box1 = self.add(QB_FieldBox01, name="Criteria", values=self.parentApp.field_list1,
                                   relx=3, rely=15, max_width=20, max_height=9, scroll_exit=True)

        self.label_field1 = self.add(npyscreen.FixedText, value="Unselected", relx=4,
                                     rely=24, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field1_criteria1 = self.add(npyscreen.TitleText, name="Criteria:", max_width=25, relx=3,
                                       use_two_lines=False, begin_entry_at=10)

        self.condition1 = self.add(npyscreen.SelectOne, max_height=2, relx=3, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.field1_criteria2 = self.add(npyscreen.TitleText, name="Criteria:", relx=3, max_width=25,
                                       use_two_lines=False, begin_entry_at=10)

        self.condition2 = self.add(npyscreen.SelectOne, max_height=2, relx=3, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.field1_criteria3 = self.add(npyscreen.TitleText, name="Criteria:", max_width=25, relx=3,
                                       use_two_lines=False, begin_entry_at=10)

        ''' FIELD CRITERIA 2 COLUMN '''

        self.field_box2 = self.add(QB_FieldBox02, name="Criteria", values=self.parentApp.field_list2,
                                   relx=30, rely=15, max_width=20, max_height=9, scroll_exit=True)

        self.label_field2 = self.add(npyscreen.FixedText, value="Unselected", relx=31,
                                     rely=24, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field2_criteria1 = self.add(npyscreen.TitleText, relx=30, name="Criteria:", max_width=25,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field2_criteria2 = self.add(npyscreen.TitleText, relx=30, name="Criteria:", max_width=25,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field2_criteria3 = self.add(npyscreen.TitleText, relx=30, name="Criteria:", max_width=25,
                                       use_two_lines=False, begin_entry_at=10)

        ''' FIELD CRITERIA 3 COLUMN '''

        self.field_box3 = self.add(QB_FieldBox03, name="Criteria", values=self.parentApp.field_list3,
                                   relx=57, rely=15, max_width=20, max_height=9, scroll_exit=True)

        self.label_field3 = self.add(npyscreen.FixedText, value="Unselected", relx=58, rely=24,
                                     max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field3_criteria1 = self.add(npyscreen.TitleText, relx=57, name="Criteria:", max_width=25,
                                         use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field3_criteria2 = self.add(npyscreen.TitleText, relx=57, name="Criteria:", max_width=25,
                                         use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field3_criteria3 = self.add(npyscreen.TitleText, relx=57, name="Criteria:", max_width=25,
                                         use_two_lines=False, begin_entry_at=10)

        self.add(QueryUpdate_LoadFieldsButton, name="Load Fields", relx=84, rely=29, max_width=12)
        self.add(QBUpdate_Button, relx=84, rely=31, max_width=12, name="Update Values")

        self.label_field01 = self.add(npyscreen.FixedText, value="", relx=79, rely=7, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field02 = self.add(npyscreen.FixedText, value="", relx=79, rely=8, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field03 = self.add(npyscreen.FixedText, value="", relx=79, rely=9, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field04 = self.add(npyscreen.FixedText, value="", relx=79, rely=10, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field05 = self.add(npyscreen.FixedText, value="", relx=79, rely=11, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field06 = self.add(npyscreen.FixedText, value="", relx=79, rely=12, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field07 = self.add(npyscreen.FixedText, value="", relx=79, rely=13, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field08 = self.add(npyscreen.FixedText, value="", relx=79, rely=14, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field09 = self.add(npyscreen.FixedText, value="", relx=79, rely=15, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field10 = self.add(npyscreen.FixedText, value="", relx=79, rely=16, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field11 = self.add(npyscreen.FixedText, value="", relx=79, rely=17, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field12 = self.add(npyscreen.FixedText, value="", relx=79, rely=18, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field13 = self.add(npyscreen.FixedText, value="", relx=79, rely=19, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field14 = self.add(npyscreen.FixedText, value="", relx=79, rely=20, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field15 = self.add(npyscreen.FixedText, value="", relx=79, rely=21, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field16 = self.add(npyscreen.FixedText, value="", relx=79, rely=22, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field17 = self.add(npyscreen.FixedText, value="", relx=79, rely=23, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field18 = self.add(npyscreen.FixedText, value="", relx=79, rely=24, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field19 = self.add(npyscreen.FixedText, value="", relx=79, rely=25, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.label_field20 = self.add(npyscreen.FixedText, value="", relx=79, rely=26, max_width=15, color="LABEL",
                                      hidden=True, editable=False)

        self.updatefield01 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=7, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield02 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=8, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield03 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=9, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield04 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=10, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield05 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=11, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield06 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=12, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield07 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=13, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield08 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=14, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield09 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=15, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield10 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=16, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield11 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=17, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield12 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=18, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield13 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=19, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield14 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=20, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield15 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=21, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield16 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=22, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield17 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=23, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield18 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=24, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield19 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=25, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        self.updatefield20 = self.add(npyscreen.TitleText, name=" ", relx=96, rely=26, max_width=20, begin_entry_at=1,
                                      use_two_lines=False, hidden=True)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the UPDATE form to update a row in the database."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryDeleteWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45, color="VERYGOOD")

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), rely=3, relx=3,
                 color="LABEL", editable=False)

        # Sub-nav for action type

        self.add(QuerySelectBtn, name="SELECT", value="QueryWindow", rely=3, relx=37)

        self.add(QueryInsertBtn, name="INSERT", value="QueryInsertWindow", rely=3, relx=49)

        self.add(QueryUpdateBtn, name="UPDATE", value="QueryUpdateWindow", rely=3, relx=61)

        self.add(QueryDeleteBtn, name="DELETE", value="QueryDeleteWindow", color="VERYGOOD", rely=3, relx=73)

        #label variables for selected table/fields
        self.table1_selected, self.table2_selected, self.table3_selected, self.field1_selected, \
        self.field2_selected, self.field3_selected = (None,)*6

        self.nextrely += 1  # Move down

        ''' TABLE '''

        self.add(QBDelete_TableBox, name="Tables", values=self.parentApp.tableList, max_width=22, max_height=26,
                 relx=3, rely=5, scroll_exit=True)

        self.label_table = self.add(npyscreen.FixedText, value="Unselected", relx=4,
                                    rely=31, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)


        ''' FIELD 1 COLUMN '''

        self.field_box1 = self.add(QB_FieldBox01, name="Fields", values=self.parentApp.field_list1,
                                   relx=28, rely=5, max_width=22, max_height=17, scroll_exit=True)

        self.label_field1 = self.add(npyscreen.FixedText, value="Unselected", relx=29,
                                     rely=22, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field1_criteria1 = self.add(npyscreen.TitleText, name="Criteria:", max_width=28, relx=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.condition1 = self.add(npyscreen.SelectOne, max_height=2, relx=28, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.field1_criteria2 = self.add(npyscreen.TitleText, name="Criteria:", relx=28, max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.condition2 = self.add(npyscreen.SelectOne, max_height=2, relx=28, value=[0], values=["AND", "OR"],
                                        scroll_exit=True, max_width=10)

        self.field1_criteria3 = self.add(npyscreen.TitleText, name="Criteria:", max_width=28, relx=28,
                                       use_two_lines=False, begin_entry_at=10)

        ''' FIELD 2 COLUMN '''

        self.field_box2 = self.add(QB_FieldBox02, name="Fields", values=self.parentApp.field_list2,
                                   relx=55, rely=5, max_width=22, max_height=17, scroll_exit=True)

        self.label_field2 = self.add(npyscreen.FixedText, value="Unselected", relx=56,
                                     rely=22, max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field2_criteria1 = self.add(npyscreen.TitleText, relx=55, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field2_criteria2 = self.add(npyscreen.TitleText, relx=55, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field2_criteria3 = self.add(npyscreen.TitleText, relx=55, name="Criteria:", max_width=28,
                                       use_two_lines=False, begin_entry_at=10)

        ''' FIELD 3 COLUMN '''

        self.field_box3 = self.add(QB_FieldBox03, name="Fields", values=self.parentApp.field_list3,
                                   relx=82, rely=5, max_width=22, max_height=17, scroll_exit=True)

        self.label_field3 = self.add(npyscreen.FixedText, value="Unselected", relx=83, rely=22,
                                     max_width=20, color="CURSOR_INVERSE", use_two_lines=False, editable=False)

        self.nextrely += 1  # Move down
        self.field3_criteria1 = self.add(npyscreen.TitleText, relx=82, name="Criteria:", max_width=28,
                                         use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field3_criteria2 = self.add(npyscreen.TitleText, relx=82, name="Criteria:", max_width=28,
                                         use_two_lines=False, begin_entry_at=10)

        self.nextrely += 2  # Move down

        self.field3_criteria3 = self.add(npyscreen.TitleText, relx=82, name="Criteria:", max_width=28,
                                         use_two_lines=False, begin_entry_at=10)

        self.nextrely += 1  # Move down
        self.add(QBDelete_Button, w_id="wDelete_Button", relx=55, max_width=12, name="Delete")

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use the DELETE form to delete rows from the database using the specified criteria.\n" \
                   "The criteria statements are executed left to right on each criteria row with an assumed\n" \
                   "AND operator. The AND/OR operators you specify apply to connect each criteria row to form\n" \
                   "the full delete query.\n\n" \
                   "Note: You must enclose criteria values within single quotes (e.g. LIKE '%Bi' or ='Tom')\n" \
                   "Also, criteria values are case sensitive."
        npyscreen.notify_confirm(help_msg, title='Help Menu')


class QueryResultsWindow(npyscreen.ActionFormMinimal, npyscreen.SplitForm):

    def create(self):

        self.gridbox_results = self.add(Grid_Box_Results, max_height=29, values=self.parentApp.query_results,
                                        default_column_number=10,
                                        contained_widget_arguments={"col_titles":self.parentApp.col_titles},
                                        col_margin=1, column_width=12,
                                        name="SQL Results")

        self.numrecords = self.add(npyscreen.FixedText, value="{} Records Found".format(self.parentApp.num_records),
                                   relx=4, rely=31, max_width=20, editable=False)

        self.numpages = self.add(npyscreen.FixedText,
                                 value="Page {} of {}".format(self.parentApp.page_num, self.parentApp.num_pages),
                                 relx=51, rely=31, editable=False, max_width=17, hidden=True)

        self.prevpage = self.add(PrevPage_Button, name="Prev Page", rely=31, relx=90, max_width=9, hidden=True)
        self.nextpage = self.add(NextPage_Button, name="Next Page", rely=31, relx=103, max_width=9, hidden=True)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Query Builder results page. Select page navigation for viewing complete result. Scroll right to see" \
                   "extended columns."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def beforeEditing(self):

        # init page values
        self.parentApp.row_start = 1  #sets the start row range
        self.parentApp.row_end = 25  #sets the end row range
        self.parentApp.per_page = 25  #sets the number of rows displayed per page result
        self.parentApp.page_num = 1
        self.parentApp.num_pages = 0

        # calculate number of pages (assuming 10 rows per page)
        self.parentApp.num_pages = int(math.ceil(float(self.parentApp.num_records) / self.parentApp.per_page))

        # display up to 25 rows
        self.gridbox_results.values = \
            self.parentApp.query_results[self.parentApp.row_start-1: self.parentApp.row_end]

        # get column titles
        self.gridbox_results.entry_widget.col_titles = self.parentApp.col_titles

        # return number of records found
        self.numrecords.value = "{} Records Found".format(self.parentApp.num_records)

        # if records found, display page num and num pages information, and page control buttons
        if self.parentApp.num_records > 0:

            self.numpages.value = \
                "Page {} of {}".format(self.parentApp.page_num, self.parentApp.num_pages)

            self.numpages.hidden = False
            self.prevpage.hidden = False
            self.nextpage.hidden = False

        # no records found, so hide page num and num pages information, and page control buttons
        else:
            self.numpages.hidden = True
            self.prevpage.hidden = True
            self.nextpage.hidden = True

    def on_ok(self):
        self.parentApp.query_results = None
        self.parentApp.num_records = 0

        self.parentApp.switchForm("QueryWindow")


class RawSQLWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45)

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58,
                 color="VERYGOOD")

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.nextrely += 1  # Move down

        self.add(Boxed_SQL_Query, name="Enter SQL Query", w_id="wSQL_query", max_height=7, editable=True,
                 scroll_exit=True)

        self.add(SQL_Send_Button, w_id="wSQL_Send_Button", relx=51, name="Send Query")

        self.nextrely += 2  # Move down

        self.gridbox_results = self.add(Grid_Box_Results, max_height=19, values=self.parentApp.query_results,
                                        default_column_number=10,
                                        contained_widget_arguments={"col_titles":self.parentApp.col_titles},
                                        col_margin=1, column_width=12,
                                        name="SQL Results")


        self.numrecords = self.add(npyscreen.FixedText, value="{} Records Found".format(self.parentApp.num_records),
                                   relx=4, rely=32, max_width=20, editable=False)

        self.numpages = self.add(npyscreen.FixedText,
                                 value="Page {} of {}".format(self.parentApp.page_num, self.parentApp.num_pages),
                                 relx=51, rely=32, editable=False, max_width=17, hidden=True)

        self.prevpage = self.add(PrevPage_Button, name="Prev Page", rely=32, relx=90, max_width=9, hidden=True)
        self.nextpage = self.add(NextPage_Button, name="Next Page", rely=32, relx=103, max_width=9, hidden=True)


        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use this page to enter and submit a raw SQL query without any of form assistance from the " \
                   "Query Builder or Tables pages. Entering raw SQL provides none of the protections that the " \
                   "aforementioned forms offer, and should only be performed by experienced users."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

    def beforeEditing(self):

        #clear grid widget results and num records on page load
        self.parentApp.col_titles = []
        self.gridbox_results.entry_widget.col_titles = self.parentApp.col_titles
        self.parentApp.query_results = []
        self.gridbox_results.values = self.parentApp.query_results
        self.gridbox_results.display()

        self.parentApp.num_records = 0
        self.numrecords.value = "{} Records Found".format(self.parentApp.num_records)
        self.numrecords.display()

    def on_ok(self):
        self.parentApp.query_results = None
        self.parentApp.num_records = 0


class SQL_Query(npyscreen.MultiLineEdit):

    def display_value(self, vl):
        return


class Boxed_SQL_Query(npyscreen.BoxTitle):
    _contained_widget = SQL_Query


class Grid_Results(npyscreen.GridColTitles):

    def __init__(self, *args, **keywords):
        super(Grid_Results, self).__init__(*args, **keywords)


class Grid_Box_Results(npyscreen.BoxTitle):
    _contained_widget = Grid_Results


class QB_TableList01(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_table1.value = act_on_this
        self.parent.label_table1.display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            field_list.append('[ALL]')

            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box1.values = field_list
            self.parent.field_box1.display()
            self.parent.parentApp.table1 = act_on_this

        else:
            npyscreen.notify_confirm(str(results[1]))


class QB_TableList02(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_table2.value = act_on_this
        self.parent.label_table2.display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            field_list.append('[ALL]')
            #npyscreen.notify_confirm("the results returned are :" + str(results[1]))
            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box2.values = field_list
            self.parent.field_box2.display()
            self.parent.parentApp.table2 = act_on_this

        else:
            npyscreen.notify_confirm(results[1])


class QB_TableList03(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_table3.value = act_on_this
        self.parent.label_table3.display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            field_list.append('[ALL]')
            #npyscreen.notify_confirm("the results returned are :" + str(results[1]))
            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box3.values = field_list
            self.parent.field_box3.display()
            self.parent.parentApp.table3 = act_on_this

        else:
            npyscreen.notify_confirm(results[1])


class QB_TableBox01(npyscreen.BoxTitle):
    _contained_widget = QB_TableList01


class QB_TableBox02(npyscreen.BoxTitle):
    _contained_widget = QB_TableList02


class QB_TableBox03(npyscreen.BoxTitle):
    _contained_widget = QB_TableList03


class QB_FieldList01(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_field1.value = act_on_this
        self.parent.label_field1.display()

        self.parent.parentApp.field1 = act_on_this


class QB_FieldList02(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_field2.value = act_on_this
        self.parent.label_field2.display()

        self.parent.parentApp.field2 = act_on_this


class QB_FieldList03(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_field3.value = act_on_this
        self.parent.label_field3.display()

        self.parent.parentApp.field3 = act_on_this


class QB_FieldBox01(npyscreen.BoxTitle):
    _contained_widget = QB_FieldList01


class QB_FieldBox02(npyscreen.BoxTitle):
    _contained_widget = QB_FieldList02


class QB_FieldBox03(npyscreen.BoxTitle):
    _contained_widget = QB_FieldList03


class QB_InsertTableList(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        field_list = []
        self.parent.insertfield_box.value = None
        self.parent.insertfield_box.display()

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            field_list.append('[ALL]')

            for field in results[1]:
                field_list.append(field[0])
            self.parent.insertfield_box.values = field_list
            self.parent.insertfield_box.display()

            self.parent.parentApp.insertTable = act_on_this

        else:
            npyscreen.notify_confirm(str(results[1]))


class QB_InsertTableBox(npyscreen.BoxTitle):
    _contained_widget = QB_InsertTableList


class QB_InsertFieldList(npyscreen.MultiSelect):
    pass


class QB_InsertFieldBox(npyscreen.BoxTitle):
    _contained_widget = QB_InsertFieldList


class QBUpdate_TableList(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        # reset form values on table switch
        field_list = []
        self.parent.label_table.value = act_on_this
        self.parent.label_table.display()

        self.parent.label_field1.value = "Unselected"
        self.parent.label_field2.value = "Unselected"
        self.parent.label_field3.value = "Unselected"
        self.parent.label_field1.display()
        self.parent.label_field2.display()
        self.parent.label_field3.display()

        self.parent.updatefield_box.value = None
        self.parent.updatefield_box.display()

        self.parent.label_field01.hidden = True
        self.parent.updatefield01.hidden = True
        self.parent.label_field01.value = ""
        self.parent.updatefield01.value = None
        self.parent.label_field01.display()
        self.parent.updatefield01.display()

        self.parent.label_field02.hidden = True
        self.parent.updatefield02.hidden = True
        self.parent.label_field02.value = ""
        self.parent.updatefield02.value = None
        self.parent.label_field02.display()
        self.parent.updatefield02.display()

        self.parent.label_field03.hidden = True
        self.parent.updatefield03.hidden = True
        self.parent.label_field03.value = ""
        self.parent.updatefield03.value = None
        self.parent.label_field03.display()
        self.parent.updatefield03.display()

        self.parent.label_field04.hidden = True
        self.parent.updatefield04.hidden = True
        self.parent.label_field04.value = ""
        self.parent.updatefield04.value = None
        self.parent.label_field04.display()
        self.parent.updatefield04.display()

        self.parent.label_field05.hidden = True
        self.parent.updatefield05.hidden = True
        self.parent.label_field05.value = ""
        self.parent.updatefield05.value = None
        self.parent.label_field05.display()
        self.parent.updatefield05.display()

        self.parent.label_field06.hidden = True
        self.parent.updatefield06.hidden = True
        self.parent.label_field06.value = ""
        self.parent.updatefield06.value = None
        self.parent.label_field06.display()
        self.parent.updatefield06.display()

        self.parent.label_field07.hidden = True
        self.parent.updatefield07.hidden = True
        self.parent.label_field07.value = ""
        self.parent.updatefield07.value = None
        self.parent.label_field07.display()
        self.parent.updatefield07.display()

        self.parent.label_field08.hidden = True
        self.parent.updatefield08.hidden = True
        self.parent.label_field08.value = ""
        self.parent.updatefield08.value = None
        self.parent.label_field08.display()
        self.parent.updatefield08.display()

        self.parent.label_field09.hidden = True
        self.parent.updatefield09.hidden = True
        self.parent.label_field09.value = ""
        self.parent.updatefield09.value = None
        self.parent.label_field09.display()
        self.parent.updatefield09.display()

        self.parent.label_field10.hidden = True
        self.parent.updatefield10.hidden = True
        self.parent.label_field10.value = ""
        self.parent.updatefield10.value = None
        self.parent.label_field10.display()
        self.parent.updatefield10.display()

        self.parent.label_field11.hidden = True
        self.parent.updatefield11.hidden = True
        self.parent.label_field11.value = ""
        self.parent.updatefield11.value = None
        self.parent.label_field11.display()
        self.parent.updatefield11.display()

        self.parent.label_field12.hidden = True
        self.parent.updatefield12.hidden = True
        self.parent.label_field12.value = ""
        self.parent.updatefield12.value = None
        self.parent.label_field12.display()
        self.parent.updatefield12.display()

        self.parent.label_field13.hidden = True
        self.parent.updatefield13.hidden = True
        self.parent.label_field13.value = ""
        self.parent.updatefield13.value = None
        self.parent.label_field13.display()
        self.parent.updatefield13.display()

        self.parent.label_field14.hidden = True
        self.parent.updatefield14.hidden = True
        self.parent.label_field14.value = ""
        self.parent.updatefield14.value = None
        self.parent.label_field14.display()
        self.parent.updatefield14.display()

        self.parent.label_field15.hidden = True
        self.parent.updatefield15.hidden = True
        self.parent.label_field15.value = ""
        self.parent.updatefield15.value = None
        self.parent.label_field15.display()
        self.parent.updatefield15.display()

        self.parent.label_field16.hidden = True
        self.parent.updatefield16.hidden = True
        self.parent.label_field16.value = ""
        self.parent.updatefield16.value = None
        self.parent.label_field16.display()
        self.parent.updatefield16.display()

        self.parent.label_field17.hidden = True
        self.parent.updatefield17.hidden = True
        self.parent.label_field17.value = ""
        self.parent.updatefield17.value = None
        self.parent.label_field17.display()
        self.parent.updatefield17.display()

        self.parent.label_field18.hidden = True
        self.parent.updatefield18.hidden = True
        self.parent.label_field18.value = ""
        self.parent.updatefield18.value = None
        self.parent.label_field18.display()
        self.parent.updatefield18.display()

        self.parent.label_field19.hidden = True
        self.parent.updatefield19.hidden = True
        self.parent.label_field19.value = ""
        self.parent.updatefield19.value = None
        self.parent.label_field19.display()
        self.parent.updatefield19.display()

        self.parent.label_field20.hidden = True
        self.parent.updatefield20.hidden = True
        self.parent.label_field20.value = ""
        self.parent.updatefield20.value = None
        self.parent.label_field20.display()
        self.parent.updatefield20.display()

        # get field values and populates field chooser and field criteria boxes
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            field_list.append('[ALL]')

            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box1.values = field_list
            self.parent.field_box1.display()
            self.parent.field_box2.values = field_list
            self.parent.field_box2.display()
            self.parent.field_box3.values = field_list
            self.parent.field_box3.display()

            self.parent.updatefield_box.values = field_list
            self.parent.updatefield_box.display()

            self.parent.parentApp.table1 = act_on_this

        else:
            npyscreen.notify_confirm(str(results[1]))


class QBUpdate_TableBox(npyscreen.BoxTitle):
    _contained_widget = QBUpdate_TableList


class QB_UpdateFieldList(npyscreen.MultiSelect):
    pass


class QB_UpdateFieldBox(npyscreen.BoxTitle):
    _contained_widget = QB_UpdateFieldList


class QBDelete_TableList(npyscreen.MultiLineAction):

    def actionHighlighted(self, act_on_this, key_press):

        self.parent.label_table.value = act_on_this
        self.parent.label_table.display()

        field_list = []

        #run query
        results = self.parent.parentApp.dbms.get_table_fields(act_on_this)
        if results[0] == "success":
            field_list.append('[ALL]')

            for field in results[1]:
                field_list.append(field[0])
            self.parent.field_box1.values = field_list
            self.parent.field_box1.display()
            self.parent.field_box2.values = field_list
            self.parent.field_box2.display()
            self.parent.field_box3.values = field_list
            self.parent.field_box3.display()

            self.parent.parentApp.table1 = act_on_this

        else:
            npyscreen.notify_confirm(str(results[1]))


class QBDelete_TableBox(npyscreen.BoxTitle):
    _contained_widget = QBDelete_TableList


class ImportExportWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45)

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74,
                 color="VERYGOOD")

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96)

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        # adds handler to open file selection dialog when 'f' is pressed
        self.selectfile_key = '+'
        self.add_handlers({self.selectfile_key: self.open_file_dialog})

        self.nextrely += 1  # Move down

        self.add(npyscreen.FixedText, value="Database: {}".format(self.parentApp.active_db), color="VERYGOOD",
                 relx=3, editable=False)

        self.add(npyscreen.FixedText, value="Select a table to import",
                 relx=3, rely=5, max_width=33, color="CONTROL",editable=False)

        self.add(npyscreen.FixedText, value="into or to export to an",
                 relx=3, rely=6, max_width=33, color="CONTROL",editable=False)

        self.add(npyscreen.FixedText, value="external CSV file",
                 relx=3, rely=7, max_width=33, color="CONTROL",editable=False)

        self.tablebox = self.add(npyscreen.BoxTitle, w_id="wTables_box", name="Tables", values=self.parentApp.tableList,
                                 rely=9, max_width=25, max_height=20, scroll_exit=True)

        self.add(npyscreen.FixedText, value="IMPORT CSV Table Data", color="LABEL", relx=30, rely=10, editable=False)

        self.add(npyscreen.FixedText, value="Press '+' to select CSV file to import", relx=30, rely=12, max_width=45,
                 color="CONTROL")

        self.import_filename = self.add(npyscreen.TitleFixedText, name="Import File/Path: ", value="", relx=30, rely=13,
                                        max_width=80, begin_entry_at=7, editable=False)

        self.add(Import_Button, name="Import", relx=28, rely=15, color="CONTROL", scroll_exit=True)

        self.add(npyscreen.FixedText, value="---------------------------------------", relx=30, rely=17, max_width=45,
                 color="CONTROL")

        self.add(npyscreen.FixedText, value="EXPORT Table to CSV File", color="LABEL", relx=30, rely=19, editable=False)

        self.export_filename = self.add(npyscreen.TitleText, name="CSV Path/Filename: ", value="", relx=30,
                                        rely=21, max_width=80, begin_entry_at=20, use_two_lines=False)

        self.add(Export_Button, name="Export", relx=28, rely=23, color="CONTROL", scroll_exit=True)

        #self.nextrely += 1  # Move down


        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    def open_file_dialog(self, code_of_key_pressed):

        self.selected_importfile = npyscreen.selectFile(starting_value="/home/csv_files")
        #npyscreen.notify_yes_no('Are you sure you want to import {}'.format(self.selected_importfile) + "?",
        #                        title='File Selected')
        self.import_filename.value = self.selected_importfile
        self.import_filename.display()


    @staticmethod
    def display_help():
        help_msg = "Use this page to import or export contents between database tables and CSV files.\n\n" \
                   "In order to import data from a CSV file into a database, you must first create a table containing\n" \
                   "matching column field names and types matching the CSV file. Then, to import a CSV file, press the\n" \
                   "'+' key to select the file. Select the table in the list and then choose the 'Import' button.\n\n" \
                   "A note regarding MySQL file import: Linux AppArmor access control limits visibility to files to be\n" \
                   "imported by MySQL's LOAD DATA functionality. To workaround this in ezdb, AppArmor's config file has\n" \
                   "been modified to provide import file visibility in the top level '/tmp' directory. Because of this,\n" \
                   "be sure to place any file you wish to import using MySQL into the '/tmp' directory."

        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)


class AdminWindow(npyscreen.ActionForm, npyscreen.SplitForm):

    def create(self):

        # main navigation menu buttons
        self.add(NavMainButton, w_id="wNavMain", name="Main", value="Main",rely=1, scroll_exit=True)

        self.add(NavDatabaseButton, w_id="wNavDatabase", name="Databases", value="DatabaseWindow", rely=1, relx=14,
                 scroll_exit=True)

        self.add(NavTablesButton, w_id="wNavTables", name="Tables", value="TablesWindow", rely=1, relx=31)

        self.add(NavQueryButton, w_id="wNavQuery", name="Query", value="QueryWindow", rely=1, relx=45)

        self.add(NavRawSQLButton, w_id="wNavRawSQL", name="Raw SQL", value="RawSQLWindow", rely=1, relx=58)

        self.add(NavImportExportButton, w_id="wNavExport", name="Import/Export", value="ExportWindow", rely=1, relx=74)

        self.add(NavAdminButton, w_id="wNavAdmin", name="Admin", value="AdminWindow", rely=1, relx=96, color="VERYGOOD")

        self.add(NavExitButton, w_id="wNavExit", name="Exit", value="AdminWindow", rely=1, relx=109)

        self.add(npyscreen.FixedText, value="Here is the ADMIN window", editable=False)

        # Help menu guidance
        self.nextrely = 34
        self.nextrelx = 2
        self.add(npyscreen.FixedText, value=" Press ^Q for Help ", editable=False)

        # Register help key
        self.add_handlers({'^Q': self.display_help})

    @staticmethod
    def display_help(self):
        help_msg = "Use this screen to manage permissions for the currently selected database instance. You can add " \
                   "user accounts and modify user read/write access from this page."
        npyscreen.notify_confirm(help_msg, title='Help Menu', editw=1)

'''DATABASE BUTTONS'''

class OpenDBButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.db_box.value is None:
            npyscreen.notify_confirm("Please select a database by highlighting it and enter")
            return

        else:
            selected_db = self.parent.db_box.values[self.parent.db_box.value]
            self.parent.parentApp.active_db = selected_db
            self.parent.parentApp.dbms.connect_database(self.parent.parentApp.active_db)

            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()

            self.parent.parentApp.switchForm("TablesWindow")


class CreateDBButton(npyscreen.ButtonPress):
    newDB_name = None

    def whenPressed(self):
        self.newDB_name = self.parent.get_widget("wNewDB_name").value
        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " + str(self.newDB_name) + "?",
                                                 "Confirm Creation", editw=2)
        if create_confirm:
            servermsg = self.parent.parentApp.dbms.create_database(self.newDB_name)
            npyscreen.notify_confirm(servermsg)
            self.parent.db_box.values = self.parent.parentApp.dbms.list_databases()
            self.parent.db_box.display()

            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class DeleteDBButton(npyscreen.ButtonPress):
    def whenPressed(self):

        #npyscreen.notify_confirm("self.parent.db_box.value = " + str(self.parent.db_box.value))

        if self.parent.db_box.value is None:
            npyscreen.notify_confirm("Please select a database by highlighting it and enter")
            return

        else:
            selected_db = self.parent.db_box.values[self.parent.db_box.value]

            delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(selected_db) + "?",
                                                     "Confirm Deletion", editw=2)
            if delete_confirm:
                servermsg = self.parent.parentApp.dbms.delete_database(selected_db)

                npyscreen.notify_confirm(servermsg)
                dblist = self.parent.parentApp.dbms.list_databases()
                self.parent.db_box.value = None
                self.parent.db_box.values = dblist
                self.parent.db_box.display()
                return

            else:
                npyscreen.blank_terminal() # clears the notification and just goes back to the original form

'''TABLE BUTTONS'''

class ViewTableStructButton(npyscreen.ButtonPress):

    def whenPressed(self):

        # reset page values
        self.parent.parentApp.page_num = 1
        self.parent.parentApp.num_pages = 0

        # hides number of pages and page controls as default should results return 0 records

        self.parent.numpages.hidden = True
        self.parent.numpages.display()

        self.parent.prevpage.hidden = True
        self.parent.nextpage.hidden = True

        self.parent.prevpage.display()
        self.parent.nextpage.display()

        # checks if table value is highlighted before browsing, else perform query

        if self.parent.tablebox.value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.tablebox.value]
            self.results = self.parent.parentApp.dbms.view_table_struct(self.selected_table)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))

        elif self.results[0] == 'success':

            self.parent.parentApp.query_results = self.results[1]
            self.parent.parentApp.col_titles = self.results[2]
            self.parent.parentApp.num_records = self.results[3]

            # calculate number of pages (assuming 10 rows per page)
            self.parent.parentApp.num_pages = \
                int(math.ceil(float(self.parent.parentApp.num_records) / self.parent.parentApp.per_page))

            # display up to 10 rows
            self.parent.gridbox_results.values = \
                self.parent.parentApp.query_results[self.parent.parentApp.row_start - 1: self.parent.parentApp.row_end]

            # get column titles
            self.parent.gridbox_results.entry_widget.col_titles = self.parent.parentApp.col_titles

            # return number of records found
            self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

        # if records found, display page num and num pages information, and page control buttons
        if self.parent.parentApp.num_records > 0:

            self.parent.numpages.value = \
                "Page {} of {}".format(self.parent.parentApp.page_num, self.parent.parentApp.num_pages)

            self.parent.numpages.hidden = False
            self.parent.numpages.display()

            self.parent.prevpage.hidden = False
            self.parent.nextpage.hidden = False

            self.parent.prevpage.display()
            self.parent.nextpage.display()

        # no records found, so hide page num and num pages information, and page control buttons
        else:
            self.parent.numpages.hidden = True
            self.parent.numpages.display()

            self.parent.prevpage.hidden = True
            self.parent.nextpage.hidden = True

            self.parent.prevpage.display()
            self.parent.nextpage.display()

        # display grid results and number or records
        self.parent.gridbox_results.display()
        self.parent.numrecords.display()
        return


class BrowseTableButton(npyscreen.ButtonPress):

    def whenPressed(self):

        # reset page values
        self.parent.parentApp.page_num = 1
        self.parent.parentApp.num_pages = 0

        # hides number of pages and page controls as default should results return 0 records

        self.parent.numpages.hidden = True
        self.parent.numpages.display()

        self.parent.prevpage.hidden = True
        self.parent.nextpage.hidden = True

        self.parent.prevpage.display()
        self.parent.nextpage.display()

        # checks if table value is highlighted before browsing, else perform query

        if self.parent.tablebox.value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return

        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.tablebox.value]
            self.results = self.parent.parentApp.dbms.browse_table(self.selected_table)

            if self.results[0] == 'error':
                npyscreen.notify_confirm(str(self.results[1]))

            elif self.results[0] == 'success':

                self.parent.parentApp.query_results = self.results[1]
                self.parent.parentApp.col_titles = self.results[2]
                self.parent.parentApp.num_records = self.results[3]

                # calculate number of pages (assuming 10 rows per page)
                self.parent.parentApp.num_pages = \
                    int(math.ceil(float(self.parent.parentApp.num_records) / self.parent.parentApp.per_page))

                # display up to 10 rows
                self.parent.gridbox_results.values = \
                    self.parent.parentApp.query_results[self.parent.parentApp.row_start - 1: self.parent.parentApp.row_end]

                # get column titles
                self.parent.gridbox_results.entry_widget.col_titles = self.parent.parentApp.col_titles

                # return number of records found
                self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

            # if records found, display page num and num pages information, and page control buttons
            if self.parent.parentApp.num_records > 0:

                self.parent.numpages.value = \
                    "Page {} of {}".format(self.parent.parentApp.page_num, self.parent.parentApp.num_pages)

                self.parent.numpages.hidden = False
                self.parent.numpages.display()

                self.parent.prevpage.hidden = False
                self.parent.nextpage.hidden = False

                self.parent.prevpage.display()
                self.parent.nextpage.display()

            # no records found, so hide page num and num pages information, and page control buttons
            else:
                self.parent.numpages.hidden = True
                self.parent.numpages.display()

                self.parent.prevpage.hidden = True
                self.parent.nextpage.hidden = True

                self.parent.prevpage.display()
                self.parent.nextpage.display()

            # display grid results and number or records
            self.parent.gridbox_results.display()
            self.parent.numrecords.display()
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
        self.field_type_val = ""
        self.attribute = ""
        self.auto_increment = ""

        if self.parent.get_widget("wField_length_or_val").value:
            self.field_type_val += "("
            self.field_type_val += str(self.parent.get_widget("wField_length_or_val").value)
            self.field_type_val += ")"
            self.field_string += (self.field_name + " " + self.field_type + self.field_type_val)

        elif self.parent.parentApp.dbtype == 1 and self.field_type == "VARCHAR":
            npyscreen.notify_confirm("You must specify a length value for the VARCHAR data type")
            return

        else:
            self.field_string += (self.field_name + " " + self.field_type)

        if self.parent.parentApp.dbtype == 1:

            if self.parent.get_widget("wAttribute").get_selected_objects()[0] is not None:

                self.attribute = str(self.parent.get_widget("wAttribute").get_selected_objects()[0])

                if self.attribute == "binary" and (self.field_type != "tinytext" or "text" or "mediumtext" or "longtext"):

                    npyscreen.notify_confirm("The 'binary' attribute can only be used with one of the following data"
                                             " types:\ntinytext, text, mediumtext or longtext")
                    return

                elif (self.attribute == "unsigned" or self.attribute == "unsigned zerofill") \
                    and self.field_type not in ("TINYINT", "SMALLINT", "INT", "BIGINT", "FLOAT", "DOUBLE", "REAL",
                                                "DECIMAL", "NUMERIC"):

                    npyscreen.notify_confirm("The 'unsigned' and 'unsigned zerofill' attribute can only be used with"
                                             " one of the following data types:\n"
                                             "TINYINT, SMALLINT, INT, BIGINT, FLOAT, DOUBLE, REAL, DECIMAL or NUMERIC")
                    return

                elif self.attribute == "on update current_timestamp" and self.field_type != "TIMESTAMP":

                    npyscreen.notify_confirm("The 'on update current_timestamp' attribute can only be used with"
                                             " the TIMESTAMP data type")
                    return

                else:
                    self.field_string += (" " + self.attribute)

        if self.parent.get_widget("wCollation").get_selected_objects()[0] is not None:

            if self.parent.parentApp.dbtype == 0:

                if self.field_type not in ("CHAR", "VARCHAR", "TEXT"):
                    npyscreen.notify_confirm("Collation can only be used with CHAR, VARCHAR and TEXT data types")
                    return

                else:
                    #if postgreSQ, collation name needs double quotesL
                    self.collation = "COLLATE \"" + str(self.parent.get_widget("wCollation").get_selected_objects()[0])\
                                     + "\""

            else:

                if self.field_type not in ("CHAR", "VARCHAR", "TINYTEXT", "TEXT", "MEDIUMTEXT", "LONGTEXT"):
                    npyscreen.notify_confirm("Collation can only be used with CHAR, VARCHAR, TINYTEXT, TEXT,"
                                             " MEDIUMTEXT and LONGTEXT data types")
                    return

                else:
                    #if MySQL
                    self.collation = "COLLATE " + str(self.parent.get_widget("wCollation").get_selected_objects()[0])

            self.field_string += (" " + self.collation)

        if self.parent.get_widget("wConstraint").get_selected_objects()[0] is not None:

            self.constraint = self.parent.get_widget("wConstraint").get_selected_objects()[0]

        if self.parent.get_widget("wNot_null").value[0] == 1:
            self.not_null = "NOT NULL"

        elif self.parent.get_widget("wNot_null").value[0] == 0 and self.constraint != "PRIMARY KEY":
            self.not_null = "NULL"

        else:
            npyscreen.notify_confirm("A Primary Key cannot be null. Select the 'Required' option.")
            return

        self.field_string += (" " + self.not_null)

        if self.parent.get_widget("wDefault").value:
            self.default = "DEFAULT '" + str(self.parent.get_widget("wDefault").value) + "'"
            self.field_string += (" " + self.default)

        if self.parent.parentApp.dbtype == 1:

            if self.parent.get_widget("wAuto_increment").value[0] == 1 and self.field_type in ("TINYINT", "SMALLINT",
                                                    "INT", "BIGINT", "FLOAT", "DOUBLE", "REAL", "DECIMAL", "NUMERIC"):

                self.auto_increment = "AUTO_INCREMENT"
                self.field_string += (" " + self.auto_increment)

            elif self.parent.get_widget("wAuto_increment").value[0] == 1 and self.field_type not in ("TINYINT", "SMALLINT",
                                                    "INT", "BIGINT", "FLOAT", "DOUBLE", "REAL", "DECIMAL", "NUMERIC"):

                npyscreen.notify_confirm("Auto increment can only be used on a numeric data type")
                return

            self.parent.parentApp.engine = self.parent.get_widget("wStorage_engine").get_selected_objects()[0]

        if self.constraint:
            self.field_string += (" " + self.constraint)

        add_confirm = npyscreen.notify_yes_no("Add the following field?\n" + self.field_string, editw=2)
        if add_confirm:
            self.parent.parentApp.field_string_array.append(self.field_string + ", ")

            if self.parent.parentApp.dbtype == 0:
                self.parent.parentApp.switchForm("TableCreatePostgreSQLForm")

            else:
                self.parent.parentApp.switchForm("TableCreateMySQLForm")

        else:
            return


class CreateTableButton(npyscreen.ButtonPress):
    results = None

    def whenPressed(self):

        if self.parent.parentApp.dbtype == 1 and not self.parent.parentApp.field_string_array:
                npyscreen.notify_confirm("Sorry, you can't create an empty table in MySQL")
                return

        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " +
                                                 str(self.parent.parentApp.table_name) + "?", "Confirm Creation",
                                                 editw=2)

        if create_confirm:
            create_table_string = "CREATE TABLE {} ".format(self.parent.parentApp.table_name)
            field_string = ""

            if self.parent.parentApp.field_string_array is not None:
                for field in self.parent.parentApp.field_string_array:
                    field_string += field
                field_string = field_string[:-2]

            create_table_string += "(" + field_string + ")"

            if self.parent.parentApp.dbtype == 1:
                create_table_string += "ENGINE=" + self.parent.parentApp.engine + ";"

            npyscreen.notify_confirm(create_table_string)

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
            self.parent.parentApp.query_results = []
            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()

            self.parent.parentApp.switchForm("TablesWindow")

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class DeleteTableButton(npyscreen.ButtonPress):
    selected_table = None

    def whenPressed(self):
        if self.parent.tablebox.value is None:
            npyscreen.notify_confirm("Please select a table by highlighting it and enter")
            return
        else:
            self.selected_table = self.parent.parentApp.tableList[self.parent.tablebox.value]

        delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(self.selected_table) + "?",
                                                 "Confirm Deletion", editw=2)
        if delete_confirm:
            servermsg = self.parent.parentApp.dbms.delete_table(self.selected_table)
            self.parent.tablebox.value = None
            if servermsg:
                npyscreen.notify_confirm(servermsg)

            self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()
            self.parent.tablebox.values = self.parent.parentApp.tableList
            self.parent.tablebox.display()
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form

'''QUERY BUILDER BUTTONS'''

class QB_SQL_Build_Button(npyscreen.ButtonPress):

    def whenPressed(self):

        self.sql_string = "SELECT "
        self.table_string = ""
        self.field_string = ""
        self.criteria1_string = ""
        self.criteria2_string = ""
        self.criteria3_string = ""
        self.orderby_string = ""

        '''table and paired field checks'''

        # check to make sure at least one table selected
        if self.parent.label_table1.value == "None" and self.parent.label_table2.value == "None" \
                and self.parent.label_table3.value == "None":
            npyscreen.notify_confirm("You must select at least one table")
            return

        # check to make sure a selected table has field selected
        if self.parent.label_table1.value != "None" and self.parent.label_field1.value == "None":
            npyscreen.notify_confirm("Select a field for the {} table".format(self.parent.parentApp.table1))
            return

        if self.parent.label_table2.value != "None" and self.parent.label_field2.value == "None":
            npyscreen.notify_confirm("Select a field for the {} table".format(self.parent.parentApp.table2))
            return

        if self.parent.label_table3.value != "None" and self.parent.label_field3.value == "None":
            npyscreen.notify_confirm("Select a field for the {} table".format(self.parent.parentApp.table3))
            return

        '''build table and field_strings'''
        if self.parent.label_table1.value != "None":
            if self.parent.label_field1.value == "[ALL]":
                self.parent.label_field1.value = "*"

            self.field_string += self.parent.label_table1.value + "." + self.parent.label_field1.value + ", "

            # check for duplicate table name; if found, add later on
            if self.parent.label_table1.value in [self.parent.label_table2.value, self.parent.label_table3.value]:
                pass
            else:
                self.table_string += self.parent.label_table1.value + ", "

        if self.parent.label_table2.value != "None":
            if self.parent.label_field2.value == "[ALL]":
                self.parent.label_field2.value = "*"

            self.field_string += self.parent.label_table2.value + "." + self.parent.label_field2.value + ", "

            if self.parent.label_table2.value == self.parent.label_table3.value:
                pass
            else:
                self.table_string += self.parent.label_table2.value + ", "

        if self.parent.label_table3.value != "None":
            if self.parent.label_field3.value == "[ALL]":
                self.parent.label_field3.value = "*"

            self.field_string += self.parent.label_table3.value + "." + self.parent.label_field3.value + ", "
            self.table_string += self.parent.label_table3.value + ", "

        self.field_string = self.field_string[:-2]  # strip last comma from string
        self.table_string = self.table_string[:-2]  # strip last comma from string

        '''build WHERE criteria strings'''

        # build criteria 1 string

        if self.parent.tbl1_criteria1.value == "" and self.parent.tbl2_criteria1.value == "" \
                and self.parent.tbl3_criteria1.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria1_string += "("

            if self.parent.tbl1_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table1.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.tbl1_criteria1.value + ")"

                if self.parent.tbl2_criteria1.value != "" or self.parent.tbl3_criteria1.value != "":
                    self.criteria1_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.tbl2_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table2.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.tbl2_criteria1.value + ")"

                if self.parent.tbl3_criteria1.value != "":
                    self.criteria1_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.tbl3_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table3.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.tbl3_criteria1.value + ")"

            self.criteria1_string += ")"

        # build criteria 2 string

        if self.parent.tbl1_criteria2.value == "" and self.parent.tbl2_criteria2.value == "" \
                and self.parent.tbl3_criteria2.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria2_string += "("

            if self.parent.tbl1_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table1.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.tbl1_criteria2.value + ")"

                if self.parent.tbl2_criteria2.value != "" or self.parent.tbl3_criteria2.value != "":
                    self.criteria2_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.tbl2_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table2.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.tbl2_criteria2.value + ")"

                if self.parent.tbl3_criteria2.value != "":
                    self.criteria2_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.tbl3_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table3.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.tbl3_criteria2.value + ")"

            self.criteria2_string += ")"

        # build criteria 3 string

        if self.parent.tbl1_criteria3.value == "" and self.parent.tbl2_criteria3.value == "" \
                and self.parent.tbl3_criteria3.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria3_string += "("

            if self.parent.tbl1_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table1.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.tbl1_criteria3.value + ")"

                if self.parent.tbl2_criteria3.value != "" or self.parent.tbl3_criteria3.value != "":
                    self.criteria3_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.tbl2_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table2.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.tbl2_criteria3.value + ")"

                if self.parent.tbl3_criteria3.value != "":
                    self.criteria3_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.tbl3_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table3.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.tbl3_criteria3.value + ")"

            self.criteria3_string += ")"

        '''build ORDER BY string'''
        # check if no table columns are to be sorted
        if self.parent.tbl1_sort.get_selected_objects()[0] == "NO SORT" \
                and self.parent.tbl2_sort.get_selected_objects()[0] == "NO SORT" \
                and self.parent.tbl3_sort.get_selected_objects()[0] == "NO SORT":
            pass

        else:
            # checks if table val and sor val is not 'No Sort' and the field val isn't '*'
            if self.parent.label_table1.value != "None" and self.parent.tbl1_sort.get_selected_objects()[0] \
                    != "NO SORT" and self.parent.label_field1.value != "*":

                self.orderby_string += self.parent.label_table1.value + "." + self.parent.label_field1.value \
                                       + " {}, ".format(self.parent.tbl1_sort.get_selected_objects()[0])

            if self.parent.label_table2.value != "None" and self.parent.tbl2_sort.get_selected_objects()[0] \
                    != "NO SORT" and self.parent.label_field2.value != "*":

                self.orderby_string += self.parent.label_table2.value + "." + self.parent.label_field2.value \
                                       + " {}, ".format(self.parent.tbl2_sort.get_selected_objects()[0])

            if self.parent.label_table3.value != "None" and self.parent.tbl3_sort.get_selected_objects()[0] \
                    != "NO SORT" and self.parent.label_field3.value != "*":

                self.orderby_string += self.parent.label_table3.value + "." + self.parent.label_field3.value \
                                       + " {}, ".format(self.parent.tbl3_sort.get_selected_objects()[0])

            self.orderby_string = self.orderby_string[:-2]

        '''build cumulative SQL string'''

        self.sql_string += self.field_string + "\nFROM " + self.table_string

        # check if no criteria fields are specified; if so, add
        if self.criteria1_string == "" and self.criteria2_string == "" and self.criteria3_string == "":
            pass

        else:
            self.sql_string += "\nWHERE "

            if self.criteria1_string != "":
                self.sql_string += self.criteria1_string

                if self.criteria2_string != "":  # if criteria 2 exists

                    # get condition1 value and add it and criteria 2
                    self.sql_string += "\n" + self.parent.condition1.get_selected_objects()[0] + " " \
                                       + self.criteria2_string

                if self.criteria3_string != "":  # if criteria 3 exists

                    # get condition2 value and add it and criteria 3
                    self.sql_string += "\n " + self.parent.condition2.get_selected_objects()[0] + " " \
                                       + self.criteria3_string

            elif self.criteria2_string != "":
                self.sql_string += self.criteria2_string

                if self.criteria3_string != "":  # if criteria 3 exists

                    # get condition2 value and add it and criteria 3
                    self.sql_string += "\n" + self.parent.condition2.get_selected_objects()[0] + " " \
                                       + self.criteria3_string

            elif self.criteria3_string != "":
                self.sql_string += self.criteria3_string

        # check if order by fields are specified; if so, add
        if self.orderby_string == "":
            pass

        else:
            self.sql_string += "\nORDER BY " + self.orderby_string


        #npyscreen.notify_confirm("SQL string = " + self.sql_string)

        self.parent.query_box.entry_widget.value = self.sql_string
        self.parent.query_box.display()


class QB_SQL_Send_Button(npyscreen.ButtonPress):
    sql_command, results = (None,)*2

    def whenPressed(self):

        #clear results
        self.parent.parentApp.query_results = []
        self.parent.parentApp.col_titles = []

        self.sql_query = self.parent.get_widget("wSQL_query").value
        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_query)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':

            self.parent.parentApp.query_results = self.results[1]
            if self.results[2]:
                self.parent.parentApp.col_titles = self.results[2]
            if self.results[3]:
                self.parent.parentApp.num_records = self.results[3]

            self.parent.parentApp.switchForm("QueryResultsWindow")


class SQL_Send_Button(npyscreen.ButtonPress):

    def whenPressed(self):

        #clear query results
        self.parent.parentApp.query_results = []
        self.parent.parentApp.col_titles = []

        # init page values
        self.parent.parentApp.row_start = 1  #sets the start row range
        self.parent.parentApp.row_end = 15  #sets the end row range
        self.parent.parentApp.per_page = 15  #sets the number of rows displayed per page result
        self.parent.parentApp.page_num = 1
        self.parent.parentApp.num_pages = 0

        self.sql_query = self.parent.get_widget("wSQL_query").value
        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_query)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':

            self.parent.parentApp.query_results = self.results[1]
            self.parent.parentApp.col_titles = self.results[2]
            self.parent.parentApp.num_records = self.results[3]

            if self.parent.parentApp.num_records != 0 and self.parent.parentApp.per_page != 0:

                # calculate number of pages (assuming 10 rows per page)
                self.parent.parentApp.num_pages = int(math.ceil(float(self.parent.parentApp.num_records) /
                                                                self.parent.parentApp.per_page))

                # display up to 25 rows
                self.parent.gridbox_results.values = \
                    self.parent.parentApp.query_results[self.parent.parentApp.row_start-1: self.parent.parentApp.row_end]

                # get column titles
                self.parent.gridbox_results.entry_widget.col_titles = self.parent.parentApp.col_titles

                # return number of records found
                self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

                # if records found, display page num and num pages information, and page control buttons
                if self.parent.parentApp.num_records > 0:

                    self.parent.numpages.value = \
                        "Page {} of {}".format(self.parent.parentApp.page_num, self.parent.parentApp.num_pages)

                    self.parent.numpages.hidden = False
                    self.parent.prevpage.hidden = False
                    self.parent.nextpage.hidden = False

                # no records found, so hide page num and num pages information, and page control buttons
                else:
                    self.parent.numpages.hidden = True
                    self.parent.prevpage.hidden = True
                    self.parent.nextpage.hidden = True

                self.parent.numrecords.value = "{} Records Found".format(self.parent.parentApp.num_records)

                self.parent.gridbox_results.display()
                self.parent.numrecords.display()
                self.parent.numpages.display()
                self.parent.prevpage.display()
                self.parent.nextpage.display()

                return


class QBDelete_Button(npyscreen.ButtonPress):

    def whenPressed(self):

        ''' table and paired field checks '''

        # check to make sure at least one table selected
        if self.parent.label_table.value == "Unselected":
            npyscreen.notify_confirm("You must select a table")
            return

        # check to make sure a selected table has field selected
        if self.parent.label_table.value != "Unselected" and self.parent.label_field1.value == "Unselected" and \
                        self.parent.label_field2.value == "Unselected" and \
                        self.parent.label_field3.value == "Unselected":
            npyscreen.notify_confirm("Select at least 1 field for the {} table".format(self.parent.parentApp.table1))
            return

        self.sql_string = "DELETE FROM {} ".format(self.parent.parentApp.table1)
        #self.field_string = ""
        self.criteria1_string = ""
        self.criteria2_string = ""
        self.criteria3_string = ""

        if self.parent.label_field1.value == "[ALL]":
            self.parent.label_field1.value = "*"
        elif self.parent.label_field2.value == "[ALL]":
            self.parent.label_field2.value = "*"
        elif self.parent.label_field3.value == "[ALL]":
            self.parent.label_field3.value = "*"

        '''build WHERE criteria strings'''

        # build criteria 1 string

        if self.parent.field1_criteria1.value == "" and self.parent.field2_criteria1.value == "" \
                and self.parent.field3_criteria1.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria1_string += "("

            if self.parent.field1_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.field1_criteria1.value + ")"

                if self.parent.field2_criteria1.value != "" or self.parent.field3_criteria1.value != "":
                    self.criteria1_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.field2_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.field2_criteria1.value + ")"

                if self.parent.field3_criteria1.value != "":
                    self.criteria1_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.field3_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.field3_criteria1.value + ")"

            self.criteria1_string += ")"

        # build criteria 2 string

        if self.parent.field1_criteria2.value == "" and self.parent.field2_criteria2.value == "" \
                and self.parent.field3_criteria2.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria2_string += "("

            if self.parent.field1_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.field1_criteria2.value + ")"

                if self.parent.field2_criteria2.value != "" or self.parent.field3_criteria2.value != "":
                    self.criteria2_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.field2_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.field2_criteria2.value + ")"

                if self.parent.field3_criteria2.value != "":
                    self.criteria2_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.field3_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.field3_criteria2.value + ")"

            self.criteria2_string += ")"

        # build criteria 3 string

        if self.parent.field1_criteria3.value == "" and self.parent.field2_criteria3.value == "" \
                and self.parent.field3_criteria3.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria3_string += "("

            if self.parent.field1_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.field1_criteria3.value + ")"

                if self.parent.field2_criteria3.value != "" or self.parent.field3_criteria3.value != "":
                    self.criteria3_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.field2_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.field2_criteria3.value + ")"

                if self.parent.field3_criteria3.value != "":
                    self.criteria3_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.field3_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.field3_criteria3.value + ")"

            self.criteria3_string += ")"

        '''build cumulative SQL string'''

        # check if no criteria fields are specified; if so, add
        if self.criteria1_string == "" and self.criteria2_string == "" and self.criteria3_string == "":
            npyscreen.notify_confirm("You haven't specified any criteria for deletion")
            return

        else:
            self.sql_string += "\nWHERE "

            if self.criteria1_string != "":
                self.sql_string += self.criteria1_string

                if self.criteria2_string != "":  # if criteria 2 exists

                    # get condition1 value and add it and criteria 2
                    self.sql_string += "\n" + self.parent.condition1.get_selected_objects()[0] + " " \
                                       + self.criteria2_string

                if self.criteria3_string != "":  # if criteria 3 exists

                    # get condition2 value and add it and criteria 3
                    self.sql_string += "\n " + self.parent.condition2.get_selected_objects()[0] + " " \
                                       + self.criteria3_string

            elif self.criteria2_string != "":
                self.sql_string += self.criteria2_string

                if self.criteria3_string != "":  # if criteria 3 exists

                    # get condition2 value and add it and criteria 3
                    self.sql_string += "\n" + self.parent.condition2.get_selected_objects()[0] + " " \
                                       + self.criteria3_string

            elif self.criteria3_string != "":
                self.sql_string += self.criteria3_string

        # npyscreen.notify_confirm("SQL string = " + self.sql_string)

        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_string)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        else:
            npyscreen.notify_confirm("Delete operation completed successfully")


class QueryInsert_LoadFieldsButton(npyscreen.ButtonPress):

    def whenPressed(self):

        field_select_list = self.parent.insertfield_box.entry_widget.get_selected_objects()
        field_list_control = [self.parent.insertfield01, self.parent.insertfield02, self.parent.insertfield03,
                              self.parent.insertfield04, self.parent.insertfield05, self.parent.insertfield06,
                              self.parent.insertfield07, self.parent.insertfield08, self.parent.insertfield09,
                              self.parent.insertfield10, self.parent.insertfield11, self.parent.insertfield12,
                              self.parent.insertfield13, self.parent.insertfield14, self.parent.insertfield15,
                              self.parent.insertfield16, self.parent.insertfield17, self.parent.insertfield18,
                              self.parent.insertfield19, self.parent.insertfield20]

        field_label_control = [self.parent.label_field01, self.parent.label_field02, self.parent.label_field03,
                              self.parent.label_field04, self.parent.label_field05, self.parent.label_field06,
                              self.parent.label_field07, self.parent.label_field08, self.parent.label_field09,
                              self.parent.label_field10, self.parent.label_field11, self.parent.label_field12,
                              self.parent.label_field13, self.parent.label_field14, self.parent.label_field15,
                              self.parent.label_field16, self.parent.label_field17, self.parent.label_field18,
                              self.parent.label_field19, self.parent.label_field20]
        0

        fieldSelectlist_length = len(field_select_list)

        if fieldSelectlist_length == 0 or fieldSelectlist_length > 20:
            npyscreen.notify_confirm("Please select at least 1 and no more than 20 fields for the insert operation")
            return

        fieldSelectList_idx = 0

        self.parent.label_field01.value = field_select_list[fieldSelectList_idx]
        self.parent.label_field01.hidden = False
        self.parent.label_field01.display()

        for label in field_label_control:
            if fieldSelectList_idx == fieldSelectlist_length:
                break

            else:
                label.value = str(field_select_list[fieldSelectList_idx] + ":")
                label.hidden = False
                field_list_control[fieldSelectList_idx].hidden = False

                label.display()
                field_list_control[fieldSelectList_idx].display()
                fieldSelectList_idx += 1


class QueryInsertButton(npyscreen.ButtonPress):

    def whenPressed(self):

        field_list_control = [self.parent.insertfield01, self.parent.insertfield02, self.parent.insertfield03,
                              self.parent.insertfield04, self.parent.insertfield05, self.parent.insertfield06,
                              self.parent.insertfield07, self.parent.insertfield08, self.parent.insertfield09,
                              self.parent.insertfield10, self.parent.insertfield11, self.parent.insertfield12,
                              self.parent.insertfield13, self.parent.insertfield14, self.parent.insertfield15,
                              self.parent.insertfield16, self.parent.insertfield17, self.parent.insertfield18,
                              self.parent.insertfield19, self.parent.insertfield20]

        field_select_list = self.parent.insertfield_box.entry_widget.get_selected_objects()

        fieldSelectlist_length = len(field_select_list)

        if fieldSelectlist_length == 0 or fieldSelectlist_length > 20:
            npyscreen.notify_confirm("Please select the table and fields first")
            return

        field_string = ""
        values_string = ""

        for field in field_select_list:
            field_string += field + ", "

        field_string = field_string[:-2]

        for insertfield in field_list_control:
            if insertfield.value is not None:
                values_string += "'" + insertfield.value + "', "

        values_string = values_string[:-2]

        sql_string = "INSERT INTO {}({}) VALUES({})".format(self.parent.parentApp.insertTable, field_string, values_string)

        self.results = self.parent.parentApp.dbms.execute_SQL(sql_string)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':

            npyscreen.notify_confirm("The insert operation completed successfully")
            return


class QueryUpdate_LoadFieldsButton(npyscreen.ButtonPress):

    def whenPressed(self):

        field_select_list = self.parent.updatefield_box.entry_widget.get_selected_objects()
        field_list_control = [self.parent.updatefield01, self.parent.updatefield02, self.parent.updatefield03,
                              self.parent.updatefield04, self.parent.updatefield05, self.parent.updatefield06,
                              self.parent.updatefield07, self.parent.updatefield08, self.parent.updatefield09,
                              self.parent.updatefield10, self.parent.updatefield11, self.parent.updatefield12,
                              self.parent.updatefield13, self.parent.updatefield14, self.parent.updatefield15,
                              self.parent.updatefield16, self.parent.updatefield17, self.parent.updatefield18,
                              self.parent.updatefield19, self.parent.updatefield20]

        field_label_control = [self.parent.label_field01, self.parent.label_field02, self.parent.label_field03,
                              self.parent.label_field04, self.parent.label_field05, self.parent.label_field06,
                              self.parent.label_field07, self.parent.label_field08, self.parent.label_field09,
                              self.parent.label_field10, self.parent.label_field11, self.parent.label_field12,
                              self.parent.label_field13, self.parent.label_field14, self.parent.label_field15,
                              self.parent.label_field16, self.parent.label_field17, self.parent.label_field18,
                              self.parent.label_field19, self.parent.label_field20]
        0

        fieldSelectlist_length = len(field_select_list)

        if fieldSelectlist_length == 0 or fieldSelectlist_length > 20:
            npyscreen.notify_confirm("Please select at least 1 and no more than 20 fields for the update operation")
            return

        fieldSelectList_idx = 0

        for label in field_label_control:
            if fieldSelectList_idx == fieldSelectlist_length:
                break

            else:
                label.value = str(field_select_list[fieldSelectList_idx] + ":")
                label.hidden = False
                field_list_control[fieldSelectList_idx].hidden = False

                label.display()
                field_list_control[fieldSelectList_idx].display()
                fieldSelectList_idx += 1


class QBUpdate_Button(npyscreen.ButtonPress):

    def whenPressed(self):

        ''' table and paired field checks '''

        # check to make sure at least one table selected
        if self.parent.label_table.value == "Unselected":
            npyscreen.notify_confirm("You must select a table")
            return

        # check to make sure a selected table has field selected
        if self.parent.label_table.value != "Unselected" and self.parent.label_field1.value == "Unselected" and \
                        self.parent.label_field2.value == "Unselected" and \
                        self.parent.label_field3.value == "Unselected":
            npyscreen.notify_confirm("Select at least 1 field for the {} table".format(self.parent.parentApp.table1))
            return

        self.sql_string = "DELETE FROM {} ".format(self.parent.parentApp.table1)
        #self.field_string = ""
        self.criteria1_string = ""
        self.criteria2_string = ""
        self.criteria3_string = ""

        if self.parent.label_field1.value == "[ALL]":
            self.parent.label_field1.value = "*"
        elif self.parent.label_field2.value == "[ALL]":
            self.parent.label_field2.value = "*"
        elif self.parent.label_field3.value == "[ALL]":
            self.parent.label_field3.value = "*"

        '''build WHERE criteria strings'''

        # build criteria 1 string

        if self.parent.field1_criteria1.value == "" and self.parent.field2_criteria1.value == "" \
                and self.parent.field3_criteria1.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria1_string += "("

            if self.parent.field1_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.field1_criteria1.value + ")"

                if self.parent.field2_criteria1.value != "" or self.parent.field3_criteria1.value != "":
                    self.criteria1_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.field2_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.field2_criteria1.value + ")"

                if self.parent.field3_criteria1.value != "":
                    self.criteria1_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.field3_criteria1.value != "":
                self.criteria1_string += "(" + self.parent.label_table.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.field3_criteria1.value + ")"

            self.criteria1_string += ")"

        # build criteria 2 string

        if self.parent.field1_criteria2.value == "" and self.parent.field2_criteria2.value == "" \
                and self.parent.field3_criteria2.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria2_string += "("

            if self.parent.field1_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.field1_criteria2.value + ")"

                if self.parent.field2_criteria2.value != "" or self.parent.field3_criteria2.value != "":
                    self.criteria2_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.field2_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.field2_criteria2.value + ")"

                if self.parent.field3_criteria2.value != "":
                    self.criteria2_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.field3_criteria2.value != "":
                self.criteria2_string += "(" + self.parent.label_table.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.field3_criteria2.value + ")"

            self.criteria2_string += ")"

        # build criteria 3 string

        if self.parent.field1_criteria3.value == "" and self.parent.field2_criteria3.value == "" \
                and self.parent.field3_criteria3.value == "":  # check if all criteria1 fields are empty
            pass

        else:

            self.criteria3_string += "("

            if self.parent.field1_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table.value + "." + self.parent.label_field1.value \
                                         + " " + self.parent.field1_criteria3.value + ")"

                if self.parent.field2_criteria3.value != "" or self.parent.field3_criteria3.value != "":
                    self.criteria3_string += " AND "  # adds 'AND' operator if at least one other criteria1 value exists

            if self.parent.field2_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table.value + "." + self.parent.label_field2.value \
                                         + " " + self.parent.field2_criteria3.value + ")"

                if self.parent.field3_criteria3.value != "":
                    self.criteria3_string += " AND "  # adds 'AND' operator if table 3 criteria1 value exists

            if self.parent.field3_criteria3.value != "":
                self.criteria3_string += "(" + self.parent.label_table.value + "." + self.parent.label_field3.value \
                                         + " " + self.parent.field3_criteria3.value + ")"

            self.criteria3_string += ")"

        '''build cumulative SQL string'''

        # check if no criteria fields are specified; if so, add
        if self.criteria1_string == "" and self.criteria2_string == "" and self.criteria3_string == "":
            npyscreen.notify_confirm("You haven't specified any criteria for deletion")
            return

        else:
            self.sql_string += "\nWHERE "

            if self.criteria1_string != "":
                self.sql_string += self.criteria1_string

                if self.criteria2_string != "":  # if criteria 2 exists

                    # get condition1 value and add it and criteria 2
                    self.sql_string += "\n" + self.parent.condition1.get_selected_objects()[0] + " " \
                                       + self.criteria2_string

                if self.criteria3_string != "":  # if criteria 3 exists

                    # get condition2 value and add it and criteria 3
                    self.sql_string += "\n " + self.parent.condition2.get_selected_objects()[0] + " " \
                                       + self.criteria3_string

            elif self.criteria2_string != "":
                self.sql_string += self.criteria2_string

                if self.criteria3_string != "":  # if criteria 3 exists

                    # get condition2 value and add it and criteria 3
                    self.sql_string += "\n" + self.parent.condition2.get_selected_objects()[0] + " " \
                                       + self.criteria3_string

            elif self.criteria3_string != "":
                self.sql_string += self.criteria3_string

        # npyscreen.notify_confirm("SQL string = " + self.sql_string)

        self.results = self.parent.parentApp.dbms.execute_SQL(self.sql_string)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        else:
            npyscreen.notify_confirm("Delete operation completed successfully")

'''QB NAV BUTTONS'''

class QuerySelectBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryWindow")
        return


class QueryInsertBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryInsertWindow")
        return


class QueryUpdateBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryUpdateWindow")
        return


class QueryDeleteBtn(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("QueryDeleteWindow")
        return

'''IMPORT/EXPORT BUTTONS'''


class Import_Button(npyscreen.ButtonPress):

    def whenPressed(self):

        # check if file is selected and if it's a CSV file
        if str(self.parent.import_filename.value) == "" or str(self.parent.import_filename.value)[-4:] != ".csv":
            npyscreen.notify_confirm("You must select a CSV file to import")
            return

        elif self.parent.tablebox.value is None:
            npyscreen.notify_confirm("You must select a table from the list to import into")
            return

        sql_string = ""

        self.selected_table = self.parent.parentApp.tableList[self.parent.tablebox.value]

        if self.parent.parentApp.dbtype == 0: # if postgresql

            sql_string = "COPY {} FROM '{}' DELIMITER ',' CSV HEADER".format(self.selected_table,
                                                                             self.parent.selected_importfile)

        elif self.parent.parentApp.dbtype == 1: # if mysql

            sql_string = "LOAD DATA INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' " \
                         "IGNORE 1 LINES".format(self.parent.selected_importfile, self.selected_table)
            npyscreen.notify_confirm(sql_string)

        self.results = self.parent.parentApp.dbms.execute_SQL(sql_string)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':

            npyscreen.notify_confirm("File imported successfully")

            return


class Export_Button(npyscreen.ButtonPress):

    def whenPressed(self):

        # check if export file specified has a CSV extension
        if str(self.parent.export_filename.value) == "" or str(self.parent.export_filename.value)[-4:] != ".csv":
            npyscreen.notify_confirm("You must specify filename with a CSV extension to export")
            return

        elif self.parent.tablebox.value is None:
            npyscreen.notify_confirm("You must choose a table from the list to export")
            return

        sql_string = ""

        self.selected_table = self.parent.parentApp.tableList[self.parent.tablebox.value]

        if self.parent.parentApp.dbtype == 0: # if postgresql

            sql_string = "COPY {} TO '{}' DELIMITER ',' CSV HEADER".format(self.selected_table,
                                                                           self.parent.export_filename.value)

        elif self.parent.parentApp.dbtype == 1: # if mysql

            sql_string = "SELECT * INTO OUTFILE '{}' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' " \
                         "LINES TERMINATED BY '\\r\\n' FROM {}".format(self.parent.export_filename.value, self.selected_table)

        npyscreen.notify_confirm(sql_string)
        self.results = self.parent.parentApp.dbms.execute_SQL(sql_string)

        if self.results[0] == 'error':
            npyscreen.notify_confirm(str(self.results[1]))
            return

        elif self.results[0] == 'success':
            #os.chmod(self.parent.export_filename.value, 0o777)
            #os.chown(self.parent.export_filename.value, os.getuid(), os.getgid())
            npyscreen.notify_confirm("File exported successfully")

            return

'''PAGE BUTTONS'''


class PrevPage_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        # npyscreen.notify_confirm("self.parent.parentApp.row_start = " + str(self.parent.parentApp.row_start) +
        #                          "\nself.parent.parentApp.row_end = " + str(self.parent.parentApp.row_end))

        if self.parent.parentApp.page_num > 1:
            self.parent.parentApp.page_num -= 1
            self.parent.parentApp.row_start -= self.parent.parentApp.per_page
            self.parent.parentApp.row_end -= self.parent.parentApp.per_page

            self.parent.gridbox_results.values = \
                self.parent.parentApp.query_results[self.parent.parentApp.row_start-1: self.parent.parentApp.row_end]

            self.parent.gridbox_results.display()

            self.parent.numpages.value = \
                "Page {} of {}".format(self.parent.parentApp.page_num, self.parent.parentApp.num_pages)
            self.parent.numpages.display()

            return


class NextPage_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        # npyscreen.notify_confirm("self.parent.parentApp.row_start = " + str(self.parent.parentApp.row_start) +
        #                         "\nself.parent.parentApp.row_end = " + str(self.parent.parentApp.row_end))
        if self.parent.parentApp.page_num < self.parent.parentApp.num_pages:

            self.parent.parentApp.page_num += 1
            self.parent.parentApp.row_start += self.parent.parentApp.per_page
            self.parent.parentApp.row_end += self.parent.parentApp.per_page

            self.parent.gridbox_results.values = \
                self.parent.parentApp.query_results[self.parent.parentApp.row_start-1: self.parent.parentApp.row_end]

            self.parent.gridbox_results.display()

            self.parent.numpages.value = \
                "Page {} of {}".format(self.parent.parentApp.page_num, self.parent.parentApp.num_pages)
            self.parent.numpages.display()

            return

'''NAV BAR BUTTONS'''


class NavMainButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("MAIN")
        return


class NavDatabaseButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("DatabaseWindow")
        return


class NavTablesButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.parentApp.active_db is None:
            npyscreen.notify_confirm("You must first open a database before accessing the Tables page")
            return

        else:
            #self.parent.parentApp.tableList = self.parent.parentApp.dbms.list_database_tables()
            self.parent.parentApp.switchForm("TablesWindow")


class NavQueryButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.parentApp.active_db is None:
            npyscreen.notify_confirm("You must first open a database before accessing the Query Builder page")
            return

        else:
            self.parent.parentApp.switchForm("QueryWindow")


class NavRawSQLButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("RawSQLWindow")
        return


class NavImportExportButton(npyscreen.ButtonPress):
    def whenPressed(self):

        if self.parent.parentApp.active_db is None:
            npyscreen.notify_confirm("You must first open a database before accessing the Import/Export page")
            return

        else:
            self.parent.parentApp.switchForm("ImportExportWindow")


class NavAdminButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("AdminWindow")
        return


class NavExitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=2)
        if exiting:
            self.parent.parentApp.switchForm(None)
        else:
            # Clears the notification and just goes back to the original form
            npyscreen.blank_terminal()
        return


# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):

    dbtype, host, port, username, password, dbms, active_db, tableList, active_table = (None,)*9

    # Table creation global variables
    field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = (None,)*6

    engine = "InnoDB"  # sets default MySQL engine type

    field_autoincrement, field_primarykey, field_unique, field_index = (False,)*4

    field_optional = True  # User friendly way of saying if Null is okay for this field

    field1, field2, field3, tbl1_criteria1, tbl1_criteria2, tbl1_criteria3, tbl2_criteria1, tbl2_criteria2, \
        tbl2_criteria3, tbl3_criteria1, tbl3_criteria2, tbl3_criteria3, table1, table2, table3, insertTable = (None,)*16

    tablefield_cols, query_results, col_titles, table_struct_results, field_string_array, field_list1, \
    field_list2, field_list3, insertfield_list = ([],)*9

    page_num = 0
    num_pages, num_records = (0,)*2
    row_start = 0
    row_end = 0  # set by forms
    per_page = 0  # set by forms

    def onStart(self):

        # Declare all the forms that will be used within the app
        self.addFormClass("MAIN", Initial, name="Welcome to ezdb", draw_line_at=34, minimum_lines=37,
                          minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("ConnectDBMS", ConnectDBMS, name="ezdb >> DBMS Connection Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("DatabaseWindow", DatabaseWindow, name="ezdb >> Database Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("TablesWindow", TablesWindow, name="ezdb >> Tables Page", draw_line_at=34, minimum_lines=37,
                          minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("QueryWindow", QueryWindow, name="ezdb >> Query >> SELECT Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("QueryInsertWindow", QueryInsertWindow, name="ezdb >> Query >> INSERT Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("QueryUpdateWindow", QueryUpdateWindow, name="ezdb >> Query >> UPDATE Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("QueryDeleteWindow", QueryDeleteWindow, name="ezdb >> Query >> DELETE Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("QueryResultsWindow", QueryResultsWindow, name="ezdb >> Query >> Results Page",
                          draw_line_at=34, minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("RawSQLWindow", RawSQLWindow, name="ezdb >> Raw SQL Page", draw_line_at=34, minimum_lines=37,
                          minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("ImportExportWindow", ImportExportWindow, name="ezdb >> Export Page", draw_line_at=34,
                          minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("AdminWindow", AdminWindow, name="ezdb >> Admin Page", draw_line_at=34, minimum_lines=37,
                          minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("TableCreatePostgreSQLForm", TableCreatePostgreSQLForm, name="ezdb >> Build/Create Table",
                          draw_line_at=34, minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        self.addFormClass("TableCreateMySQLForm", TableCreateMySQLForm, name="ezdb >> Build/Create Table",
                          draw_line_at=34, minimum_lines=37, minimum_columns=120, ALLOW_RESIZE=False)
        # for testing:
        # self.addForm("Nav_Bar", Nav_Bar)

if __name__ == "__main__":

    print "Resizing terminal..."

    # resizes the terminal to 120 x 35
    print "\x1b[8;37;120t"

    # necessary pause to prevent race condition and allow termnal time to resize before launching npyscreen form
    time.sleep(1)

    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()
