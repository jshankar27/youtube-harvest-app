from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os;

class MongoConnection:

    db_name = ""
    collection = ""

    def connect_mongo_database(self):
        MONGO_USERNAME = os.environ["MONGO_USERNAME"]
        MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
        if MONGO_USERNAME is None or MONGO_PASSWORD is None:
            return "Please set your MONGO_USERNAME as environment variable!" 
        uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@youtubecluster.ow4brp5.mongodb.net/?retryWrites=true&w=majority&appName=youtubecluster"
        client = MongoClient(uri, server_api=ServerApi('1'))
        self.db_name = client.Youtube_info
        self.collection = self.db_name.channel_data
  

    def upsert_into_mongodb(self, channel_data):
        upload_result = None
        if self.connect_mongo_database() is None:
            channel_id = channel_data['channel']['channel_id']
            upload_result = self.db_name.channel_data.replace_one({'_id':channel_id}, channel_data, upsert = True)      
            return upload_result 

    def list_channel_names(self):
        return self.db_name.channel_data.find({"isMigrated": False})
    
    def find_selected_channel(self,channel_name):
        return self.db_name.channel_data.find_one({"channel.channel_name":channel_name})