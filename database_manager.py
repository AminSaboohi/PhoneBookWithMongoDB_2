from pymongo import MongoClient


class DatabaseManager:
    def __init__(self, database_name, host, port):
        self.database_name = database_name
        self.host = host
        self.port = port
        self.models = dict()

        client = MongoClient(host=self.host,
                             port=self.port)

        self.mongodb_database = client[self.database_name]

    def create_collections(self, models):
        collections = self.mongodb_database.list_collection_names()
        for model in models:
            if model in collections:
                self.models[model] = self.mongodb_database.get_collection(
                    model)
            else:
                self.models[model] = self.mongodb_database[model]
