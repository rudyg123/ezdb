#!/usr/bin/env python

import npyscreen

__author__ = 'bobby'


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
        self.sessionType = self.add(npyscreen.SelectOne, values=["Open Existing Database", "Create New Database"],
                                    scroll_exit=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")

    def on_ok(self):
        if self.sessionType.value[0] == 0:
            self.parentApp.setNextForm("ConnectToExistingDatabase")
        elif self.sessionType.value[0] == 1:
            self.parentApp.setNextForm("CreateNewDatabase")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Are you sure?", editw=1)
        if exiting:
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form


class ConnectToExistingDatabase(npyscreen.ActionFormWithMenus, npyscreen.SplitForm):
    storedConnections = None

    def create(self):
        self.storedConnections = self.add(npyscreen.BoxTitle, name="Stored Connections:", max_height=4,
                                          scroll_exit=True)
        # TODO: These are hardcoded. They need to be stored locally somehow (text file?)
        self.storedConnections.values = ["1. First stored connection",
                                         "2. Second stored connection",
                                         "3. Third stored connection"]
        self.nextrely += 2  # Move down
        # TODO: Use a widget that makes it more obvious that input is required, i.e. BoxTitle
        self.add(npyscreen.TitleText, name="Hostname:")
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="Port:")
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="DB Name:")
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="Username:")
        self.nextrely += 1  # Move down
        self.add(npyscreen.TitleText, name="Password:")

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


class CreateNewDatabase(npyscreen.ActionFormWithMenus):
    def create(self):
        self.add(npyscreen.FixedText, value="Yay you made it to the create new form!", editable=True)

        # Add a menu
        menu = self.new_menu(name="Help Menu")
        menu.addItem("Some helpful guidance here.")


# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):
    def onStart(self):
        # Declare all the forms that will be used within the app
        self.addForm("MAIN", Initial, name="Welcome to ezdb")
        self.addForm("ConnectToExistingDatabase", ConnectToExistingDatabase, name="Connect to an Existing Database",
                     draw_line_at=6)
        self.addForm("CreateNewDatabase", CreateNewDatabase, name="Create a New Database")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()
