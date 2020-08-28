from elasticsearch import Elasticsearch
from urllib.request import urlopen
import json
import time
import logging

class ESConnection:
    def __init__(self):
        self.elasticsearch = self.connect_to_elasticsearch()

    def connect_to_elasticsearch(self):
        '''
        Tests if the elasticsearch connection is possible by pinging the server
        '''
        logging.debug("=================================================================")
        logging.debug("Testing Elasticsearch connection")
        try:
            elasticsearch = Elasticsearch()
            logging.debug("Ping successful? " + elasticsearch.ping())
            logging.debug("Info: " + elasticsearch.info())
        except:
            logging.debug("Failed. Start the elasticsearch server and try again.")
            exit
        return elasticsearch

    def create_index(self, index_name, mapping):
        '''
        Creates a new elasticsearch index with the provided index_name

            parameters:
                index_name : Name of the index to be created
                mapping : The mapping to be used for elasticsearch index creation 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to create an index")
        try:
            logging.debug("Checking if the index exists")
            if self.elasticsearch.indices.exists(index_name):
                logging.debug("Index " + index_name + " exists")
            else:
                logging.debug("Index does not exist. Creating index " + index_name)
                self.elasticsearch.indices.create(index_name, mapping)
        except:
            logging.debug("Failed")

    def insert_doc(self, index_name, doc):
        '''
        Inserts a single doc into an index

            parameters:
                index_name : Name of the index
                doc : The doc to be inserted in the elasticsearch index 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to insert doc into " + index_name)
        try:
            self.elasticsearch.index(index_name, doc_type="_doc",
                                body=doc)
            logging.debug("Indexed " + str(doc) + " successfully")
        except:
            logging.debug("Failed")

    def bulk_index(self, index_name, body):
        '''
        Bulk index the documents

            parameters:
                index_name : Name of the index
                body : The docs to be inserted in the elasticsearch index 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to insert docs into " + index_name)
        try:
            self.elasticsearch.bulk(body=body, index=index_name)
            logging.debug("Indexed successfully")
        except:
            logging.debug("Failed")

    def search_results(self, index_name, q):
        '''
        Performs a simple search on an index

            parameters:
                index_name : Name of the index
                q : The elasticsearch query term 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to search from " + index_name)
        try:
            logging.debug(self.elasticsearch.search(index_name, q))
        except:
            logging.debug("Failed")

    def search_with_place_id(self, index_name, place_id):
        '''
        Performs search based on place_id

            parameters:
                index_name : Name of the index
                place_id : The place_id to search on the elasticsearch index 
        '''
        logging.debug("=================================================================")
        try:
            res = es.search("nominatim_test_", body={
                "query": {
                    "match": {
                        "place_id": {
                            "query": place_id
                        }
                    }
                }
            })['hits']['hits'][0]
            return res
        except:
            logging.debug("Failed")

    def delete_index(self, index_name):
        '''
        Deletes and index if it exists
            parameters:
                index_name : Name of the index to be deleted
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to delete an index")
        try:
            logging.debug("Checking if the index exists")
            if self.elasticsearch.indices.exists(index_name):
                logging.debug("Index " + index_name + " exists")
                self.elasticsearch.indices.delete(index_name)
                logging.debug("Index successfully deleted")
            else:
                logging.debug("Index does not exist.")
        except:
            logging.debug("Failed")

"""
if __name__ == "__main__":
    with open('mapping.json') as f:
        mapping = json.load(f)
    logging.debug(mapping)
    index_name = "nominatim_test"
    es_connection = ESConnection()
    es_connection.create_index(index_name, mapping)
    doc = {"age": 21, "first name": "Rahul", "last name": "Reddy"}
    es_connection.insert_doc(index_name, doc)
    logging.debug("Waiting for 3 seconds for changes to reflect")
    time.sleep(3)
    es_connection.search_results(index_name, 'asdf')
    es_connection.delete_index(index_name)
"""