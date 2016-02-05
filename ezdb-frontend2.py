#!/usr/bin/env python

import npyscreen

__author__ = 'bobby'


# ActionForm includes "Cancel" in addition to "OK"
class FormObject(npyscreen.ActionFormWithMenus):

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
            npyscreen.notify_confirm("You selected \"Open Existing Database\"", "Open Existing Database", editw=1)
        elif self.sessionType.value[0] == 1:
            npyscreen.notify_confirm("You selected \"Create New Database\"", "Create New Database", editw=1)

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
        # Show the starting form; resize so it's not full screen
        self.addForm("MAIN", FormObject, name="Welcome to ezdb")

if __name__ == "__main__":
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
    app = App().run()
