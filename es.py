from elasticsearch import Elasticsearch
from urllib.request import urlopen
import json
import time



def test_es_connection():
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


def create_index(elasticsearch, index_name):
    print("=================================================================")
    print("Trying to create an index")
    try:
        print("Checking if the index exists")
        if elasticsearch.indices.exists(index_name):
            print("Index", index_name, "exists")
        else:
            print("Index does not exist. Creating index", index_name)
            elasticsearch.indices.create(index_name)
    except:
        print("Failed")


def insert_doc(elasticsearch, index_name, doc={"age": 21, "first name": "Rahul", "last name": "Reddy"}):
    print("=================================================================")
    print("Trying to insert doc into", index_name)
    try:
        elasticsearch.index(index_name, doc_type="_doc",
                            body=doc)
        print("Indexed " + str(doc) + " successfully")
    except:
        print("Failed")

def search_results(elasticsearch, index_name):
    print("=================================================================")
    print("Trying to search for `Rahul` from", index_name)
    try:
        print(elasticsearch.search(index_name, q="Rahul"))
    except:
        print("Failed")

def delete_index(elasticsearch, index_name):
    print("=================================================================")
    print("Trying to delete an index")
    try:
        print("Checking if the index exists")
        if elasticsearch.indices.exists(index_name):
            print("Index", index_name, "exists")
            elasticsearch.indices.delete(index_name)
            print("Index successfully deleted")
        else:
            print("Index does not exist.", index_name)
    except:
        print("Failed")


if __name__ == "__main__":
    index_name = "nominatim_test"
    elasticsearch = test_es_connection()
    create_index(elasticsearch, index_name)
    doc = {"age": 21, "first name": "Rahul", "last name": "Reddy"}
    insert_doc(elasticsearch, index_name, doc)
    print("Waiting for 3 seconds for changes to reflect")
    time.sleep(3)
    search_results(elasticsearch, index_name)
    delete_index(elasticsearch, index_name)
