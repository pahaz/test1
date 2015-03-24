import shelve
import model


class Manager:
    def __init__(self, db_name):
        self._db = shelve.open(db_name)

    def all(self):
        messages = []
        for id_, data in self._db.items():
            m = model.Message(data['name'], data['message'])
            m.id = id_
            messages.append(messages)
        return messages

    def save(self, message):
        data = {
            'message': message.message,
            'name': message.name
        }
        if message.id:
            self._db[message.id] = {
                'message': message.message,
                'name': message.name
            }
        else:
            max_id = max(self._db.keys())
            self._db[max_id + 1] = data
        self._db.sync()

    def delete(self, message):
        if message.id:
            del self._db[message.id]
            self._db.sync()
            return True
        return False

    def filter_by_name(self, name):
        return [m for m in self.all() if m.name == name]

    def close(self):
        self._db.close()