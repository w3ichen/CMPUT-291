"""This is an example python script to work with the mongodb database using the
pymongo library.

We are going to model the ER diagram we had for the video-store
application as part of mongo db.
"""

from pymongo import MongoClient

# Use client = MongoClient('mongodb://localhost:27017') for specific ports!
# Connect to the default port on localhost for the mongodb server.
client = MongoClient()


# Create or open the video_store database on server.
db = client["video_store"]


# List collection names.
collist = db.list_collection_names()
if "movies_collection" in collist:
    print("The collection exists.")

# Create or open the collection in the db
movies_collection = db["movies_collection"]

# delete all previous entries in the movies_collection
# specify no condition.
movies_collection.delete_many({})

# Insert movies into the collection. Remember that each inserted document should be key-value pairs.
# movie num will be the provided _id when inserting into the collection.
movies = [
    {"title": "The matrix 4", "category_name": "action", "formats": ["VCD", "CD"]},
    {"title": "Spiderman 6", "category_name": "sci-fi", "formats": ["CD", "Blueray"]},
    {"title": "Spiderman 1", "category_name": "sci-fi", "formats": ["CD"]},
    {"title": "La la Land", "category_name": None, "formats": ["DVD"]},
]

# insert movies into the movies_collection.
# use insert_one() to insert a single document.
ret = movies_collection.insert_many(movies)

# Print list of the _id values of the inserted documents
movie_ids = ret.inserted_ids
print(movie_ids)


members = [
    {
        "_id": "7806808181",
        "name": "Saeed",
        "like": "action",
        "dependents": ["Saeed Junior", "Saeed J Junior"],
        "member_type": "Gold",
        "credit number": "450 80 81",
    },
    {
        "_id": "6806808282",
        "name": "Mike",
        "like": "drama",
        "dependents": None,
        "member_type": "Bronze",
        "credit number": None,
    },
]

# Insert members into a new collection.
members_collection = db["members_collection"]

# delete previous docs in the members collection.
members_collection.delete_many({})

ret = members_collection.insert_many(members)
member_ids = [mem["_id"] for mem in members]


rental_collection = db["rentals_collection"]

""" Rules:
You cannot rent a movie if it has already rented out.
Gold members are free to rent any number of movies they want.
Bronze and dependents can only rent one movie.
"""

rental = {"member_renting": ("Saeed", "7806808181"), "movie_rented": movie_ids[1]}
# delete previous docs in the rental_collection
rental_collection.delete_many({})
rental_collection.insert_one(rental)


def get_the_member(db, member_name, member_phone_number):
    """Check the documents in the members collection to specify the type of the
    member."""
    mem_coll = db["members_collection"]
    results = mem_coll.find({"_id": member_phone_number})
    for mem in results:
        if mem["name"] == member_name:
            return mem["member_type"]
        if mem["dependents"] is not None and member_name in mem["dependents"]:
            return "Dependent"


def check_movie_for_member(db, member_name, member_phone_number, movie_id):
    """Function to query the database for some of the checks."""

    # check if movie_id has been rented out or not.
    rent_coll = db["rentals_collection"]
    results = rent_coll.find({"movie_rented": movie_id})
    if results.count(True) > 0:
        print("This movie {0} has been rented out".format(movie_id))
        return False

    # count the number of movies this person is watching currently.
    results = rent_coll.find({"member_renting": (member_name, member_phone_number)})
    num_movies = results.count(True)
    member_type = get_the_member(db, member_name, member_phone_number)
    if member_type == "Dependent" and num_movies > 0:
        print("Dependent can only rent one movie")
        return False
    if member_type == "Bronze" and num_movies > 0:
        print("Bronze member can only rent one movie")
        return False

    return True


# This won't work since the movie is rented out.
if check_movie_for_member(db, "Saeed Junior", "7806808181", movie_ids[0]):
    rental_collection.insert(
        {"member_renting": ("Saeed Junior", "7806808181"), "movie_rented": movie_ids[0]}
    )

if check_movie_for_member(db, "Saeed Junior", "7806808181", movie_ids[1]):
    rental_collection.insert(
        {"member_renting": ("Saeed Junior", "7806808181"), "movie_rented": movie_ids[1]}
    )

if check_movie_for_member(db, "Mike", "6806808282", movie_ids[2]):
    rental_collection.insert(
        {"member_renting": ("Mike", "6806808282"), "movie_rented": movie_ids[2]}
    )

# This won't work since the Mike is a bronze member.
if check_movie_for_member(db, "Mike", "6806808282", movie_ids[3]):
    rental_collection.insert(
        {"member_renting": ("Mike", "6806808282"), "movie_rented": movie_ids[3]}
    )


# print all rentals
results = rental_collection.find({}).sort("movie_rented")
for rental in results:
    print(rental)

""" Expect to see these in the output:
This movie 5f87720ba450f7bc9a730b03 has been rented out
Bronze member can only rent one movie
{'movie_rented': ObjectId('5f87720ba450f7bc9a730b02'), '_id': ObjectId('5f87720ba450f7bc9a730b07'), 'member_renting': ['Saeed Junior', '7806808181']}
{'movie_rented': ObjectId('5f87720ba450f7bc9a730b03'), '_id': ObjectId('5f87720ba450f7bc9a730b06'), 'member_renting': ['Saeed', '7806808181']}
{'movie_rented': ObjectId('5f87720ba450f7bc9a730b04'), '_id': ObjectId('5f87720ba450f7bc9a730b08'), 'member_renting': ['Mike', '6806808282']}
"""
