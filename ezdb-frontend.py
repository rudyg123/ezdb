#!/usr/bin/env python

import npyscreen
import curses
import postgres_db as pdb
import mysql_db as mdb

# ActionForm includes "Cancel" in addition to "OK"
class Initial(npyscreen.ActionFormWithMenus):
    sessionType = None

    def create(self):

        # Title text
        self.nextrely += 3  # Move down
        self.nextrelx += 23  # Move right (centered))
        self.add(npyscreen.FixedText, value="                _  _     ", editable=False)
        self.add(npyscreen.FixedText, value="               | || |    ", editable=False)
        self.add(npyscreen.FixedText, value="  ___  ____  __| || |__  ", editable=False)
        self.add(npyscreen.FixedText, value=" / _ \|_  / / _` || '_ \ ", editable=False)
        self.add(npyscreen.FixedText, value="|  __/ / / | (_| || |_) |", editable=False)
        self.add(npyscreen.FixedText, value=" \___|/___| \__,_||_.__/ ", editable=False)
        self.nextrely += 1  # Extra padding

        # Add session options and save the selected value

        self.db = self.add(npyscreen.TitleSelectOne, max_height=4,
                                     name="Choose Database Type:", value = [0,],
                                     values = ["postgreSQL", "MySQL"],
                                     scroll_exit=True)


        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")



    def on_ok(self):
        #For debugging:
        #npyscreen.notify_confirm("You selected " + str(self.db.value[0]))
        self.parentApp.dbtype = self.db.value[0]
        self.parentApp.setNextForm("Connect_DBMS")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=2)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form

class Connect_DBMS(npyscreen.ActionFormWithMenus):
    storedConnections = None

    def create(self):

        #set default DBMS connection values
        #For debugging:
        #npyscreen.notify_confirm("The value of dbtype in ConectDBMS is " + str(dbtype))
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

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):

        #connect to DBMS
        if self.parentApp.dbtype == 0:
            self.parentApp.dbms = pdb.Postgres_Database()
            self.parentApp.dbms.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value, self.parentApp.port.value,
                                             self.parentApp.username.value, self.parentApp.password.value)
        elif self.parentApp.dbtype == 1:
            self.parentApp.dbms = mdb.MySQL_Database()
            self.parentApp.dbms.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value, self.parentApp.port.value,
                                             self.parentApp.username.value, self.parentApp.password.value)

        self.parentApp.setNextForm("Database_Window")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class Database_Window(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None


    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1, scroll_exit=True)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.dblist = self.parentApp.dbms.list_databases()

        self.nextrely += 1  # Move down

        if self.parentApp.dbtype == 0:
            self.dbtype_str = "PostgreSQL"
        elif self.parentApp.dbtype == 1:
            self.dbtype_str = "MySQL"

        self.add(npyscreen.TitleSelectOne, w_id="wActiveDB", max_height=10,
                             name="{} Databases:".format(self.dbtype_str), value = [0,],
                             values = self.dblist, scroll_exit=True)

        #database button options
        self.nextrely += 1  # Move down
        self.add(OpenDB_Button, name="Open Database")

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewDB_name", name="New Database Name:", relx=4,
                                   begin_entry_at=22, use_two_lines=False)

        self.add(CreateDB_Button, name="Create")

        self.nextrely += 1  # Move down
        self.add(DeleteDB_Button, name="Delete Database")

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

        #self.add(npyscreen.MiniButton, name = "Main", rely=-1)

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


    def while_waiting(self):
        self.get_widget("wActiveDB").display()


