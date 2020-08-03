from Input import *
from es import *
from tqdm import tqdm
import time
import pprint


tags = ['name', 'name:en', 'name:it', 'name:fr', 'name:de']
def get_add(count, bucket):
    db_connection = DBConnection
    connection = connect_to_db()

    index_name = "nominatim_final"
    elasticsearch = test_es_connection()
    delete_index(elasticsearch, index_name)
    create_index(elasticsearch, index_name)

    doc_count = count
    print("================================================================")
    print("================================================================")
    sql = "SELECT place_id, parent_place_id, name, address, country_code,\
         housenumber, postcode, rank_search, rank_address from placex where name is not null \
order by rank_address" # limit " + str(doc_count)
    print(sql, "\n")

    cursor = connection.cursor(cursor_factory=RealDictCursor, name='mycursor')
    cursor.execute(sql)

#    record = cursor.fetchone()
    t = bucket
    records = []
    docs = []
    a = ''
    bucket_start = time.time()
    j = 0
    for record in cursor:
        if t == 0:
            t = bucket
            # push docs to es
            print("================================================================")
            print(bucket * j)
            j = j + 1
            print("================================================================")
            print(docs[0])
            try:
                elasticsearch.bulk(index=index_name, body=a)
            except:
                print("Bulk indexing failed!! Trying agin in few seconds")
                time.sleep(5)
                elasticsearch.bulk(index=index_name, body=a)

            print(bucket/(time.time() - bucket_start))
            bucket_start = time.time()
#            print(docs)
            print("================================================================")
            print("================================================================")

            records = []
            docs = []
            a = ''
#        print("Rank:", record['rank_search'])
        # print(record['name'])
        # Formed address: {'formed_address': {'addr': 'Juberri, Sant Julià de Lòria, Sant Julià de Lòria', 'addr:ca': 'Juberri, Sant Julià de Lòria', 'addr:ru': 'Джубери, Сант-Жулия-де-Лория'}, 'postcode': 'AD600', 'country_code': 'ad'}
        formed_address = form_address(connection, record)
        doc = formed_address
        doc.update({'place_id': record['place_id']})
        if 'osm_id' in record:
            #  and record['osm_type']:
            doc.update({'osm_id': record['osm_id'], 'osm_type': record['osm_type']})
        if record['postcode']:
            doc.update({'postcode': record['postcode']})
        if record['address']:
            doc.update({'nominatim_address': record['address']})
        if record['country_code']:
            doc.update({'country_code': record['country_code']})
        docs.append(doc)
        header = { "index" : { "_index" : index_name } }
        a += str(json.dumps(header)) + "\n"
        a += str(json.dumps(doc)) + "\n"
#        print("Formed address:", doc)
        records.append(record)

#        record = cursor.fetchone()
        t -= 1
    print(bucket/(time.time() - bucket_start))

def form_parent_address(connection, record, tag):
    if record["rank_search"] < 5:
        # print("<5. Handle this")
#        print("<5")
        if record['name'] and record['name']['name']:
            
            return record['name']['name']
        return record['name']
#    if record["rank_search"] > 27:
#        print(">27. Handle this")
#        print(record)

    # if record['address']:
    #     print("Address exists in record")
    #     return record['address']

    
    sql = "SELECT * from place_addressline where isaddress=true and place_id = " + str(record['place_id'])

    # print(sql, "\n")

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)

    a_record = cursor.fetchone()
    
    if a_record:
        if tag in record['name']:
            return record['name'][tag] + ", " + form_parent_address(connection, fetch_record(connection, a_record['address_place_id']), tag)
        else:
            if 'name' in record['name']:
                return record['name']['name'] + ", " + form_parent_address(connection, fetch_record(connection, a_record['address_place_id']), tag)
            else:
                return form_parent_address(connection, fetch_record(connection, a_record['address_place_id']), tag)
    if tag in record['name'] and record['name'][tag]:
        return record['name'][tag]
    return ""

def form_address(connection, record):
    if not record['name']:
        return {"addr": ""}
    # print(record)
    if record["rank_search"] < 5:
        # print("<5. Handle this")
#        print("<5")
        if record['name'] and "name" in record['name']:
            
            return {"addr": record['name']['name']}
        return {"addr": record['name']}
    if record["rank_search"] > 29:
        add = {}
        parent_record = fetch_record(connection, record['parent_place_id'])
        for tag in record['name'].keys():
            if "name" not in tag or tag not in tags:
                continue
            parent = ""
            if parent_record and 'name' in parent_record and parent_record['name']:
                if tag in parent_record['name']:
                    parent = ", " + parent_record['name'][tag]
            #parent = ''
                add[tag.replace("name", "addr")] = record['name'][tag] + parent
       # print(add)
        return add

#        print(">27. Handle this")
        # print(record)

    # if record['address']:
    #     print("Address exists in record")
    #     return record['address']

    
    sql = "SELECT * from place_addressline where isaddress=true and place_id = " + str(record['place_id'])

    # print(sql, "\n")

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)

    a_record = cursor.fetchone()
    add = {}
    parent_record = fetch_record(connection, record['parent_place_id'])
    for tag in record['name'].keys():
        if "name" not in tag or tag not in tags:
            continue
        parent = ""
        if parent_record and 'name' in parent_record and parent_record['name']:
            if tag in parent_record['name']:
                parent = ", " + parent_record['name'][tag]
        parent = ''
        if a_record:
            add[tag.replace("name", "addr")] = record['name'][tag] + parent + ", " + form_parent_address(connection, fetch_record(connection, a_record['address_place_id']), tag)
        else:
            add[tag.replace("name", "addr")] = record['name'][tag] + parent
    # print(add)
    return add



def fetch_record(connection, place_id):
    if not place_id:
        return None

    sql = "SELECT place_id, parent_place_id, name, address, country_code,\
         housenumber, postcode, rank_search, rank_address from placex \
              where place_id=" + str(place_id)
    # print(sql, "\n")

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)

    record = cursor.fetchone()
    return record

print(get_add(500000, 10000))
