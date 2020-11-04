# privileged user inherits User class
from User import User
class Privileged(User):
    def __init__(self, c, conn, uid, name):
        super().__init__(c, conn, uid, name)
    
    def postActionMenu(self):
        if self.isQuestion:
            # post answer is only an option is selected post is a question
            print('''Post Action--------
            1-Main Menu
            2-Vote on post
            3-Mark as accepted
            4-Give a badge
            5-Add a tag
            6-Edit post
            7-Post an answer''')
        else:
            print('''Post Action--------
            1-Main Menu
            2-Vote on post
            3-Mark as accepted
            4-Give a badge
            5-Add a tag
            6-Edit post''')
        print('Selected Post ID: ',self.pid)
        option = input("Option: ")
        if option=="1":
            return self.menu()
        elif option=="2":
            return self.vote()
        elif option=="3":
            return self.accept()
        elif option=="4":
            return self.badge()
        elif option=="5":
            return self.tag()
        elif option=="6":
            return self.edit()
        elif option=="7":
            if self.isQuestion:
                return self.answer()
            else:
                print("\nNot a Valid Option\n")
                return self.menu()
        else:
            print("\nNot a Valid Option\n")
            return self.menu()

    def accept(self):
        print("accept post as answer")

    def badge(self):
        print("give a badge")
    
    def tag(self):
        print("give tag")
    
    '''
        Post Action-Edit. The user should be able to edit the title and/or the body of the post. 
        Other fields are not updated when a post is edited.
    '''
    def edit(self):
        print("\nEdit Post",self.pid)
        self.c.execute('SELECT title,body FROM posts WHERE pid=:pid',{'pid':self.pid})
        old_post = self.c.fetchone()
        # change title and/or body, use or if user does not change field
        title = input("Update Title: ") or old_post[0]
        body = input("Update Body: ") or old_post[1]
        # update to database
        self.c.execute('UPDATE posts SET title=:title, body=:body WHERE pid=:pid',
                {'title':title, 'body':body, 'pid':self.pid})
        self.conn.commit()
        print('\nSuccessfully Updated Post',self.pid+"\n")
        # go back to menu
        return self.postActionMenu()
        