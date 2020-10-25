class User():
    def __init__(self, uid, name):
        print("created uid of",uid)
        self.uid = uid
        self.name = name

    def menu(self):
        print('''Menu--------
        1-Logout
        2-Exit Program
        3-Post a question
        4-Search for posts
        5-Post an answer
        6-Vote on post''')
        option = input("Option: ")
        if option=="1":
            #logout
            print("LOGOUT")
        elif option=="2":
            quit()
        elif option=="3":
            self.post()
        elif option=="4":
            self.search()
        elif option=="5":
            self.answer()
        elif option=="6":
            self.vote()

    def post(self):
        print("post a question")

    def search(self):
        print("search for posts")

    def answer(self):
        print("answer question")

    def vote(self):
        print("vote")

