from datetime import date
class User():
    def __init__(self, c, conn, uid, name):
        print("created uid of",uid)
        self.c = c
        self.conn = conn
        self.uid = uid
        self.name = name
        self.pid = 'test1'
        self.isQuestion = False

    def menu(self):
        print('''Menu--------
        1-Logout
        2-Exit Program
        3-Post a question
        4-Search for posts''')
        option = input("Option: ")
        if option=="1":
            #logout
            print("LOGOUT")
        elif option=="2":
            self.conn.close()
            quit()
        elif option=="3":
            self.post()
        elif option=="4":
            self.search()
        else:
            print("\nNot a Valid Option\n")
            return self.menu()
    
    def postActionMenu(self):
        if self.isQuestion:
            # post answer is only an option is selected post is a question
            print('''Post Action--------
            1-Main Menu
            2-Vote on post
            3-Post an answer''')
        else:
            print('''Post Action--------
            1-Main Menu
            2-Vote on post''')
        print('Selected Post ID: ',self.pid)
        option = input("Option: ")
        if option=="1":
            self.menu()
        elif option=="2":
            self.vote()
        elif option=="3":
            if self.isQuestion:
                self.answer()
            else:
                print("\nNot a Valid Option\n")
                return self.menu()
        else:
            print("\nNot a Valid Option\n")
            return self.menu()

    def post(self):
        print("post a question")

    def search(self):
        print("search for posts")
        # NEED TO UPDATE self.pid and self.isQuestion!!
        # open menu for action on post
        self.postActionMenu()

    def answer(self):
        print("answer question")

    '''
        Post action-Vote.The user should be able to vote on the post (if not voted already on the same post). 
        The vote should be recorded in the database with a vno assigned by your system, the vote date set to the 
        current date and the user id is set to the current user.
    '''
    def vote(self):
        # check that user has not already voted on the post
        self.c.execute('SELECT * FROM votes WHERE pid=:pid AND uid=:uid',{'pid':self.pid, 'uid':self.uid})
        if (self.c.fetchone() == None):
            # has not voted
            # generate a unique vno
            self.c.execute('SELECT COALESCE(MAX(vno),0) FROM votes;')
            vno = int(self.c.fetchone()[0])+1
 
            # insert vote into database
            self.c.execute('INSERT INTO votes(pid,vno,vdate,uid) VALUES(:pid,:vno,:vdate,:uid);',
                {'pid':self.pid, 'vno':vno ,'vdate':date.today(), 'uid':self.uid})
            self.conn.commit()
        else:
            print('\nAlready Voted on Post',self.pid,"\n")
            self.postActionMenu()
        

