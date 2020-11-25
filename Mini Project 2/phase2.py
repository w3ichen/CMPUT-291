import pymongo
from pymongo import MongoClient
import sys
from datetime import datetime
import re
import json

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
    #creating a dictionary to store the post details
    post_dict = dict()

    #user inputs
    title = input("Please enter a title: ")
    body = input("Body: ") 
    tags = input("Please enter tags separated by a space.\nPress Enter if no tags applicable.\n")
    
    #storing tags in a set to avoid duplicates
    if tags == '':
        tags = None
    else:
        temp_tags = tags.split(" ")
        tag_list = []
        #creating tags in the required format to insert into the dictionart 
        for i in temp_tags:
            tag_list.append("<" + i + ">")
        tags = set(tag_list)
        tag_input = ''.join(tags)

    #finding the maximum ID to generate a new unique ID for the post
    maxi = db["Posts"].aggregate([{ "$group" : { "_id": "null", "max": { "$max" : {"$toInt": "$Id"} }}}])
    max_id = list(maxi)[0]["max"]
    new_id = str(max_id + 1)

    #inserting post details into the dictionary
    post_dict["Id"] = new_id
    post_dict["PostTypeId"] = "1" 
    post_dict["CreationDate"] = (str(datetime.now())[0:10] + 'T' + str(datetime.now())[11:23])
    post_dict["Score"] = 0
    post_dict["ViewCount"] = 0
    post_dict["Body"] = body
    #user ID will only be added if it is provided
    if user_id != None:
        post_dict["OwnerUserId"] = str(user_id)
    post_dict["Title"] = title
    #tags will only be added if it is provided
    if tags != None:
            post_dict["Tags"] = tag_input
    post_dict["AnswerCount"] = 0
    post_dict["CommentCount"] = 0
    post_dict["FavoriteCount"] = 0
    post_dict["ContentLicense"] = "CC BY-SA 2.5"

    #inserting the dictionary we just created into the database 
    db.Posts.insert_one(post_dict)
    
    
    tagz = None
    if tags != None:
        tagz = list(set(temp_tags))

    #Adding tags to Tags collection (if they don't exist) or updating the count (if they do exists)
    if tagz != None:
        for tag in tagz:
            tag_match = None
            # the query between the ^ and $ char is for finding exact matches
            tag_regex = re.compile('^' + re.escape(tag) + '$', re.IGNORECASE)
            tag_match = db.Tags.find_one({"TagName": tag_regex})
            #print(tag_match)
            if tag_match != None:
                db.Tags.update_one({"TagName": tag_regex}, {"$set" : {"Count": tag_match["Count"]+1}})
                #tag_match = db.Tags.find_one({"TagName": tag_regex})
                #print(tag_match)
            else:
                tag_dict = dict()
                
                max_t = db["Tags"].aggregate([{ "$group" : { "_id": "null", "max": { "$max" : {"$toInt": "$Id"} }}}])
                max_tag = list(max_t)[0]["max"]
                new_tag_id = str(max_tag + 1)    
                            
                tag_dict["Id"] = new_tag_id
                tag_dict["TagName"] = tag
                tag_dict["Count"] = 1
                db.Tags.insert_one(tag_dict)
                #tag_match = db.Tags.find_one({"TagName": tag_regex})
                #print(tag_match)
                
    print("\nYour question has been posted!") 
    
    return menu()

'''
    Search for questions. The user should be able to provide one or more keywords, and the system should retrieve all posts that 
    contain at least one keyword either in title, body, or tag fields (the match should be case-insensitive). 
    Questions have a post type id of 1 in Posts. For each matching question, display the title, the creation date, the score, 
    and the answer count. The user should be able to select a question to see all fields of the question from Posts. 
    After a question is selected, the view count of the question should increase by one (in Posts) and the user should be able to 
    perform a question action (as discussed next).
'''            
#Helper function to redundancy in the search function
def searchHelper(column,keyword_regex): 
    if column == "terms":
        results = db.Posts.find({ column: { "$in": keyword_regex },"PostTypeId":"1" }, ["_id"])
    else:
        results = db.Posts.find({"PostTypeId": "1", "$or": [ {"Title": keyword_regex}, {"Body":keyword_regex}, {"Tags":keyword_regex} ]}, ["_id"])
    return results
