from os import name
import pymongo
from pymongo import MongoClient


client = MongoClient('mongodb://mongo')
db = client.todo
users = db.users
tokens = db.tokens 
messages = db.messages 
db.filepaths.drop({})
filepaths = db.filepaths 


#Entries in users follow the format:
#{'user':user, 'pass':pass, 'salt':salt}

#Entries in tokens follow the format:
#{'user':user, 'token':token}

#Entries in filepaths follow the format:
#filename user