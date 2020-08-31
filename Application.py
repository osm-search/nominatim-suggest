from psycopg2.extras import RealDictCursor, DictCursor, register_hstore
from DBConnection import DBConnection
from ESConnection import ESConnection
from tqdm import tqdm
import time
import logging
from Helper import form_doc
import json

if __name__ == "__main__":
    # Setting the logging mode and output file
    logging.basicConfig(filename='output.log',level=logging.INFO)

    # The set of languages to be indexed. Modify this list to change language support
    languages = ['zh', 'sp', 'en', 'ar', 'fr', 'ru', 'pt', 'de', 'ja', 'ko']
    tags = ['name:'+i for i in languages]
    tags.append('name')
    # To add tags like house_name, use the format below
    # tags.append('house_name')

    # Provide a user name with read access to Nominatim DB and corresponding password
    db_connection = DBConnection(user="nominatim_reader", password="")

    # Name of the elasticsearch index. This should be the same in search.py
    index_name = "nominatim_sugg"
    elasticsearch = ESConnection()
    elasticsearch.delete_index(index_name)
    # mapping.json contains the mapping to be used
    with open('mapping.json') as f:
        mapping = json.load(f)
    elasticsearch.create_index(index_name, mapping)

    # This query fetches all required columns from placex
    # * where name is not null
    # * Atleast one of the required tags exist
    # and orders according to rank_search
    logging.debug("================================================================")
    logging.debug("================================================================")
    sql = "SELECT place_id, parent_place_id, name, address, country_code, importance, class, type, \
         housenumber, postcode, rank_search, rank_address from placex where name is not null \
and name ?| ARRAY[" + ','.join(["'" + tag + "'" for tag in tags]) + "] \
order by rank_search"
    logging.debug(sql + "\n")

    cursor = db_connection.connection.cursor(cursor_factory=RealDictCursor, name='mycursor')
    cursor.execute(sql)

    # bucket_size indicates the number of docs to bulk index
    bucket = 10000
    doc_count = bucket
    body = ''
    start_time = time.time()
    bucket_start = time.time()
    for record in tqdm(cursor):
        # we collected bucket_size number of docs. Now we bulk index them
        if doc_count == 0:
            doc_count = bucket
            elasticsearch.bulk_index(index_name=index_name, body=body)
            bucket_start = time.time()
            body = ''
        # Forms doc with all the necessary fields
        doc = form_doc(db_connection.connection, record, tags, index_name)
        
        # We form a string in required format for elasticsearch indexing
        header = { "index" : { "_index" : index_name } }
        body += str(json.dumps(header)) + "\n"
        body += str(json.dumps(doc)) + "\n"
        doc_count -= 1
    # For indexing the overflow docs
    if body:
        elasticsearch.bulk_index(index_name=index_name, body=body)
    logging.debug('Total time = ' + str(time.time() - start_time))