class Tables_Window(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.nextrely += 1  # Move down
        self.add(npyscreen.FixedText, value="Here is the TABLES window", editable=False)
        self.nextrely += 1  # Move down
        self.add(npyscreen.BoxTitle, w_id="wTableresults_box", name="{} Tables".format(self.parentApp.active_db),
                 values=self.parentApp.tablelist, max_width=25, max_height=8, scroll_exit=True)

        self.nextrely += 1  # Move down
        self.add(ViewTableStruct_Button, name="View Table Structure", rely=6, relx=27, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wNewTable_name", name="New Table Name:",
                                  begin_entry_at=22, relx=29, max_width=35, use_two_lines=False)

        self.add(CreateTable_Button, name="Create", relx=27, max_width=35)

        self.nextrely += 1  # Move down
        self.add(DeleteTable_Button, name="Delete Table", relx=27, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.GridColTitles, w_id="w_TableGrid", col_titles=self.parentApp.tablefield_cols, relx=1)


        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def while_editing(self):
        self.get_widget("wTableresults_box").display()

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")

class Table_Create_PostgreSQL_Form(npyscreen.ActionForm):
    '''
    field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = None
    field_autoincrement, field_primarykey, field_unique, field_index= False
    field_optional = True #user friendly way of saying if Null is okay for this field
    '''


    def create(self):

        postgresql_field_type_list = ['CHAR','VARCHAR','TEXT','BIT','VARBIT','SMALLINT','INT','BIGINT','SMALLSERIAL',
                                  'SERIAL','BIGSERIAL','NUMERIC','DOUBLE PRECISION','REAL','MONEY','BOOL',
                                  'DATE','TIMESTAMP','TIMESTAMP WITH TIME ZONE','TIME','TIME WITH TIME ZONE','BYTEA']

        postgresql_field_collat_list = ['en_US.utf8','C','POSIX','C.UTF-8','en_AG','en_AG.utf8','en_AU.utf8',
                                    'en_AU.utf8','en_BW.utf8','en_BW.utf8','en_CA.utf8','en_CA.utf8','en_DK.utf8',
                                    'en_DK.utf8','en_GB.utf8','en_GB.utf8','en_HK.utf8','en_HK.utf8','en_IE.utf8',
                                    'en_IE.utf8','en_IN','en_IN.utf8','en_NG','en_NG.utf8','en_NZ.utf8','en_NZ.utf8',
                                    'en_PH.utf8','en_SG.utf8','en_SG.utf8','en_ZA.utf8','en_ZA.utf8','en_ZM',
                                    'en_ZM.utf8','en_ZW.utf8','en_ZW.utf8']

        postgresql_field_constraint_list = ['NONE','PRIMARY KEY','UNIQUE','INDEX']

        self.add(npyscreen.TitleText, w_id="wField_name", name="Field Name: ", max_width=35, begin_entry_at=15,
                 use_two_lines=False)

        self.add(npyscreen.TitleSelectOne, w_id="wField_type", max_height=4, name="Type: ", value = [0,],
                 values=postgresql_field_type_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wField_length_or_val", name="Length/Value: ", max_width=35,
                                   begin_entry_at=15, use_two_lines=False)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wCollation", max_height=4, name="Collation: ", value = [0,],
                 values=postgresql_field_collat_list, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleSelectOne, w_id="wConstraint", max_height=4, name="Constraint: ", value = [0,],
                 values=postgresql_field_constraint_list, rely=2, relx=40, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.Checkbox, w_id="wNot_null", name="Required?", relx=40)

        self.add(npyscreen.Checkbox, w_id="wAuto_increment", name="Auto Increment?", relx=40)

        self.nextrely += 1  # Move down
        self.add(npyscreen.MultiLineEditableBoxed, w_id="wField_comment", name="Field Comment", max_height=5,
                 relx=40, edit=True, scroll_exit=True)



    def on_cancel(self):
        self.parentApp.setNextForm("Tables_Window")

class FieldComment(npyscreen.MultiLineEdit):
    pass


class FieldComment_Box(npyscreen.BoxTitle):
    _entry_contained_widget = FieldComment
    contained_widget_arguments={
        'name':'comment'
    }


class Table_Create_MySQL_Form(npyscreen.ActionForm):
    '''
    field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = None
    field_autoincrement, field_primarykey, field_unique, field_index= False
    field_optional = True #user friendly way of saying if Null is okay for this field
    '''

    def create(self):
        self.add(npyscreen.TitleText, w_id="wNewField_name", name="Field Name:",
                                   begin_entry_at=15, use_two_lines=False)

