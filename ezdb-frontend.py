#!/usr/bin/env python

import npyscreen
import postgres_db as pdb
import mysql_db as mdb


# ActionForm includes "Cancel" in addition to "OK"
class Initial(npyscreen.ActionFormWithMenus):
    sessionType, db = None, None

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
        self.db = self.add(npyscreen.TitleSelectOne, max_height=4, name="Choose Database Type:", value=[0],
                           values=["postgreSQL", "MySQL"], scroll_exit=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

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


class ConnectDBMS(npyscreen.ActionFormWithMenus):
    storedConnections, result = None, None

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

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

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

        # self.add(npyscreen.MiniButton, name = "Main", rely=-1)

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
                 begin_entry_at=22, relx=29, max_width=35, use_two_lines=False)

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
    # field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = None
    # field_autoincrement, field_primarykey, field_unique, field_index= False
    # field_optional = True #user friendly way of saying if Null is okay for this field

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
        self.add(npyscreen.TitleSelectOne, w_id="wConstraint", max_height=4, name="Constraint: ",
                 values=postgresql_field_constraint_list, rely=2, relx=40, max_width=35)

        self.nextrely += 1  # Move down
        self.add(npyscreen.SelectOne, w_id="wNot_null", values=["Not Required", "Required"], value=[0],
                 max_width=20, max_height=4, relx=40)

        # self.add(npyscreen.Checkbox, w_id="wAuto_increment", name="Auto Increment?", relx=40)
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, w_id="wDefault", name="Default: ", max_width=35,
                 relx=40, use_two_lines=False)

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


class FieldComment(npyscreen.MultiLineEdit):
    pass


class FieldCommentBox(npyscreen.BoxTitle):
    _entry_contained_widget = FieldComment
    contained_widget_arguments={
        'name': 'comment'
    }


class TableCreateMySQLForm(npyscreen.ActionForm):
    # field_name, field_type, field_length_or_val, field_collation, field_attrib, field_default = None
    # field_autoincrement, field_primarykey, field_unique, field_index= False
    # field_optional = True #user friendly way of saying if Null is okay for this field
    def create(self):
        self.add(npyscreen.TitleText, w_id="wNewField_name", name="Field Name:", begin_entry_at=15, use_two_lines=False)


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

        self.parent.parentApp.field_string_array.append(self.field_string + ", ")
        npyscreen.notify_confirm("Adding the following field:\n" + self.field_string)
        self.parent.parentApp.switchForm("TableCreatePostgreSQLForm")


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

            npyscreen.notify_confirm(create_table_string)

            self.results = self.parent.parentApp.dbms.execute_SQL(create_table_string)

            if self.results[0] == 'error':
                if self.results[1] == 'no results to fetch':
                    npyscreen.notify_confirm("Table [] successfully created".format(self.parent.parentApp.table_name))
                    self.parent.parentApp.field_string_array = []
                    self.parent.parentApp.switchForm("TablesWindow")
                else:
                    npyscreen.notify_confirm(str(self.results[1]))
                    self.parent.parentApp.field_string_array = []

            elif self.results[0] == 'success':
                npyscreen.notify_confirm("Table [] successfully created".format(self.parent.parentApp.table_name))
                self.parent.parentApp.field_string_array = []

                self.parent.parentApp.switchForm("TablesWindow")
                return

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
        self.parent.parentApp.switchForm("TablesWindow")
        return


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
        self.addFormClass("TableCreatePostgreSQLForm", TableCreatePostgreSQLForm, name="ezdb >> Create Table")
        self.addFormClass("TableCreateMySQLForm", TableCreateMySQLForm, name="ezdb >> Create Table")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()
