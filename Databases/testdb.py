import sqlite3

conn = sqlite3.connect("test.db")
c = conn.cursor()

# c.execute("create table user (id integer primary key autoincrement not null, username text not null, password not null, age integer, created_at real not_null, favourite_color text) ")
c.execute("""insert into user
    (username, password, created_at)
    values
    ("hammond","awesome",0)""")

conn.commit()
conn.close()  