def search():
    global db, user_id, selected_post
    
    #set where all the IDs of the search results are stored
    search_ids = set()
    
    keywords = input("Please enter keywords to search separated by a space\n")
    keywords = keywords.split(" ")
    
    #arrays to store keywords
    greater_than_3 = []
    less_than_3 = []
    
    #sorting keywords in different arrays based on length
    for x in keywords:
        if len(x) >= 3:
            greater_than_3.append(x)
        if len(x) < 3:
            less_than_3.append(x)
    
    #local function to reduce complexity
    #adds the search result (post IDs) to the set
    def add_to_results(arr):
        for x in arr:
            search_ids.add(x["_id"])
    
    #searching keywords greater than 3 in terms array       
    keyword_regex = [word.lower() for word in greater_than_3]
    search_results = searchHelper("terms",keyword_regex)
    add_to_results(search_results)

    #searching keywords less than 3 in Title, Body, Tags collections
    for x in less_than_3:
        keyword_regex = re.compile('.*' + re.escape(x) + '.*', re.IGNORECASE)
        
        less_results = searchHelper("Title",keyword_regex)
        add_to_results(less_results)
 
          
    #printing the search results
    for n in search_ids:
        final_results = db.Posts.find({"_id": n}, ["Id","Title","CreationDate", "Score","AnswerCount"])
        for x in final_results:
            x.pop("_id")
            print("\n")
            print(json.dumps(x, indent=4))
    print("Number of search results: " + str(len(search_ids)))
    
    #selecting a post        
    if (len(search_ids) != 0):
        selected_post = input("\n\nPlease type in a post ID to select a post\n")
        if not selected_post.isdigit():
            print("Invalid Post ID\nAborting")
            return menu()
    
        #printing the full post
        full_post = db.Posts.find_one({"Id": selected_post},{"terms": False})
        try:
            full_post.pop("_id")
        except Exception:
            print("Invalid ID, Aborting")
            return menu()
        print("\n")
        print(json.dumps(full_post, indent=4,sort_keys=True))
        
        #updating the view count by adding one
        post_match = db.Posts.find_one({"Id": selected_post})
        db.Posts.update_one({"Id": selected_post}, {"$set" : {"ViewCount": post_match["ViewCount"]+1}})
        return action_menu()
    else:
        return menu()
    
   


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
    
    #store answer info into a dictionary
    ans_dict = dict()

    print("\nAnswer Selected Question\n")

    #get user input for answer body text
    answer = input("Please enter an answer to selected question: ")

    #find max ID then generate new unique ID for the answer
    init_max = db["Posts"].aggregate([{ "$group" : { "_id": "null", "max": { "$max" : {"$toInt": "$Id"} }}}])
    max_id = list(init_max)[0]["max"]
    new_id = str(max_id + 1)

    #store answer details into the dictionary
    ans_dict["Id"] = new_id
    ans_dict["PostTypeId"] = "2"
    ans_dict["ParentID"] = selected_post
    ans_dict["CreationDate"] = (str(datetime.now())[0:10] + 'T' + str(datetime.now())[11:23])
    ans_dict["Score"] = 0
    ans_dict["Body"] = answer  

    #store user id if given
    if user_id != None:
        ans_dict["OwnerUserId"] = str(user_id)
    
    ans_dict["CommentCount"] = 0
    ans_dict["ContentLicense"] = "CC BY-SA 2.5"

    #insert answer dictionary into database
    db.Posts.insert_one(ans_dict)

    print("\nYour answer has been posted!\n") 
    
    return menu()

'''
    Question action-List answers. The user should be able to see all answers of a selected question. If an answer is marked as the 
    accepted answer, it must be shown as the first answer and should be marked with a star. Answers have a post type id of 2 in Posts. 
    For each answer, display the first 80 characters of the body text (or the full text if it is of length 80 or less characters), 
    the creation date, and the score. The user should be able to select an answer to see all fields of the answer from Posts. 
    After an answer is selected, the user may perform an answer action (as discussed next).
'''
def list_answers():
    global db, user_id, selected_post

    print("\nAll answers for post id", selected_post, "\n")

    #get results_answer where selected_post id is the same as ParentId
    result_answer = db.Posts.find({"ParentId": selected_post}, ["Id","Body","CreationDate","Score"])

    #check if there are answers to a post
    if result_answer.count() == 0:
        print("No answers found for post")
        return action_menu()

    # see if selected_post has an accepted answer
    accepted_answer_id = None
    the_post = db.Posts.find_one({"Id":selected_post})
    if "AcceptedAnswerId" in the_post.keys():
        # post has an accepted answer
        accepted_answer_id = the_post["AcceptedAnswerId"]
        the_answer = db.Posts.find_one({"Id":accepted_answer_id}, ["Id","Body","CreationDate","Score"])
        body_desc = the_answer.pop("Body")
        body_desc = body_desc[:80]
        the_answer["Body"] = body_desc
        the_answer.pop("_id")
        print("\n* Accepted Answer *\n")
        print(json.dumps(the_answer, indent=4))


    #displaying info with body limited to 80 chars
    for result in result_answer:
        if result["Id"] != accepted_answer_id:
            body_desc = result.pop("Body")
            body_desc = body_desc[:80]
            result["Body"] = body_desc
            result.pop("_id")
            print("\n")
            print(json.dumps(result, indent=4))

    #user selects answer
    user_input = input("\nWhich answer would you like to select? ")
    if not user_input.isdigit():
        print("Invalid Post ID\n")
        return menu()
    
    #print out full info of selected_post
    full_post = db.Posts.find_one({"Id": user_input},{"terms": False})
    try:
        full_post.pop("_id")
    except Exception:
        print("Invalid ID, Aborting")
    print("\n")
    print(json.dumps(full_post, indent=4, sort_keys=True))
    selected_post = user_input
    return action_menu()

