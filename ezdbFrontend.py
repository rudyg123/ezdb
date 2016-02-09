#!/usr/bin/env python

import npyscreen
import ezdbBackend

__author__ = 'bobby'


# TODO: Use this for global settings; Currently not being used
# Stores the config information specified by the user
class MySQLConfig:
    def __init__(self, hostname, port, dbName, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.dbName = dbName


# ActionForm includes "Cancel" in addition to "OK"
class Initial(npyscreen.ActionFormWithMenus):
    sessionDatabaseType = None

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
        self.nextrely += 2  # Extra padding
        self.add(npyscreen.FixedText, value="Select session type:", editable=False, relx=27)
        self.nextrely += 1  # Extra padding
        # Add session options and save the selected value
        self.sessionDatabaseType = self.add(npyscreen.SelectOne, values=["MySQL", "PostgreSQL"],
                                            scroll_exit=True, relx=30)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):
        if self.sessionDatabaseType.value[0] == 0:
            self.parentApp.setNextForm("ConnectToMySQL")
        elif self.sessionDatabaseType.value[0] == 1:
            self.parentApp.setNextForm("ConnectToPostgreSQL")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class ConnectToMySQL(npyscreen.ActionFormWithMenus, npyscreen.SplitForm):
    storedConnections, hostname, port, dbName, username, password, connectionStatus = None, None, None, None, None, \
                                                                                      None, None
    connectOrCreate = None

    def create(self):
        self.storedConnections = self.add(npyscreen.BoxTitle, name="Stored Connections:", max_height=4,
                                          scroll_exit=True)
        # TODO: These are hardcoded. They need to be stored locally somehow (text file?)
        # Selecting one should populate the form with everything except password
        self.storedConnections.values = ["1. First stored connection",
                                         "2. Second stored connection",
                                         "3. Third stored connection"]
        self.nextrely += 2  # Move down
        # TODO: Use a widget that makes it more obvious that input is required, i.e. BoxTitle
        self.hostname = self.add(npyscreen.TitleText, name="Hostname:", value="127.0.0.1")
        self.nextrely += 1  # Move down
        self.port = self.add(npyscreen.TitleText, name="Port:", value="3306")
        self.nextrely += 1  # Move down
        self.dbName = self.add(npyscreen.TitleText, name="DB Name:")
        self.nextrely += 1  # Move down
        self.username = self.add(npyscreen.TitleText, name="Username:", value="root")
        self.nextrely += 1  # Move down
        self.password = self.add(npyscreen.TitlePassword, name="Password:")
        self.nextrely += 1  # Move down
        self.connectOrCreate = self.add(npyscreen.TitleSelectOne, name="Action:", values=["Connect", "Create"],
                                        scroll_exit=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")

    def on_ok(self):
        # if self.dbType.value[0] == 0:
        #     self.connectionStatus = ezdbBackend.connectMySQL(self.hostname, self.port, self.dbName, self.username,
        #                                                        self.password)
        #     if self.connectionStatus == "Success":
        #         self.add(npyscreen.notify_confirm("MySQL Database Connection Established!", title="Success!", editw=1))
        #     # self.add(npyscreen.notify_wait("Opening MySQL connection.", title="Please wait"))
        #     else:
        #         self.add(npyscreen.notify_confirm("Failed to establish MySQL connection", title="Failure :(", editw=1))
        # elif self.dbType.value[0] == 1:
        #     self.add(npyscreen.notify_wait("Opening Postgres connection...", title="Please wait"))
        # else:
        #     self.add(npyscreen.notify_confirm("You must specify a database type to proceed.",
        #                                       title="Select Database Type", editw=1))
        self.parentApp.setNextForm("SessionWindow")
        pass


class ConnectToPostgreSQL(npyscreen.ActionFormWithMenus):
    def create(self):
        self.add(npyscreen.FixedText, value="This is the Connect to PostgreSQL Screen", editable=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):
        self.parentApp.setNextForm(None)
        pass


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
        self.tabExit = self.add(npyscreen.ButtonPress, name="Exit", rely=1, relx=64)



        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):
    # noinspection PyPep8Naming
    def onStart(self):
        # Declare all the forms that will be used within the app
        self.addForm("MAIN", Initial, name="Welcome to ezdb")
        self.addForm("ConnectToMySQL", ConnectToMySQL, name="Connect to a MySQL Database System",
                     draw_line_at=6)
        self.addForm("ConnectToPostgreSQL", ConnectToPostgreSQL, name="Connect to a PostgreSQL Database System")
        self.addForm("SessionWindow", SessionWindow, draw_line_at=2)

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()
