from psycopg2.extras import RealDictCursor, DictCursor, register_hstore
from ESConnection import ESConnection

# It forms a doc that can be indexed in elasticsearch.
def form_doc(db_connection, record, tags, index_name='nonminatim'):
    formed_address = form_address(db_connection, record, tags, index_name)
    doc = formed_address
    doc.update({'place_id': record['place_id']})
    if 'osm_id' in record:
        doc.update({'osm_id': record['osm_id'], 'osm_type': record['osm_type']})
    if record['postcode']:
        doc.update({'postcode': record['postcode']})
    if record['importance']:
        doc.update({'importance': float(record['importance'])})
    else:
        doc.update({'importance': 0.75 - float(record['rank_search']) / 40})
    if record['country_code']:
        doc.update({'country_code': record['country_code']})
    # print(doc)
    return doc

def form_address(connection, record, tags, index_name='nominatim'):
    if not record or not record['name']:
        return {}
    if record['rank_search'] > 29:
        parent_address = form_address(connection, fetch_record(connection, record['parent_place_id']), tags)
        address = {}
        for name_tag in record['name']:
            if name_tag in tags:
                address[name_tag.replace("name", "addr")] = record['name'][name_tag]
        for tag in tags:
            if tag.replace("name", "addr") in address and tag.replace("name", "addr") in parent_address:
                address[tag.replace("name", "addr")] += ", " + parent_address[tag.replace("name", "addr")]
        # print(address)
        return address

    sql = "SELECT p.name from place_addressline a, placex p\
 where a.isaddress=true and a.place_id = " + str(record['place_id']) + " \
   and a.address_place_id = p.place_id \
	 order by cached_rank_address desc"
    
    # print(record['rank_search'], record['rank_address'])
    # print(sql)

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)
    
    address = {}
    for name_tag in record['name']:
        if name_tag in tags:
            address[name_tag.replace("name", "addr")] = record['name'][name_tag]

    # print(address)
    for parent_record in cursor:
        # print(parent_record)
        if not parent_record['name']:
            continue
        # print('bleh')
        for tag in tags:
            if tag in record['name']:
                if tag in parent_record['name']:
                    # print(parent_record['name']['tag'], end=', ')
                    address[tag.replace("name", "addr")] += ", " + parent_record['name'][tag]   
                elif 'name' in parent_record['name']:
                    address[tag.replace("name", "addr")] += ", " + parent_record['name']['name']
    # print(address)
    return address

# Fetches a single record with given place_id
def fetch_record(connection, place_id):
    if not place_id:
        return None

    sql = "SELECT place_id, parent_place_id, name, address, country_code,\
         housenumber, postcode, rank_search, rank_address from placex \
              where place_id=" + str(place_id)

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)

    record = cursor.fetchone()
    return record



        # es = ESConnection()
        # parent_address = es.search_with_place_id(index_name, record['parent_place_id'])
        # if not parent_address:
