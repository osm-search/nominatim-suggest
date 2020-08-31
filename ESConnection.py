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
        elasticsearch = Elasticsearch()
        logging.debug("Ping successful? " + str(elasticsearch.ping()))
        logging.debug("Info: " + str(elasticsearch.info()))

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
        logging.debug("Checking if the index exists")
        if self.elasticsearch.indices.exists(index_name):
            logging.debug("Index " + index_name + " exists")
        else:
            logging.debug("Index does not exist. Creating index " + index_name)
            self.elasticsearch.indices.create(index_name, mapping)

    def insert_doc(self, index_name, doc):
        '''
        Inserts a single doc into an index

            parameters:
                index_name : Name of the index
                doc : The doc to be inserted in the elasticsearch index 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to insert doc into " + index_name)
        self.elasticsearch.index(index_name, doc_type="_doc",
                            body=doc)
        logging.debug("Indexed " + str(doc) + " successfully")

    def bulk_index(self, index_name, body):
        '''
        Bulk index the documents

            parameters:
                index_name : Name of the index
                body : The docs to be inserted in the elasticsearch index 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to insert docs into " + index_name)
        self.elasticsearch.bulk(body=body, index=index_name)
        logging.debug("Indexed successfully")


    def search_results(self, index_name, q):
        '''
        Performs a simple search on an index

            parameters:
                index_name : Name of the index
                q : The elasticsearch query term 
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to search from " + index_name)

        logging.debug(self.elasticsearch.search(index_name, q))

    def search_with_place_id(self, index_name, place_id):
        '''
        Performs search based on place_id

            parameters:
                index_name : Name of the index
                place_id : The place_id to search on the elasticsearch index 
        '''
        logging.debug("=================================================================")
        res = self.elasticsearch.search("nominatim_test_", body={
            "query": {
                "match": {
                    "place_id": {
                        "query": place_id
                    }
                }
            }
        })['hits']['hits'][0]
        return res

    def delete_index(self, index_name):
        '''
        Deletes and index if it exists
            parameters:
                index_name : Name of the index to be deleted
        '''
        logging.debug("=================================================================")
        logging.debug("Trying to delete an index")
        logging.debug("Checking if the index exists")
        if self.elasticsearch.indices.exists(index_name):
            logging.debug("Index " + index_name + " exists")
            self.elasticsearch.indices.delete(index_name)
            logging.debug("Index successfully deleted")
        else:
            logging.debug("Index does not exist.")
