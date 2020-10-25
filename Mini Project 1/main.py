import sqlite3
from datetime import date
import hashlib
from User import User
from Privileged import Privileged
from getpass import getpass

# cusor and connection global variables
c = None
conn = None

def hash_password(password):
    alg = hashlib.sha256()
    alg.update(password.encode('utf-8'))
    return alg.hexdigest()

def start():
    print("Welcome to Reddit\n----Menu----")
    print("   1-Registered User")
    print("   2-Unregistered User")
    option = input("Option: ")
    if option == "1":
        # registered user
        print("\n----Login----")
        uid = input("User ID: ")
        password = getpass()
        c.execute('SELECT * FROM users WHERE uid = :uid AND pwd = :pw;',
             { 'uid': uid, 'pw': hash_password(password) })
        user = c.fetchone()
        if (user == None):
            print("\nInvalid User ID or Password\n")
            return start()
        else:
            # check if user is privileged
            c.execute('SELECT * FROM privileged WHERE uid=:uid',{'uid':uid})
            if (c.fetchone() == None):
                # not a privileged user
                return User(uid, user[1])
            else:
                # is a privileged user
                print("Access: Privileged")
                return Privileged(uid, user[1])

    elif option == "2":
        # unregistered user
        print("\n----Register----")
        uid = input("Unique ID: ")
        name = input("Name: ")
        city = input("City: ")
        password = hash_password(getpass())
        # check that user does not exist
        c.execute('SELECT * FROM users WHERE uid=:uid;',{'uid':uid})
        if (c.fetchone() == None):
            c.execute('''INSERT INTO users(uid,name,city,pwd,crdate) 
                        VALUES(:uid, :name, :city, :pwd, :crdate);''',
                { 'uid':uid, 'name':name, 'city':city, 'pwd':password, 'crdate':date.today() })
            conn.commit()
            print("Successfully Created",name,"User")
        else:
            print("\nUser Already Exists\n")
            return start()
        # return user object
        return User(uid, name)
    else:
        print("\nInvalid Option - Enter 1 or 2\n")
        return start()


if __name__ == "__main__":
    # 1. Open database
    databse = input("Open database: ")
    conn = sqlite3.connect(databse)
    # 2. Create a cursor object
    c = conn.cursor()

    user = start()
    
    user.menu()

    # c.execute(''' ''')
    # c.execute("SELECT * FROM movie WHERE movie_number=:num and year=:year",
    # {"num":movie_number, "year": movie_year} )
    # conn.commit()
    # row = c.fetchone()
    # rows = c.fetchall()
    # print(rows)
    # for each in rows:
    #     print(each["title"])



    conn.close()