import pymongo
from pymongo import MongoClient
import sys
import json
import re

db = None

def insertCollection(name):
    name = name.capitalize()
    with open(name+".json") as file:
        data = json.load(file)
    # create or open collection
    collection = db[name]
    # drop collection if exists
    collection.drop()
    # insert all into database
    collection.insert_many(data[name.lower()]["row"])

def extractTerms():
    # extract all terms of length 3 characters or more in title and body fields of Posts, 
    # add those terms as an array named terms to Posts collection, and build an index on those terms. 
    # Assume a term is an alphanumeric character string, and that terms are separated by white spaces and/or punctuations
    posts = db["Posts"]
    terms = set() # empty set
    
    separators = '[,.?\/~`!@#$%^&*()_+\-={}\[\]\\\|:;\'\"\n<> ]'
    # 
    # iterate through every post
    for post in posts.find():
        # split string into words separated by white space and/or punctuation
        if "Title" in post.keys():
            title_words = re.compile(separators).split(post["Title"])
            for word in title_words:
                if len(word) >= 3:
                    # if word is greater or equal to 3 characters in length, then add to set
                    terms.add(word.lower())
        if "Body" in post.keys():
            body_words = re.compile(separators).split(post["Body"])
            for word in body_words:
                if len(word) >= 3:
                    # if word is greater or equal to 3 characters in length, then add to set
                    terms.add(word.lower())
    return list(terms)

if __name__ == "__main__":

    # python3 phase1.py <port>

    # connect to port
    try:
        port = sys.argv[1]
        client = MongoClient('mongodb://localhost:'+port)
    except Exception:
        print("Unable to connect to MongoDB")
        print("Try: python3 phase1.py <port number>")
        quit()
    print("Connected to MongoDB Port",port)
    db = client["291db"]  

    # insert .json into mongodb
    # Tags.json
    print("Reading and Inserting Tags.json")
    insertCollection("Tags")
    # Posts.json
    print("Reading and Inserting Posts.json")
    insertCollection("Posts")
    # Votes.json
    print("Reading and Inserting Votes.json")
    insertCollection("Votes")

    print("Extracting Terms")
    # Extract terms and store into Posts
    db["Posts"].insert_one({"Id":"terms","_id":"terms","terms":extractTerms()})

    
    
    # print(db["Posts"].find_one({"Id":"terms"})["terms"])
    