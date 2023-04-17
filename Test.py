#!/usr/bin/env python

import cmd
import subprocess
import json
from getpass import getpass
import secrets
import string
import pyperclip
from Client_ReadFace import FaceCapturer
import Client_DetectFace


def is_authorized(func):
    """Get a password entry
        add [title]"""
    def wrapper(self, line):
        if self.is_authenticated:
            return func(self, line)
        else:
            print("You are not authorized to execute this command.")
    return wrapper



class KryPiShell(cmd.Cmd):
    intro = "Welcome to KryPi. Type 'help' for a list of commands.\n"
    prompt = "KryPi> "
    file = None
    json_data = None
    IDs = []
    Titles = []
    is_authenticated = False
    socket = None


    
    def add_data(self,data):
        self.json_data = json.loads(data)
        self.edit_ids()
        
    def edit_ids(self):
        for i in self.json_data:
            self.IDs.append(int(i["id"]))
        for i in self.json_data:
            self.Titles.append(i["title"]) 
        print(self.IDs)
        print(self.Titles)
        
        
        
        
        
    def retrieve_data(self):
        return self.json_data
        
        
###             ADD  #################################################
    def do_add(self, arg):
        """Get a password entry
        add [title]"""
        try:
            if arg:  title = arg
            else:    title = input("Title name: ")
            if title in self.Titles:
                print("Entry with that title already exists")
            else:
                username = input("Enter username: ")
                gen = True
                while gen:
                    generate = input("Do you want to generate password? [n/y]: ")
                    if generate.lower() == 'y':
                        delka = input("how many characters to generate?: ")
                        delka = int(delka)
                        password = generate_password(delka)
                        gen = False
                    elif generate.lower() == 'n':
                        password = getpass("Enter password: ")
                        gen = False
                    else:
                        print("Enter correct value")
                source = input("Enter source: ")
                
                print(f"""
                    --------------------------------
                    Title: {title}
                    Username: {username}
                    Source: {source}
                    Password: *********
                    --------------------------------     
                    """)
                show = input("do you want to show input with password? [N/y]: ")
                if show == "y" or show == "Y":
                            print(f"""
                    --------------------------------
                    Title: {title}
                    Username: {username}
                    Source: {source}
                    Password: {password}
                    --------------------------------     
                    """)
                choice = input("Final - are credentials right? [Y/n]: ")
            if title not in self.Titles:               
                largest_id = 0
                for passwords in self.json_data:
                    password_id = passwords.get('id')
                    if (password_id is not None) and (largest_id is None or password_id > largest_id):
                        largest_id = password_id
                newEntry = {"title": title, "id":largest_id + 1,"username":username, "password":password, "source":source}
                
                if choice.lower() == "n":
                    print("Please enter again")
                else:
                    self.json_data.append(newEntry)
                    print("Entry added\n -----------")
                    for i in self.json_data:
                        print(str(i["id"])  +"  " + str(i["title"]))
                self.edit_ids()
        except KeyboardInterrupt:
            print("Canceled...")
            
            
            
###             SHOW  #################################################
    
    def do_show(self, arg):
        """Get a password entry
            get [id] or get [title]
        """
        try:
            if arg:  arg = arg
            else:    arg = input("Enter ID or title to show: ")
            
            print("!!!THE PASSWORD WILL BE PRINTED!!!")
            pr = input("IF YOU DONT WANT TO CONTINUE PRESS [N/n]: ")
            if pr.lower() == "n":
                print("Entry not shown")
            else:
                try:
                    id = int(arg)
                    for i in self.json_data:
                        if i["id"] == id:   
                            print(f"""
                            --------------------------------
                            Title: {i["title"]}
                            Username: {i["username"]}
                            Source: {i["source"]}
                            Password: {i["password"]}
                            --------------------------------     
                            """)
                except ValueError:
                    for i in self.json_data:
                        if i["title"] == arg:   
                            print(f"""
                            --------------------------------
                            Title: {i["title"]}
                            Username: {i["username"]}
                            Source: {i["source"]}
                            Password: {i["password"]}
                            --------------------------------     
                            """)
        except KeyboardInterrupt:
            print("Canceled...")

###             LIST  #################################################
    def do_list(self, arg):
        """ List all password entries, it's titles"""
        print("Printing entries of passwords...")
        for i in self.json_data:
            print( str(i["id"])  +"  " + str(i["title"]))
        
        
###             EDIT  #################################################        
    def do_edit(self, arg):
        """ Edit password entry
            edit [id] or edit [title]
            Can edit in CLI or in notepad(on windows) [L/e] 
        """
        try:
            if arg:  arg = arg
            else:    arg = input("Enter ID or title to edit: ")
            
            try:
                id = int(arg)
                for i in self.json_data:
                    if i["id"] == id:   
                        print(f"""
                        --------------------------------
                        Title: {i["title"]}
                        Username: {i["username"]}
                        Source: {i["source"]}
                        Password: ***********
                        --------------------------------     
                        """)
                username = input("Username: ")
                password = getpass("Password: ")
                source = input("Source: ")

            except ValueError:
            
                for i in self.json_data:
                    if i["title"] == arg:   
                        print(f"""
                        --------------------------------
                        Title: {i["title"]}
                        Username: {i["username"]}
                        Source: {i["source"]}
                        Password: *************
                        -------------------------------- """)
                username = input("Username: ")
                password = getpass("Password: ")
                source = input("Source: ")
                for passwords in self.json_data:
                    if passwords['title'] == arg:
                        if username != "":  passwords['username'] = username
                        if password != "":  passwords['password'] = password
                        if source != "":    passwords['source'] = source
                            
            self.edit_ids()
        except KeyboardInterrupt:
            print("Canceled...")


###             DELETE  #################################################
    def do_delete(self, arg):
        """ Delete password entry
            delete [id] or delete [title]
        """
        try:
            if arg: arg = arg
            else:   arg = input("Enter ID or title to delete: ")
            try:
                id = int(arg)
                for index, entry in enumerate(self.json_data):
                    if entry["id"] == id:
                        self.json_data.pop(index)
                    for index, passwords in enumerate(self.json_data):
                        passwords['id'] = index+1
            except ValueError:
                for index, entry in enumerate(self.json_data):
                    if entry["title"] == arg:
                        self.json_data.pop(index)
                    for index, passwords in enumerate(self.json_data):
                        passwords['id'] = index+1

            for i in self.json_data:
                print( str(i["id"])  +"  " + str(i["title"]))
            self.edit_ids()
        except KeyboardInterrupt:
            print("Canceled...")

###             GET  #################################################
    def do_get(self,arg):
        """ Copy password to clipboard without showing it"""
        try:
            id = int(arg)
            for entry in self.json_data:
                if entry["id"] == id:
                    pyperclip.copy(entry["password"])
        except ValueError:
            for passwords in self.json_data:
                if passwords['title'] == arg:
                    pyperclip.copy(entry["password"])
        
        
###             END  #################################################
    def do_end(self, arg):
        """Exit KryPi"""
        print("Exiting KryPi...")
        return True
    
    def emptyline(self):
         pass

    
    


def generate_password(delka):
    pwd = ""
    for i in range(delka):
        pwd += ''.join(secrets.choice(string.ascii_letters + string.digits +string.punctuation))
    return pwd
    



if __name__ == '__main__':

    data 

    krypi = KryPiShell()
    krypi.cmdloop()
    
    
    
