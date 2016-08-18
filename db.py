import os
import sqlite3


class Database(object):

    DB_SCHEMA_FILE = 'sql/schema.sql'

    def __init__(self, path, overwrite=False):

        self.path = path
        if os.path.exists(path):
            if overwrite:
                os.unlink(path)
                self._create_db(path)
            else:
                self.conn = sqlite3.connect(path)
        else:
            self._create_db(path)

    def _create_db(path):
        with open(self.DB_SCHEMA_FILE, 'r') as f:
            self.conn = sqlite3.connect(path)
            self.conn.executescript(f.read())
            self.conn.commit()