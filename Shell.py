#!/usr/bin/env python

import cmd
import json
from getpass import getpass
import secrets
import string
import pyperclip

class KryPiShell(cmd.Cmd):
    intro = "Welcome to KryPi. Type 'help' for a list of commands.\n"
    prompt = "KryPi> "
    file = None
    json_data = [{"id": 1, "source": "test2.example", "password": "453", "username": "evz6en", "title": "komini"}]
    IDs = []
    Titles = []
    is_authenticated = False
    socket = None

    # Function that add Users data infor memory for user to work with them.
    def add_data(self,data):
        self.json_data = json.loads(data)
        self.edit_ids()
        
    # Function that updates list of available IDs and Titles.
    def edit_ids(self):
        self.IDs = []
        self.Titles = []
        for i in self.json_data:
            temp = int(i["id"])
            self.IDs.append(temp)
        for i in self.json_data:
            self.Titles.append(i["title"]) 
        
    def retrieve_data(self):
        return self.json_data
         
    # Function for adding entries.
    # lets you add new entries, with basic informations
    # Title, Username, Password, Source, ID
    def do_add(self, arg):
        """Add a new entry
        add [title]"""
        self.edit_ids()
        try:
            if arg:  title = arg
            else:    title = input("Enter title: ")
            if len(title) == 0 and title in self.Titles:
                print("Entry with that title already exists")
            else:
                while True:
                    username = input("Enter username: ")
                    if len(username) == 0:
                        continue
                    source = input("Enter source: ")
                    if len(source) == 0:
                        continue
                    generate = input("Do you want to generate password? [n/y]: ")
                    if generate.lower() == 'y':
                        delka = input("how many characters to generate?: ")
                        delka = int(delka)
                        if delka == 0:
                            continue
                        password = generate_password(delka)
                        break
                    elif generate.lower() == 'n':
                        password = getpass("Enter password: ")
                        break
                    else:
                        print("Enter correct value")
                print(f"""
                    --------------------------------
                    Title: {title}
                    Username: {username}
                    Source: {source}
                    Password: *********
                    --------------------------------     
                    """)
                show = input("Show with password? [N/y]: ")
                if show == "y" or show == "Y":
                            print(f"""
                    --------------------------------
                    Title: {title}
                    Username: {username}
                    Source: {source}
                    Password: {password}
                    --------------------------------     
                    """)
                largest_id = 0
                largest_id = self.IDs[-1]
                newEntry = {"title": title, "id":largest_id + 1,"username":username, "password":password, "source":source}
                
                choice = input("Final - are credentials right? [Y/n]: ")
                if choice.lower() == "n":
                    print("Please enter again")
                else:
                    self.json_data.append(newEntry)
                    print("Entry added\n")
                    for i in self.json_data:
                        print(str(i["id"])  +"  " + str(i["title"]))
        except KeyboardInterrupt:
            print("Canceled...")
                 
    # Function for showing data entries
    # It prints out specified entry.
    # be careful - password is also shown
    def do_show(self, arg):
        """Get a password entry
            get [id] or get [title]
        """
        self.edit_ids()
        try:
            if arg:  arg = arg
            else:    arg = input("Enter ID or title to show: ")
            
            pr = input("Password will show, Do you want to continue [N/y]: ")
            if pr.lower() == "n":
                print("Entry not shown.")
            else:
                try:
                    id = int(arg)
                    index = self.IDs.index(id)
                except ValueError:
                    index = self.Titles.index(arg)
                
                entry = self.json_data[index]
                print(f"""
                --------------------------------
                Title: {entry["title"]}
                Username: {entry["username"]}
                Source: {entry["source"]}
                Password: {entry["password"]}
                --------------------------------     
                """)
             
        except KeyboardInterrupt:
            print("Canceled...")

    # Function for listing all current entries 
    # it lists only id and title.
    def do_list(self, arg):
        """ List all password entries, it's titles"""
        self.edit_ids()
        if len(self.json_data) == 0:
            print("You have no entries yet.")
        else:
            print("Printing entries of passwords...")
            for i in self.json_data:
                print( str(i["id"])  +"  " + str(i["title"]))
        
    # Function for editing users entries.
    # This function lets you edit your entries. 
    # When you dont want to change anything, leave the variable empty and press ENTER.      
    def do_edit(self, arg):
        """ Edit password entry
            edit [id] or edit [title]
            Can edit in CLI or in notepad(on windows) [L/e] 
        """
        self.edit_ids()
        try:
            if arg:  arg = arg
            else:    arg = input("Enter ID or title to edit: ")
            try:
                id = int(arg)
                if id in self.IDs:
                    index = self.IDs.index(id)
            except:
                if arg in self.Titles:
                    index = self.Titles.index(arg)
            entry = self.json_data[index]
            print(f"""
                --------------------------------
                Title: {entry["title"]}
                Username: {entry["username"]}
                Source: {entry["source"]}
                Password: {entry["password"]}
                --------------------------------     
                """)
            title = input("Title: ")
            username = input("Username: ")
            password = getpass("Password: ")
            source = input("Source: ")

            if title != "":  self.json_data[index]['title'] = title
            if username != "":  self.json_data[index]['username'] = username
            if password != "":  self.json_data[index]['password'] = password
            if source != "":    self.json_data[index]['source'] = source
                
        except KeyboardInterrupt:
            print("Canceled...")

    # Function for deleting users entries.
    # Remaining entry IDs are reordered so it's nice in order
    def do_delete(self, arg):
        """ Delete password entry
            delete [id] or delete [title]
        """
        self.edit_ids()
        try:
            if arg: arg = arg
            else:   arg = input("Enter ID or title to delete: ")
            try:
                id = int(arg)
                if id in self.IDs:
                    index = self.IDs.index(id)
                    self.json_data.pop(index)
            except ValueError:
                if arg in self.Titles:
                    index = self.Titles.index(arg)
                    self.json_data.pop(index)
            for index, passwords in enumerate(self.json_data):
                passwords['id'] = index+1

            for i in self.json_data:
                print( str(i["id"])  +"  " + str(i["title"]))
        except KeyboardInterrupt:
            print("Canceled...")

    # This function gets entry and saves its password into clipboard without showing it on screen
    def do_get(self,arg):
        """ Copy password to clipboard without showing it"""
        self.edit_ids()
        print(self.IDs)
        if arg in self.Titles or int(arg) in self.IDs:  
            try:
                id = int(arg)
                for entry in self.json_data:
                    if entry["id"] == id:
                        pyperclip.copy(entry["password"])
            except ValueError:
                for entry in self.json_data:
                    if entry['title'] == arg:
                        pyperclip.copy(entry["password"])
        else:
            print("No entry with that name or ID")
        
    # function which exits out of KryPi shell
    def do_end(self, arg):
        """Exit KryPi"""
        print("Exiting KryPi...")
        return True
    
    # Function for when user presses enter on empty line        
    def emptyline(self):
         pass

# Function for generating new passwords
def generate_password(delka):
    pwd = ""
    for i in range(delka):
        pwd += ''.join(secrets.choice(string.ascii_letters + string.digits +string.punctuation))
    return pwd
