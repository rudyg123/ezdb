#!/usr/bin/env python
# encoding: utf-8

import npyscreen as npy
import postgres_db as pdb
import mysql_db as mdb
import settings

# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application
class ezdbApp(npy.NPSAppManaged):

    def onStart(self):
        self.mydb = pdb.Postgres_Database()
        self.addForm("MAIN", DBMS_Form, name = 'Welcome to ezdb')
        self.addForm("ConnectDB_Form", ConnectDB_Form, name = 'ezdb open database')
        self.addForm("CreateDB_Form", CreateDB_Form, name = 'ezdb create database')

class DBMS_Form(npy.Form, settings.Settings):

    def create(self):

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

        self.mydb = pdb.Postgres_Database(self.dbtype.get_selected_objects()[0], self.host.value, self.port.value,
                                          self.username.value, self.password.value)
        self.mydb.connect_database('postgres')

        self.parentApp.setNextForm("ConnectDB_Form")


class ConnectDB_Form(npy.Form, settings.Settings):

    def create(self):

        self.add(npy.FixedText, value=self.parentApp.mydb.dbtype + ' Database Type')
        self.conn_new_or_existing = self.add(npy.TitleSelectOne, name="Choose:",
                                             values = ["Create New Database", "Open Existing Database"],
                                             scroll_exit=True, max_height=5)

        self.new_dbname = self.add(npy.TitleText, name = "New Database:",)
        dblist = self.parentApp.mydb.list_databases()
        self.add(npy.TitleMultiLine, name = "Or Open Database:", values=dblist, max_width=50, max_height=10, scroll_exit=True)

        #self.add(npy.Pager, values = dblist[0], max_width=50, max_height=10)



    def afterEditing(self):

        if self.conn_new_or_existing.get_selected_objects()[0] == "Create New Database":
            self.parentApp.mydb.create_database(self.new_dbname.value)

        self.parentApp.setNextForm("ConnectDB_Form")

class CreateDB_Form(npy.Form):

    def create(self):
        self.add(npy.FixedText, value = "Create DB Form created!")

    def afterEditing(self):
        self.parentApp.setNextForm(None)

if __name__ == "__main__":
    App = ezdbApp().run()

