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


    """
    Description: Function used to add received users data from server to memory
    Parameters: json : data -> users vault data, which contains his entries.
    """
    def add_data(self,data):
        self.json_data = json.loads(data)
        self.edit_ids()
        
    """
    Description: Function used edit list variables for searching and finding entries.
    """
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
         
    """
    Description: Function used for adding entries to users vault.
    Parameters: One entry contains these information: Username, Password, Title of entry, Source and ID.
    """
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

    """
    Description: Function used to show users entry on screen.
    Parameters: str/int : arg -> either ID or title of entry which will be shown
    """
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

    """
    Description: Function used to list all current users entries inside his vault.
                It lists only Id and title of users entries.
    Parameters: None
    """
    def do_list(self,arg):
        """ List all password entries, it's titles"""
        self.edit_ids()
        if len(self.json_data) == 0:
            print("You have no entries yet.")
        else:
            print("Printing entries of passwords...")
            for i in self.json_data:
                print( str(i["id"])  +"  " + str(i["title"]))
        

    """
    Description: Function used to edit existing users entries.
                 User can all four information of entry - Username,Password,Title,Source.
                 If no change is wanted, leave the field empty and press ENTER.
    Parameters: str/int : arg -> ID or Title of entry to be edited.
    """
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

    """
    Description: Function used to delete entries from users vault.
                 ID's or remaining entries will be reordered to be in order beginning from 1.
    Parameters: str/int : arg -> ID or Title of entry to be deleted.
    """
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

    """
    Description: Function used to copy entry password into clipboard without showing it on screen.
    Parameters: str/int : arg -> ID or Title of entry's password to be copied into clipboard.
    """
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
        
    """
    Description: Function used exit from KryPi shell.
    Parameters: None
    """
    def do_end(self, arg):
        """Exit KryPi"""
        print("Exiting KryPi...")
        return True
    
    
    """
    Description: Function used to when user presses enter on empty or wrong command.
    """    
    def emptyline(self):
         pass


"""
Description: Function used for generating users password when choosen.
             Generated Letters, Numbers and Special characters.
Parameters: int : length -> Length of generated password.
"""
def generate_password(length):
    pwd = ""
    for i in range(length):
        pwd += ''.join(secrets.choice(string.ascii_letters + string.digits +string.punctuation))
    return pwd



if __name__ == '__main__':
    krypi = KryPiShell()
    krypi.cmdloop()