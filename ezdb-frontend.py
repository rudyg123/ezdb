#!/usr/bin/env python
# encoding: utf-8

import npyscreen as npy
import postgres_db as pdb
import mysql_db as mdb

#global dbtype, conn_new_or_existing

# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application
class ezdbApp(npy.NPSAppManaged):

    def onStart(self):
        self.addForm("MAIN", DBMS_Form, name = 'Welcome to ezdb')
        self.addForm("ConnectDB_Form", ConnectDB_Form, name = 'ezdb open database')
        self.addForm("CreateDB_Form", CreateDB_Form, name = 'ezdb create database')

class DBMS_Form(npy.Form):

    DEFAULT_LINES = 15
    def create(self):
        #global dbtype, conn_new_or_existing

        self.add(npy.FixedText, value = "Connect to Database System", editable = 'false')

        self.dbtype = self.add(npy.TitleSelectOne, max_height=4,
                                     name="Choose Database Type:", value = [0,],
                                     values = ["postgreSQL", "MySQL"],
                                     scroll_exit=True)

        self.add(npy.FixedText, value = "Enter Connection Settings:")

        self.host = self.add(npy.TitleText, name = "Host:",)
        self.port = self.add(npy.TitleText, name = "Port:",)

        self.username = self.add(npy.TitleText, name = "Username:",)
        self.password = self.add(npy.TitlePassword, name = "Password:", type = 'password')

    def beforeEditing(self):
        self.host.value = 'localhost'

    def while_editing(self, *args, **keywords):
        if self.dbtype.value[0] == 0:
            self.port.value = '5432'
            self.username.value = 'postgres'

        elif self.dbtype.value[0] == 1:
            self.port.value = '3306'
            self.username.value = 'root'

        self.port.display()
        self.username.display()


    def afterEditing(self):

        global mydb

        #connects to DBMS
        if self.dbtype.value[0] == 0:
            mydb = pdb.Postgres_Database(self.dbtype.value, self.host.value, self.port.value, self.username.value, self.password.value)
        elif self.dbtype.value[0] == 1:
            mydb = mdb.MySQL_Database(self.dbtype.value, self.host.value, self.port.value, self.username.value, self.password.value)

        self.parentApp.setNextForm("ConnectDB_Form")

class ConnectDB_Form(npy.Form):

    def create(self):

        conn_new_or_existing = self.add(npy.TitleSelectOne, max_height=4,
                                             name="Choose:",
                                             values = ["Open Existing Database","Create New Database"],
                                             scroll_exit=True)
        self.add(npy.TitleText, name = "Database Name:",)

    def afterEditing(self):

        self.parentApp.setNextForm(None)

class CreateDB_Form(npy.Form):

    def create(self):
        self.add(npy.FixedText, value = "Create DB Form created!")

    def afterEditing(self):
        self.parentApp.setNextForm(None)

if __name__ == "__main__":
    App = ezdbApp().run()




'''
    def main-backup(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F  = npyscreen.Form(name = "Welcome to ezdb",)
        t  = F.add(npyscreen.TitleText, name = "Text:",)
        fn = F.add(npyscreen.TitleFilename, name = "Filename:")
        fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
        dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
        s  = F.add(npyscreen.TitleSlider, out_of=12, name = "Slider")
        ml = F.add(npyscreen.MultiLineEdit,
               value = """try typing here!\nMutiline text, press ^R to reformat.\n""",
               max_height=5, rely=9)
        ms = F.add(npyscreen.TitleSelectOne, max_height=4, value = [1,], name="Pick One",
                values = ["Option1","Option2","Option3"], scroll_exit=True)
        ms2= F.add(npyscreen.TitleMultiSelect, max_height =-2, value = [1,], name="Pick Several",
                values = ["Option1","Option2","Option3"], scroll_exit=True)

        # This lets the user interact with the Form.
        F.edit()

        print(ms.get_selected_objects())
'''