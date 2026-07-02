import sqlite3

def init_db():
    con = sqlite3.connect("sql.db")
    cur = con.cursor()
    with open("schema.sql","r") as f:
        commands = f.read()
        cur.executescript(commands)
    con.commit()
    con.close()

if __name__ == "__main__":
    init_db()
