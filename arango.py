# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 21:44:07 2018

@author: Chris
"""

import pymongo

from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
print("connection established!")

db = client.test_database
print("..created database")

collection = db.test_collection
print("..created collection")

import datetime
post = {"author": "Mike",
         "text": "My first blog post!",
         "tags": ["mongodb", "python", "pymongo"],
         "date": datetime.datetime.utcnow()}


posts = db.posts
post_id = posts.insert_one(post).inserted_id
print("..added data")

post_id