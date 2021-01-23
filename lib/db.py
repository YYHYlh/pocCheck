import sqlite3
import os
import sys
class db:
    def __init__(self) -> None:
        dbPath = sys.path[0]+"/data/poc.db"
        self.db=sqlite3.connect(dbPath)
        self.cursor=self.db.cursor()
        self.cursor.execute('''CREATE TABLE  IF NOT EXISTS poc (
            NAME TEXT PRIMARY KEY NOT NULL,
            SHA  TEXT NOT NULL,
            ADDRESS TEXT NOT NULL);
            ''')
        self.db.commit()
    def get(self,item):
        self.cursor.execute("SELECT NAME FROM poc WHERE NAME=? and SHA=?;",(item.get("name"),item.get("sha")))
        if len(self.cursor.fetchall()):
            print("in get")
            return True
        else:
            return False
    def insert(self,item):
        print("插入数据：{}".format(item))
        self.cursor.execute("INSERT INTO poc values (?,?,?)",(item.get("name"),item.get("sha"),item.get("html_url")))

    def commit(self):
        self.db.commit()
        self.db.close()