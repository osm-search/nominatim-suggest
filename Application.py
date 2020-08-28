from psycopg2.extras import RealDictCursor, DictCursor, register_hstore
from DBConnection import DBConnection
from ESConnection import ESConnection
from tqdm import tqdm
import time
import logging
from Helper import form_doc
import json

if __name__ == "__main__":

    logging.basicConfig(filename='output.log',level=logging.INFO)
    languages = ['zh', 'sp', 'en', 'ar', 'fr', 'ru', 'pt', 'de', 'ja', 'ko']
    tags = ['name:'+i for i in languages]
    tags.append('name')

    db_connection = DBConnection()

    index_name = "nominatim_sugg"
    elasticsearch = ESConnection()
    elasticsearch.delete_index(index_name)
    with open('mapping.json') as f:
        mapping = json.load(f)
    elasticsearch.create_index(index_name, mapping)

    logging.debug("================================================================")
    logging.debug("================================================================")
    sql = "SELECT place_id, parent_place_id, name, address, country_code, importance, \
         housenumber, postcode, rank_search, rank_address from placex where name is not null \
and name ?| ARRAY[" + ','.join(["'" + tag + "'" for tag in tags]) + "] \
order by rank_search"
    logging.debug(sql + "\n")

    cursor = db_connection.connection.cursor(cursor_factory=RealDictCursor, name='mycursor')
    cursor.execute(sql)

    bucket = 10000
    t = bucket
    records = []
    docs = []
    body = ''
    start_time = time.time()
    bucket_start = time.time()
    j = 0
    for record in tqdm(cursor):
        if t == 0:
            t = bucket
            j = j + 1
            elasticsearch.bulk_index(index_name=index_name, body=body)
            bucket_start = time.time()
            records = []
            docs = []
            body = ''
        doc = form_doc(db_connection.connection, record, tags, index_name)

        docs.append(doc)
        header = { "index" : { "_index" : index_name } }
        body += str(json.dumps(header)) + "\n"
        body += str(json.dumps(doc)) + "\n"
        records.append(record)
        t -= 1
    if body:
        elasticsearch.bulk_index(index_name=index_name, body=body)    
    logging.debug('Total time = ' + str(time.time() - start_time))

