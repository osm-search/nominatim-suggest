from elasticsearch import Elasticsearch
from urllib.request import urlopen
import json
import time


class ESConnection:
    def __init__(self):
        self.elasticsearch = self.connect_to_elasticsearch()

    # Tests if the elasticsearch connection is possible by pinging the server
    def connect_to_elasticsearch(self):
        print("=================================================================")
        print("Testing Elasticsearch connection")
        try:
            elasticsearch = Elasticsearch()
            print("Ping successful?", elasticsearch.ping())
            print("Info: ", elasticsearch.info())
        except:
            print("Failed. Start the elasticsearch server and try again.")
            exit
        return elasticsearch

    # Creates a new elasticsearch index with the provided index_name
    def create_index(self, index_name):
        print("=================================================================")
        print("Trying to create an index")
        try:
            print("Checking if the index exists")
            if self.elasticsearch.indices.exists(index_name):
                print("Index", index_name, "exists")
            else:
                print("Index does not exist. Creating index", index_name)
                self.elasticsearch.indices.create(index_name)
        except:
            print("Failed")

    # Inserts a single doc into an index
    def insert_doc(self, index_name, doc):
        print("=================================================================")
        print("Trying to insert doc into", index_name)
        try:
            self.elasticsearch.index(index_name, doc_type="_doc",
                                body=doc)
            print("Indexed " + str(doc) + " successfully")
        except:
            print("Failed")

    # Performs a simple search on an index
    def search_results(self, index_name, q):
        print("=================================================================")
        print("Trying to search for `Rahul` from", index_name)
        try:
            print(self.elasticsearch.search(index_name, q))
        except:
            print("Failed")

    # Deletes and index if it exists
    def delete_index(self, index_name):
        print("=================================================================")
        print("Trying to delete an index")
        try:
            print("Checking if the index exists")
            if self.elasticsearch.indices.exists(index_name):
                print("Index", index_name, "exists")
                self.elasticsearch.indices.delete(index_name)
                print("Index successfully deleted")
            else:
                print("Index does not exist.", index_name)
        except:
            print("Failed")


if __name__ == "__main__":
    index_name = "nominatim_test"
    es_connection = ESConnection()
    es_connection.create_index(index_name)
    doc = {"age": 21, "first name": "Rahul", "last name": "Reddy"}
    es_connection.insert_doc(index_name, doc)
    print("Waiting for 3 seconds for changes to reflect")
    time.sleep(3)
    es_connection.search_results(index_name, 'asdf')
    es_connection.delete_index(index_name)
