'''
Connection data to MongoDB using pymongo lib
'''
import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
CLIENT_ADDRESS = os.environ.get("CLIENT_ADDRESS")

def connect_mongo(data, collection, content):
    # Making Connection 
    myclient = MongoClient(CLIENT_ADDRESS)
    
    # database  
    db = myclient[data] 

    # Created or Switched to collection  
    Collection = db[collection] 
 
    # Inserting the loaded data in the Collection 
    # if JSON contains data more than one entry 
    # insert_many is used else inser_one is used 
    if isinstance(content, list): 
        Collection.insert_many(content)   
    else: 
        Collection.insert_one(content) 

    myclient.close()
    
if __name__ == "__main__":
    connect_mongo()
