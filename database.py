import sqlite3

def create_database(name):
    """Creates a database of name"""
    conn = sqlite3.connect(name+".db")
    c = conn.cursor()
    c.execute(""" CREATE TABLE users (id INTEGER UNIQUE PRIMARY KEY NOT NULL, username TEXT UNIQUE, password TEXT, age INTERGER)""")
    conn.commit()
    conn.close()

create_database("test")