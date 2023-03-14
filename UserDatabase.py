import json


class UserDatabase:

    def __init__(self, db):
        self.db = db
        self._update_data()  # Updates metadata in json. (last_id, ...)

    def __len__(self):
        return len(self.db["entries"])

    def _update_data(self):
        self.db["last_id"] = max([entry["id"] for entry in self.db["entries"]])

    def add(self, entry):
        entry["id"] = self.db["last_id"] + 1
        self.db["entries"].append(entry)
        self.db["last_id"] += 1

    def add(self, source, password, username):
        self.db["entries"].append(
            {"id": self.db["last_id"] + 1, "source": source, "pass": password, "username": username})
        self.db["last_id"] += 1

    def count(self):
        return len(self.db["entries"])

    def delete(self, id):
        # TODO What if no souch entry?
        id = self.get_index(id)
        del self.db["entries"][id]

    def edit(self, id, username="", password="", source=""):
        # TODO What if no souch entry?
        entry = self.db["entries"][self.get_index(id)]
        if username:
            entry["username"] = username
        if password:
            entry["password"] = password
        if source:
            entry["source"] = source

    def export_data(self):
        return json.dumps(self.db)

    def find(self, word):
        return [entry for entry in self.db["entries"] if word in entry["source"] or word in entry["username"]]

    def find_source(self, word):
        return [entry for entry in self.db["entries"] if word in entry["source"]]

    def find_username(self, word):
        return [entry for entry in self.db["entries"] if word in entry["username"]]

    def get(self, id):
        return [entry for entry in self.db["entries"] if entry["id"] == id]

    def get_index(self, id):
        return next((index for (index, d) in enumerate(self.db["entries"]) if d["id"] == id), None)

    def import_data(self, data):
        self.db = json.loads(data)

    def list(self):
        return [entry["source"] for entry in self.db["entries"]]

    def read(self, source):
        return [entry for entry in self.db["entries"] if entry["source"] == source]


# tests
if __name__ == "__main__":
    db = {
        "version": 1,
        "last_id": 0,
        "entries": [
            {"id": 1, "source": "test.example", "pass": "123456", "username": "evzen"},
            {"id": 2, "source": "test1.example", "pass": "434", "username": "evz7en"},
            {"id": 3, "source": "test2.example", "pass": "453", "username": "evz6en"},
            {"id": 4, "source": "test1.example", "pass": "123", "username": "e5vzen"},
            {"id": 5, "source": "test2.example", "pass": "4534", "username": "evz2en"},
        ]}
    database = UserDatabase(db)
    database._update_data()
    print(database.list())
    print(database.read("test1.example"))
    database.add("evzenícek", "kominicek", "kroupy kroup")
    print(database.list())
    print(database.read("evzenícek"))
    print(len(database))
    database.delete(5)
    print(database.db)
    database.edit(4, username="popokatepetl_________")
    print(database.db)
