#!/usr/bin/env python

import npyscreen
import curses

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

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):
        #For debugging:
        #npyscreen.notify_confirm("You selected " + str(self.db.value[0]))
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

        dbtype = self.parentApp.getForm("MAIN").db.value[0]
        self.port = ''
        self.username = ''
        self.password = ''

        #set default DBMS connection values
        #For debugging:
        #npyscreen.notify_confirm("The value of dbtype in ConectDBMS is " + str(dbtype))
        if dbtype == 0:
            self.add(npyscreen.FixedText, value="Enter PostgreSQL Database System Connection Settings:", editable=False)
            self.port = '5432'
            self.username = 'postgres'
            self.password = 'password'
        elif dbtype == 1:
            self.add(npyscreen.FixedText, value="Enter MySQL Database System Connection Settings:", editable=False)
            self.port = '3306'
            self.username = 'root'
            self.password = 'password'

        self.nextrely += 2  # Move down
        # TODO: Use a widget that makes it more obvious that input is required, i.e. BoxTitle
        self.add(npyscreen.TitleText, name="Hostname:", value="127.0.0.1")
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="Port:", value=self.port)
        #self.nextrely += 1  # Move down
        #self.add(npyscreen.TitleText, name="DB Name:")
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="Username:", value=self.username)
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="Password:", value=self.password)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):

    def onStart(self):

        # Declare all the forms that will be used within the app
        self.addForm("MAIN", Initial, name="Welcome to ezdb")
        self.addFormClass("Connect_DBMS", Connect_DBMS, name = "ezdb connect to DBMS")
        #self.addForm("ConnectToExistingDatabase", ConnectToExistingDatabase, name="Connect to an Existing Database",
        #             draw_line_at=6)
        #self.addForm("CreateNewDatabase", CreateNewDatabase, name="Create a New Database")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()