class Query_Window(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the QUERY window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

class RawSQL_Window(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.nextrely += 1  # Move down
        self.add(npyscreen.MultiLineEditableBoxed, w_id="wSQL_command", name="Enter SQL Command", max_height=6,
                 relx=20, max_width=40, edit=True, scroll_exit=True)

        self.add(SQL_Button, w_id="wSQL_button", name="Send Command", relx=34)
        self.nextrely += 1  # Move down

        self.add(npyscreen.BoxTitle, w_id="wSQLresults_box", name="SQL Results", values=self.parentApp.sql_results,
                 max_width=75, max_height=11, scroll_exit=True)




        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

class Export_Window(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the EXPORT window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

class Admin_Window(npyscreen.ActionFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
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
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        return

class OpenDB_Button(npyscreen.ButtonPress):
    def whenPressed(self):

        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        self.parent.parentApp.dbms.connect_database(self.parent.parentApp.active_db)
        self.parent.parentApp.tablelist = self.parent.parentApp.dbms.list_database_tables()

        self.parent.parentApp.switchForm("Tables_Window")
        return self.parent.parentApp.tablelist

class CreateDB_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        self.newDB_name = self.parent.get_widget("wNewDB_name").value
        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " + str(self.newDB_name)
                                                 + "?", "Confirm Creation", editw=2)
        if create_confirm:
            servermsg = self.parent.parentApp.dbms.create_database(self.newDB_name)
            npyscreen.notify_confirm(servermsg)
            self.parent.get_widget("wActiveDB").display()
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        self.parent.get_widget("wActiveDB").display()

class DeleteDB_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        #self.parent.parentApp.dbms.connect_database()
        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(self.parent.parentApp.active_db)
                                                 + "?", "Confirm Deletion", editw=2)
        if delete_confirm:
            servermsg = self.parent.parentApp.dbms.delete_database(self.parent.parentApp.active_db)
            npyscreen.notify_confirm(servermsg)
            self.parent.get_widget("wActiveDB").display()
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        self.parent.get_widget("wActiveDB").display()

class ViewTableStruct_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        pass
        '''
        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        self.parent.parentApp.dbms.connect_database(self.parent.parentApp.active_db)
        self.parent.parentApp.tablelist = self.parent.parentApp.dbms.list_database_tables()


        self.parent.parentApp.switchForm("Tables_Window")
        return self.parent.parentApp.tablelist
        '''
class CreateTable_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        self.newTable_name = self.parent.get_widget("wNewTable_name").value
        create_confirm = npyscreen.notify_yes_no("Are you sure you want to create " + str(self.newTable_name)
                                                 + "?", "Confirm Creation", editw=2)
        if create_confirm:
            self.parent.parentApp.table_name = self.newTable_name

            if self.parent.parentApp.dbtype == 0:
                self.parent.parentApp.switchForm("Table_Create_PostgreSQL_Form")
            elif self.parent.parentApp.dbtype == 1:
                self.parent.parentApp.switchForm("Table_Create_MySQL_Form")

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class DeleteTable_Button(npyscreen.ButtonPress):
    def whenPressed(self):

        self.selected_table = self.parent.parentApp.tablelist[self.parent.get_widget("wTableresults_box").value]
        npyscreen.notify_confirm("You selected table: " + str(self.selected_table))


        delete_confirm = npyscreen.notify_yes_no("Are you sure you want to delete " + str(self.selected_table)
                                                 + "?", "Confirm Deletion", editw=2)
        if delete_confirm:
            servermsg = self.parent.parentApp.dbms.delete_table(self.selected_table)
            if servermsg:
                npyscreen.notify_confirm(servermsg)

            self.parent.parentApp.tablelist = self.parent.parentApp.dbms.list_database_tables()
            self.parent.get_widget("wTableresults_box").display()
            return

        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form

class SQL_Button(npyscreen.ButtonPress):
    def whenPressed(self):

        self.sql_command = self.parent.get_widget("wSQL_command").values[0]
        #npyscreen.notify_confirm("You are sending the following SQL: " + str(self.sql_command))
        self.parent.parentApp.sql_results = self.parent.parentApp.dbms.execute_SQL(self.sql_command)
        if self.parent.parentApp.sql_results is None:
            npyscreen.notify_confirm("SQL command sent successfully")
        else:
            npyscreen.notify_confirm(str(self.parent.parentApp.sql_results))
            return


class Tab_DatabaseButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("Database_Window")
        return

class Tab_TablesButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("Tables_Window")
        return

class Tab_QueryButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("Query_Window")
        return

class Tab_RawSQLButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("RawSQL_Window")
        return

class Tab_ExportButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("Export_Window")
        return

class Tab_AdminButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm("Admin_Window")
        return

# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):

    dbtype = None
    host = None
    port = None
    username = None
    password = None
    dbms = None
    active_db = None
    tablelist = None
    active_table = None

    #table creation global variables
    field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = None, None, None, None, None, None

    field_autoincrement, field_primarykey, field_unique, field_index= False, False, False, False
    field_optional = True #user friendly way of saying if Null is okay for this field

    tablefield_cols = []

    sql_results = []

    def onStart(self):

        # Declare all the forms that will be used within the app
        self.addFormClass("MAIN", Initial, name="Welcome to ezdb")
        self.addFormClass("Connect_DBMS", Connect_DBMS, name = "ezdb >> DBMS Connection Page")
        self.addFormClass("Database_Window", Database_Window, name = "ezdb >> Database Page")
        self.addFormClass("Tables_Window", Tables_Window, name = "ezdb >> Tables Page")
        self.addFormClass("Query_Window", Query_Window, name = "ezdb >> Query Page")
        self.addFormClass("RawSQL_Window", RawSQL_Window, name = "ezdb >> Raw SQL Page")
        self.addFormClass("Export_Window", Export_Window, name = "ezdb >> Export Page")
        self.addFormClass("Admin_Window", Admin_Window, name = "ezdb >> Admin Page")
        self.addFormClass("Table_Create_PostgreSQL_Form", Table_Create_PostgreSQL_Form, name = "ezdb >> Create Table")
        self.addFormClass("Table_Create_MySQL_Form", Table_Create_MySQL_Form, name = "ezdb >> Create Table")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()

