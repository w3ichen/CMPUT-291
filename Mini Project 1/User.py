class User():
    def __init__(self, uid, name):
        print("created",uid,name)
        self.uid = uid
        self.name = name

    def post(self):
        print("post a question")

    def search(self):
        print("search for posts")

    def answer(self):
        print("answer question")

    def vote(self):
        print("vote")

