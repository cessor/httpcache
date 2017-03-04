import sqlite3

HTML_CACHE = 'cache.sqlite'


class RecordExists(Exception):
    pass


class Store(object):
    def __init__(self, path=''):
        self._connection = sqlite3.connect(path or HTML_CACHE)
        self._initialize_database()

    def clear(self):
        sql = """delete from cache"""
        self._execute(sql, ())

    def close(self):
        self._connection.commit()
        self._connection.close()

    def _execute(self, sql, params):
        return self._connection.cursor().execute(sql, params)

    def _initialize_database(self):
        sql = """create table if not exists cache (
            id integer primary key not null,
            url text not null unique,
            status_code integer not null,
            content_type text,
            content text,
            retrieved_at datetime default current_timestamp
        )"""
        self._execute(sql, ())

        sql = """create index if not exists url_index on cache (url)"""
        self._execute(sql, ())
        self._connection.commit()

    def add(self, url, status_code, content_type, content):
        try:
            sql = """insert into cache (url, status_code, content_type, content)
                values (?, ?, ?, ?)"""
            self._execute(sql, (url, status_code, content_type, content))
            self._connection.commit()
        except sqlite3.IntegrityError:
            raise RecordExists

    def list(self):
        sql = """select url, status_code, content_type, retrieved_at
            from cache"""
        for record in self._execute(sql, ()):
            # CSV String
            print(', '.join(map(str, record)))

    def remove(self, url):
        sql = """delete from cache
            where url = ?"""
        self._execute(sql, (url,)).fetchone()
        self._connection.commit()

    def retrieve(self, url):
        sql = """select url, status_code, content_type, content, retrieved_at
            from cache
            where url = ?
            limit 1"""
        return self._execute(sql, (url,)).fetchone()
