# privileged user inherits User class
class Privileged(User):
    def __init__(self):
        super().__init__()
    
    def accept(self):
        print("accept post as answer")

    def badge(self):
        print("give a badge")
    
    def tag(self):
        print("give tag")
    
    def edit(self):
        print("edit")