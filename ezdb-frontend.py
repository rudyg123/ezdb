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
        self.nextrely += 3  # Extra padding

        # Add session options and save the selected value

        self.db = self.add(npyscreen.TitleSelectOne, max_height=4,
                                     name="Choose Database Type:", value = [0,],
                                     values = ["postgreSQL", "MySQL"],
                                     scroll_exit=True)


        #npyscreen.notify_confirm(self.parentApp.dbtype)
        #self.parentApp.dbtype = 'test2'
        #npyscreen.notify_confirm(self.parentApp.dbtype)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")



    def on_ok(self):
        #For debugging:
        #npyscreen.notify_confirm("You selected " + str(self.db.value[0]))
        self.parentApp.dbtype = self.db.value[0]
        self.parentApp.setNextForm("Connect_DBMS")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
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
        # TODO: Use a widget that makes it more obvious that input is required, i.e. BoxTitle
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
            self.parentApp.mydb = pdb.Postgres_Database()
            self.parentApp.mydb.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value, self.parentApp.port.value,
                                             self.parentApp.username.value, self.parentApp.password.value)
        elif self.parentApp.dbtype == 1:
            self.parentApp.mydb = mdb.MySQL_Database()
            self.parentApp.mydb.connect_DBMS(self.parentApp.dbtype, self.parentApp.host.value, self.parentApp.port.value,
                                             self.parentApp.username.value, self.parentApp.password.value)

        self.parentApp.setNextForm("Database_Window")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class Database_Window(npyscreen.FormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1, scroll_exit=True)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.dblist = self.parentApp.mydb.list_databases()

        self.nextrely += 1  # Move down

        if self.parentApp.dbtype == 0:
            self.dbtype_str = "PostgreSQL"
        elif self.parentApp.dbtype == 1:
            self.dbtype_str = "MySQL"

        self.add(npyscreen.TitleSelectOne, w_id="wActiveDB", max_height=10,
                             name="{} Databases:".format(self.dbtype_str), value = [0,],
                             values = self.dblist, scroll_exit=True)

        self.add(OpenDB_Button, name="Open Selected Database", rely=12)
        self.add(CreateDB_Button, name="Create Database", rely=13)

        self.add(npyscreen.TitleText, w_id="wNewDB_name", name="Enter New DB Name:",
                                   rely=14, relx=6, begin_entry_at=22, use_two_lines=False)

        self.add(DeleteDB_Button, name="Delete Database", rely=15)

        self.nextrely += 4  # Move down
        self.add(npyscreen.BoxTitle, w_id="tableresults_box", name="Database Tables", values=self.parentApp.tablelist, max_width=50,
                                    max_height=10, scroll_exit=True, hidden=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

class Tables_Window(npyscreen.FormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the TABLES window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

class Query_Window(npyscreen.FormWithMenus):
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

class RawSQL_Window(npyscreen.FormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, None

    def create(self):
        self.tabDatabases = self.add(Tab_DatabaseButton, w_id="wDatabaseTab", name="Databases", value="Database_Window", rely=1)
        self.tabTables = self.add(Tab_TablesButton, w_id="wTablesTab", name="Tables", value="Tables_Window", rely=1, relx=15)
        self.tabQuery = self.add(Tab_QueryButton, w_id="wQueryTab", name="Query", value="Query_Window", rely=1, relx=25)
        self.tabRawSQL = self.add(Tab_RawSQLButton, w_id="wRawSQLTab", name="Raw SQL", value="RawSQL_Window", rely=1, relx=34)
        self.tabExport = self.add(Tab_ExportButton, w_id="wExportTab", name="Export", value="Export_Window", rely=1, relx=45)
        self.tabAdmin = self.add(Tab_AdminButton, w_id="wAdminTab", name="Admin", value="Admin_Window", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        self.add(npyscreen.FixedText, value="Here is the RAW SQL window", editable=False)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

class Export_Window(npyscreen.FormWithMenus):
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

class Admin_Window(npyscreen.FormWithMenus):
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
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
        if exiting:
            self.parent.parentApp.switchForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        return

class OpenDB_Button(npyscreen.ButtonPress):
    def whenPressed(self):

        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        self.parent.parentApp.mydb.connect_database(self.parent.parentApp.active_db)
        self.parent.parentApp.tablelist = self.parent.parentApp.mydb.list_database_tables()

        self.parent.get_widget("tableresults_box").values = self.parent.parentApp.tablelist
        self.parent.get_widget("tableresults_box").hidden = False
        self.parent.get_widget("tableresults_box").display()

        #npyscreen.notify_confirm("The active db is " + str(self.parent.parentApp.active_db))
        #npyscreen.notify_confirm("The tablelist is " + str(self.parent.parentApp.tablelist))
        return self.parent.parentApp.tablelist

class CreateDB_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        self.newDB_name = self.parent.get_widget("wNewDB_name").value
        self.parent.parentApp.mydb.create_database(self.newDB_name)
        self.parent.get_widget("wActiveDB").display()
        return

class DeleteDB_Button(npyscreen.ButtonPress):
    def whenPressed(self):
        #self.parent.parentApp.mydb.connect_database()
        self.parent.parentApp.active_db = self.parent.get_widget("wActiveDB").get_selected_objects()[0]
        self.parent.parentApp.mydb.delete_database(self.parent.parentApp.active_db)
        self.parent.get_widget("wActiveDB").display()
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

    mydb = None
    active_db = None
    tablelist = None

    def onStart(self):

        # Declare all the forms that will be used within the app
        self.addFormClass("MAIN", Initial, name="Welcome to ezdb")
        self.addFormClass("Connect_DBMS", Connect_DBMS, name = "ezdb DBMS Connection Page")
        self.addFormClass("Database_Window", Database_Window, name = "ezdb Database Page")
        self.addFormClass("Tables_Window", Tables_Window, name = "ezdb Tables Page")
        self.addFormClass("Query_Window", Query_Window, name = "ezdb Query Page")
        self.addFormClass("RawSQL_Window", RawSQL_Window, name = "ezdb Raw SQL Page")
        self.addFormClass("Export_Window", Export_Window, name = "ezdb Export Page")
        self.addFormClass("Admin_Window", Admin_Window, name = "ezdb Admin Page")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()

