import shelve
import model


class Manager:
    def __init__(self, db_path):
        self._db = shelve.open(db_path)

    def get_all(self):
        entries = []
        for m_id, entry in self._db.items():
            e = model.Entry(entry['name'], entry['message'])
            e.m_id = int(m_id)
            entries.append(e)
        return sorted(entries, key=lambda e: e.m_id)

    def save(self, entry):
        m_id = str(entry.m_id or
                   max((int(key) + 1 for key in self._db.keys()), default=0))
        self._db[m_id] = {
            'message': entry.message,
            'name': entry.name
        }
        self._db.sync()

    def delete(self, entry):
        if entry.m_id:
            del self._db[str(entry.m_id)]
            self._db.sync()
            return True
        return False

    def get_filtered_by_name(self, name):
        return [e for e in self.get_all() if e.name == name]