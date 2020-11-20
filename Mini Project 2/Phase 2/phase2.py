import pymongo
from pymongo import MongoClient
import sys

# global variables
db = None
user_id = None
selected_post = None

'''
    Post a question. The user should be able to post a question by providing a title text, a body text, and zero or more tags. 
    The post should be properly recorded in the database. A unique id should be assigned to the post by your system, 
    the post type id should be set to 1 (to indicate that the post is a question), the post creation date should be set to 
    the current date and the owner user id should be set to the user posting it (if a user id is provided). 
    The quantities Score, ViewCount, AnswerCount, CommentCount, and FavoriteCount are all set to zero and the content 
    license is set to "CC BY-SA 2.5".
'''
def post():
    global db, user_id, selected_post
    

'''
    Search for questions. The user should be able to provide one or more keywords, and the system should retrieve all posts that 
    contain at least one keyword either in title, body, or tag fields (the match should be case-insensitive). 
    Questions have a post type id of 1 in Posts. For each matching question, display the title, the creation date, the score, 
    and the answer count. The user should be able to select a question to see all fields of the question from Posts. 
    After a question is selected, the view count of the question should increase by one (in Posts) and the user should be able to 
    perform a question action (as discussed next).
'''
def search():
    global db, user_id, selected_post
    

'''
    Question action-Answer. The user should be able to answer the question by providing a text. An answer record should be 
    inserted into the database, with body field set to the provided text. A unique id should be assigned to the post by your system, 
    the post type id should be set to 2 (to indicate that the post is an answer), the post creation date should be set to the current 
    date and the owner user id should be set to the user posting it (if a user id is provided). 
    The parent id should be set to the id of the question. The quantities Score and CommentCount are all set to zero and the content 
    license is set to "CC BY-SA 2.5".
'''
def answer():
    global db, user_id, selected_post
    

'''
    Question action-List answers. The user should be able to see all answers of a selected question. If an answer is marked as the 
    accepted answer, it must be shown as the first answer and should be marked with a star. Answers have a post type id of 2 in Posts. 
    For each answer, display the first 80 characters of the body text (or the full text if it is of length 80 or less characters), 
    the creation date, and the score. The user should be able to select an answer to see all fields of the answer from Posts. 
    After an answer is selected, the user may perform an answer action (as discussed next).
'''
def list_answers():
    global db, user_id, selected_post
    

'''
    Question/Answer action-Vote. The user should be able to vote on the selected question or answer if not voted already on the same post 
    (this constraint is only applicable to users with a user id; anonymous users can vote with no constraint). The vote should be recorded 
    in Votes with a unique vote id assigned by your system, the post id set to the question/answer id, vote type id set to 2, 
    and the creation date set to the current date. If the current user is not anonymous, the user id is set to the current user.
    With each vote, the score field in Posts will also increase by one.
'''
def vote():
    global db, user_id, selected_post
    

'''
    Your program should allow the users of the system to provide a user id (if they wish), which is a numeric field, formatted as 
    shown in the sample json files. If a user id is provided, the user will be shown a report that includes 
        (1) the number of questions owned and the average score for those questions, 
        (2) the number of answers owned and the average score for those answers, 
        (3) the number of votes registered for the user. 
    Users may also use the system without providing a user id, in which case no report is displayed.
'''
def report():
    global db, user_id, selected_post
    print("\nUser Report")
    if user_id is None:
        print("Enter User ID to Generate Report  (Press Enter to Return to Main Menu)")
        new_id = input("User ID: ")
        if new_id == "":
            return menu()
        try:
            int(new_id) # check that it's an integer
            user_id = new_id
        except Exception:
            print("\nInvalid User ID\n")
            return menu()
        # rerun report() with updated user_id
        return report()
    else:
        # Generate report
        Posts = db["Posts"]
        # (1) the number of questions owned and the average score for those questions
        results = Posts.find({"OwnerUserId":user_id, "PostTypeId":"1"})
        questions_count = results.count()
        questions_score = 0
        for result in results:
            questions_score += result["Score"]
        questions_score /= questions_count

        # (2) the number of answers owned and the average score for those answers
        results = Posts.find({"OwnerUserId":user_id, "PostTypeId":"2"})
        answers_count = results.count()
        answers_score = 0
        for result in results:
            answers_score += result["Score"]
        answers_score /= answers_count

        # (3) the number of votes registered for the user
        Votes = db["Votes"]
        results = Votes.find({"UserId":user_id})
        votes_count = results.count()
        
        # Print Report

        print("""\nReport for {0}:\n{1:25}{2:<10}\n{3:25}{4:<10.6}\n{5:25}{6:<10}\n{7:25}{8:<10.6}\n{9:25}{10:<10}\n
                """.format(user_id, "Number of Questions: ", questions_count, "Questions Score Average: ", questions_score,
                "Number of Answers: ",answers_count, "Answers Score Average: ",answers_score, "Number of Votes: ", votes_count))

    return menu()

def menu():
    print("""
        \nMain Menu
            1 - View User Report
            2 - Post a Question
            3 - Search for Questions
            4 - Exit Program
        """)
    option = input("Option: ")
    if option == "1":
        return report()
    elif option == "2":
        return post()
    elif option == "3":
        return search()
    elif option == "4":
        quit()
    else:
        print("\nInvalid Option\nTry Again\n")
        return menu()


def action_menu():
    print("\nSelected Post:", selected_post)
    print("""
        \nPost Action Menu
            1 - Back to Main Menu
            2 - Answer Question
            3 - List Answers
            4 - Vote
        """)
    option = input("Option: ")
    if option == "1":
        return menu()
    elif option == "2":
        return answer()
    elif option == "3":
        return list_answers()
    elif option == "4":
        return vote()
    else:
        print("\nInvalid Option\nTry Again\n")
        return action_menu()


if __name__ == "__main__":

    # python3 phase2.py <port>

    # connect to port
    try:
        port = sys.argv[1]
        client = MongoClient('mongodb://localhost:'+port)
    except Exception:
        print("Unable to connect to MongoDB")
        print("Try: python3 phase2.py <port number>")
        quit()
    print("Connected to MongoDB Port ",port)
    print("Welcome to MongoDB Search Engine\n")

    db = client["291db"]  

    menu()
