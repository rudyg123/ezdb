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

        self.parentApp.setNextForm("SessionWindow")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class SessionWindow(npyscreen.SplitFormWithMenus):
    tabDatabases, tabTables, tabQuery, tabRawSQL, tabExport, tabAdmin, tabExit = None, None, None, None, None, None, \
                                                                                 None

    def create(self):
        self.tabDatabases = self.add(npyscreen.ButtonPress, name="Databases", rely=1)
        self.tabTables = self.add(npyscreen.ButtonPress, name="Tables", rely=1, relx=15)
        self.tabQuery = self.add(npyscreen.ButtonPress, name="Query", rely=1, relx=25)
        self.tabRawSQL = self.add(npyscreen.ButtonPress, name="Raw SQL", rely=1, relx=34)
        self.tabExport = self.add(npyscreen.ButtonPress, name="Export", rely=1, relx=45)
        self.tabAdmin = self.add(npyscreen.ButtonPress, name="Admin", rely=1, relx=55)
        self.tabExit = self.add(ExitButton, name="Exit", rely=1, relx=64)

        #self.mydb = self.parentApp.getForm("Connect_DBMS").mydb
        self.dblist = self.parentApp.mydb.list_databases()

        self.nextrely += 1  # Move down
        self.selectdb = self.add(npyscreen.TitleSelectOne, max_height=10,
                             name="Open Database:", value = [0,],
                             values = self.dblist, scroll_exit=True)

        #self.add(npyscreen.Pager, values = self.dblist, max_width=50, max_height=10)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):
        #For debugging:
        #npyscreen.notify_confirm("You selected " + str(self.db.value[0]))
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form

class ExitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
        if exiting:
            self.parent.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
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

    def onStart(self):

        # Declare all the forms that will be used within the app
        self.addFormClass("MAIN", Initial, name="Welcome to ezdb")
        self.addFormClass("Connect_DBMS", Connect_DBMS, name = "ezdb connect to DBMS")
        self.addFormClass("SessionWindow", SessionWindow, name = "ezdb main db menu")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()

