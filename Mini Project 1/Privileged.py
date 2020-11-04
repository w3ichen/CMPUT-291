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
            3-Give a badge
            4-Add a tag
            5-Edit post
            6-Post an answer''')
        else:
            # is an answer
            print('''Post Action--------
            1-Main Menu
            2-Vote on post
            3-Give a badge
            4-Add a tag
            5-Edit post
            6-Mark as accepted''')
        print('Selected Post ID: ', self.pid)
        option = input("Option: ")
        if option == "1":
            return self.menu()
        elif option == "2":
            return self.vote()
        elif option == "3":
            return self.badge()
        elif option == "4":
            return self.tag()
        elif option == "5":
            return self.edit()
        elif option == "6":
            if self.isQuestion:
                return self.answer()
            else:
                return self.accept()
        else:
            print("\nNot a Valid Option\n")
            return self.menu()

    def accept(self):
        print("\n -----Accepted Answer-----")
        theaid = self.pid
        self.c.execute("SELECT qid FROM answers WHERE pid = " + str(theaid) + ";")
        qid = self.c.fetchone()[0]

        self.c.execute("SELECT theaid FROM questions WHERE pid=:qid", {"qid": qid})

        if self.c.fetchone() == None:

            user_ans = input("Would you like to accept this answer? [Y,N]: ")

            if user_ans.lower() == 'y':
                self.c.execute('UPDATE questions SET theaid=:theaid WHERE pid=:qid',
                               {'theaid': theaid, 'qid': qid})
                self.conn.commit()
                print('\nSuccessfully Accepted Answer', theaid, "\n")
            elif user_ans.lower() == 'n':
                print("\nAnswer will not become accepted answer\n")
                return self.menu()
            else:
                print("\n* Choose valid input *\n")
                return self.accept()

        else:
            print("An accepted answer already exists...\n")
            user_ans = input("Would you like to replace it with current answer? [Y,N]: ")
            if user_ans.lower() == 'y':
                self.c.execute('UPDATE questions SET theaid=:theaid WHERE pid=:qid',
                               {'theaid': theaid, 'qid': qid})
                self.conn.commit()
                print('\nSuccessfully Accepted Answer', theaid, "\n")
            elif user_ans.lower() == 'n':
                print("\nAccepted answer will not be changed\n")
                return self.menu()
            else:
                print("\n* Choose valid input *\n")
                return self.accept()

        return self.menu()

    def badge(self):
        print("give a badge")

    def tag(self):
        print("\n -----Add a Tag-----")
        pid = self.pid
        self.c.execute('SELECT tag FROM tags WHERE pid=:pid', {'pid': pid})
        curr_tag = self.c.fetchone()
        cont = True

        # tag_pid = self.c.fetchone()[0]
        if curr_tag is None:
            tag_in = input("What tag would you like to add? ")
            self.c.execute('''INSERT INTO tags(pid,tag) 
                    VALUES(:pid, :tag);''',
                           {'pid': pid, 'tag': tag_in})
            self.conn.commit()
            print('\nSuccessfully Added Tag:', tag_in, "\n")
        else:
            tag_in = input("What tag would you like to add? ")
            if tag_in.lower() in curr_tag:
                print("\nThis tag already exists! Please try again\n")
            else:
                self.c.execute('''INSERT INTO tags(pid,tag) 
                    VALUES(:pid, :tag);''',
                               {'pid': pid, 'tag': tag_in})
                self.conn.commit()
                print('\nSuccessfully Added Tag', tag_in, "\n")

        user_cont = input("\nWould you like to add another tag? [Y,N]: ")
        while cont:
            if user_cont.lower() == 'y':
                return self.tag()
            elif user_cont.lower() == 'n':
                cont = False
            else:
                print("\nInvalid Input!")
                break

        return self.menu()

    '''
        Post Action-Edit. The user should be able to edit the title and/or the body of the post. 
        Other fields are not updated when a post is edited.
    '''

    def edit(self):
        print("\nEdit Post", self.pid)
        self.c.execute('SELECT title,body FROM posts WHERE pid=:pid', {'pid': self.pid})
        old_post = self.c.fetchone()
        # change title and/or body, use or if user does not change field
        title = input("Update Title: ") or old_post[0]
        body = input("Update Body: ") or old_post[1]
        # update to database
        self.c.execute('UPDATE posts SET title=:title, body=:body WHERE pid=:pid',
                       {'title': title, 'body': body, 'pid': self.pid})
        self.conn.commit()
        print('\nSuccessfully Updated Post', self.pid, "\n")
        # go back to menu
        return self.postActionMenu()
