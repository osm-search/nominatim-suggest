from psycopg2.extras import RealDictCursor, DictCursor, register_hstore
from DBConnection import DBConnection
from ESConnection import ESConnection
from tqdm import tqdm
import time
import pprint
from Helper import form_doc
import json

if __name__ == "__main__":
    languages = ['zh', 'sp', 'en', 'ar', 'fr', 'ru', 'pt', 'de', 'ja', 'ko']
    tags = ['name:'+i for i in languages]
    tags.append['name']

    db_connection = DBConnection()

    index_name = "nominatim_test"
    elasticsearch = ESConnection()
    elasticsearch.delete_index(index_name)
    with open('mapping.json') as f:
        mapping = json.load(f)
    # print(mapping)
    elasticsearch.create_index(index_name, mapping)

    print("================================================================")
    print("================================================================")
    sql = "SELECT place_id, parent_place_id, name, address, country_code,\
         housenumber, postcode, rank_search, rank_address from placex where name is not null \
order by rank_address"
    print(sql, "\n")

    cursor = db_connection.connection.cursor(cursor_factory=RealDictCursor, name='mycursor')
    cursor.execute(sql)

    bucket = 10000
    t = bucket
    records = []
    docs = []
    a = ''
    start_time = time.time()
    bucket_start = time.time()
    j = 0
    for record in cursor:
        if t == 0:
            t = bucket
            j = j + 1
            elasticsearch.bulk_index(index_name=index_name, body=a)
            # print(bucket/(time.time() - bucket_start))
            bucket_start = time.time()
            records = []
            docs = []
            a = ''
        doc = form_doc(db_connection, record, tags)

        docs.append(doc)
        header = { "index" : { "_index" : index_name } }
        a += str(json.dumps(header)) + "\n"
        a += str(json.dumps(doc)) + "\n"
        records.append(record)
        t -= 1
    # print(bucket/(time.time() - bucket_start))
    print('Total time =', time.time() - start_time)

