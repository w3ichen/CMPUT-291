# privileged user inherits User class
from User import User
class Privileged(User):
    def __init__(self, uid, name):
        super().__init__(uid, name)
    
    def accept(self):
        print("accept post as answer")

    def badge(self):
        print("give a badge")
    
    def tag(self):
        print("give tag")
    
    def edit(self):
        print("edit")