'''
    Question/Answer action-Vote. The user should be able to vote on the selected question or answer if not voted already on the same post 
    (this constraint is only applicable to users with a user id; anonymous users can vote with no constraint). The vote should be recorded 
    in Votes with a unique vote id assigned by your system, the post id set to the question/answer id, vote type id set to 2, 
    and the creation date set to the current date. If the current user is not anonymous, the user id is set to the current user.
    With each vote, the score field in Posts will also increase by one.
'''
def vote():
    global db, user_id, selected_post
    
    #store vote info into a dictionary
    vote_dict = dict()

    #get user input to vote
    user_input = input("\nWould you like to vote on this post [Y,N]? ")

    #if user inputs 'y', continue
    if user_input.lower() == 'y':
        #check if user_id exists
        if user_id != None:
            votes = db.Votes.find({"UserId": user_id, "PostId":selected_post})

            #check if user already voted on post
            if votes.count()>0:
                print("\nCannot vote on this post anymore...\n")
            else:
                init_max = db["Votes"].aggregate([{ "$group" : { "_id": "null", "max": { "$max" : {"$toInt": "$Id"} }}}])
                max_id = list(init_max)[0]["max"]
                new_id = str(max_id + 1)

                vote_dict["Id"] = new_id
                vote_dict["PostId"] = selected_post
                vote_dict["VoteTypeId"] = '2'
                vote_dict["UserId"] = user_id
                vote_dict["CreationDate"] = (str(datetime.now())[0:10] + 'T' + str(datetime.now())[11:23])

                #insert voter dictionary into database
                db.Votes.insert_one(vote_dict)
                #updating the score count by adding one
                post_match = db.Posts.find_one({"Id": selected_post})
                db.Posts.update_one({"Id": selected_post}, {"$set" : {"Score": post_match["Score"]+1}})

                print("\nVoted on ",selected_post,"\n")

        else:
            init_max = db["Votes"].aggregate([{ "$group" : { "_id": "null", "max": { "$max" : {"$toInt": "$Id"} }}}])
            max_id = list(init_max)[0]["max"]
            new_id = str(max_id + 1)

            vote_dict["Id"] = new_id
            vote_dict["PostId"] = selected_post
            vote_dict["VoteTypeId"] = '2'
            vote_dict["UserId"] = user_id
            vote_dict["CreationDate"] = (str(datetime.now())[0:10] + 'T' + str(datetime.now())[11:23])
            #insert voter dictionary into database
            db.Votes.insert_one(vote_dict)
            #updating the score count by adding one
            post_match = db.Posts.find_one({"Id": selected_post})
            db.Posts.update_one({"Id": selected_post}, {"$set" : {"Score": post_match["Score"]+1}})

            print("\nVoted on ",selected_post,"\n")
    
    #if user inputs 'n'
    elif user_input.lower() == 'n':
        print("\nVoting was cancelled...\n")
        return menu()

    else:
        print("\nInvalid Input!\n")
    
    return action_menu()

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
        results = Posts.find({"OwnerUserId":user_id, "PostTypeId":"1"},["Score"])
        questions_count = results.count()
        questions_score = 0
        for result in results:
            questions_score += result["Score"]
        if questions_count != 0:
            questions_score /= questions_count
        else:
            questions_score = 0.0

        # (2) the number of answers owned and the average score for those answers
        results = Posts.find({"OwnerUserId":user_id, "PostTypeId":"2"},["Score"])
        answers_count = results.count()
        answers_score = 0
        for result in results:
            answers_score += result["Score"]
        if questions_count != 0:
            answers_score /= answers_count
        else:
            answers_score = 0.0

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

    # ask for user_id
    print("Enter User ID (press Enter to skip):")
    new_id = input("User ID: ")
    if new_id == "":
        menu()
    try:
        int(new_id) # check that it's an integer
        user_id = new_id
        report()
    except Exception:
        print("\nInvalid User ID\n")
        menu()
    

    menu()
