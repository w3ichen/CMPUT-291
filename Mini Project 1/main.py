import sqlite3

if __name__ == "__main__":
    # 1. Open database
    databse = input("Open database: ")
    conn = sqlite3.connect(databse)
    # 2. Create a cursor object
    c = conn.cursor()

    c.execute(''' ''')