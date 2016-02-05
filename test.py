#!/usr/bin/env python

import npyscreen

# class FormObject(npyscreen.Form):
#     def create(self):
#         # Reposition the form so it's centered in a stanard terminal window
#         self.show_atx = 20
#         self.show_aty = 3

#         self.add(npyscreen.TitleText, name = "First Name: ")
#         self.nextrely += 1 # Adds a space between fields
#         #self.nextrelx += 3 # Adds some indentation for sub-items
#         self.add(npyscreen.TitleText, name = "Last Name: ")

#     def afterEditing(self):
#         # On submitting this form, exit (don't go to another form)
#         self.parentApp.setNextForm(None)

# # Splits the form with a horizontal line in a specified location
# class FormObject(npyscreen.SplitForm):
#     def create(self):
#         # Reposition the form so it's centered in a stanard terminal window
#         self.show_atx = 20
#         self.show_aty = 3

#         self.add(npyscreen.TitleText, name = "First Name: ")

#     def afterEditing(self):
#         # On submitting this form, exit (don't go to another form)
#         self.parentApp.setNextForm(None)

# ActionForm includes "Cancel" in addition to "OK"
class FormObject(npyscreen.ActionForm, npyscreen.SplitForm, npyscreen.FormWithMenus):
    def create(self):
        # Reposition the form so it's centered in a stanard terminal window
        self.show_atx = 20
        self.show_aty = 3

        # Add some widgets
        self.firstName = self.add(npyscreen.TitleText, name = "First Name: ")
        self.lastName = self.add(npyscreen.TitleText, name = "Last Name: ")

        # Add a menu
        self.menu = self.new_menu(name = "Main Menu")
        self.menu.addItem("Item 1", self.press_1, "1")
        self.menu.addItem("Item 2", self.press_2, "2")
        self.menu.addItem("Exit Form", self.exit_form, "^X")

        self.submenu = self.menu.addNewSubmenu("A Sub Menu!")
        self.submenu.addItem("Woo! Subscribe! pl0x")

    def press_1(self):
        npyscreen.notify_confirm("You pressed Item 1!", "Item 1", editw = 1)
        npyscreen.blank_terminal()

    def press_2(self):
        npyscreen.notify_confirm("You pressed Item 2!", "Item 2", editw = 1)
        npyscreen.blank_terminal()

    def exit_form(self):
        #self.parentApp.switchForm(None)
        npyscreen.blank_terminal()

    # def afterEditing(self):
    #     # On submitting this form, exit (don't go to another form)
    #     self.parentApp.setNextForm(None)

    def on_ok(self):
        npyscreen.notify_confirm("Form has been saved!", "Saved!", editw = 1)

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to cancel?", "Positive?", editw = 1)
        if (exiting):
            npyscreen.notify_confirm("Form has not been saved. Good bye!", "Goodbye!", editw = 1)
            self.parentApp.setNextForm(None)
        else:
            npyscreen.blank_terminal() # clears the notification and just goes back to the original form
        #     npyscreen.notify_confirm("You may continue working.", "Okay!", editw = 1)

# NPSAppManaged provides a framework to start and end the application
# Manages the display of the various Forms we have created
class App(npyscreen.NPSAppManaged):
    def onStart(self):
        # Show the starting form; resize so it's not full screen
        self.addForm("MAIN", FormObject, name = "npyscreen Form!", lines = 10, columns = 40, draw_line_at = 7)

if (__name__ == "__main__"):
    # Start an NPSAppManaged application mainloop
    # Activates the default form which has a default ID of "MAIN"
	app = App().run()