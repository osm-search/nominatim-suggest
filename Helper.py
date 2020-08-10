from psycopg2.extras import RealDictCursor, DictCursor, register_hstore

# It forms a doc that can be indexed in elasticsearch.
def form_doc(db_connection, record, tags):
    formed_address = form_address(db_connection, record, tags)
    doc = formed_address
    doc.update({'place_id': record['place_id']})
    if 'osm_id' in record:
        doc.update({'osm_id': record['osm_id'], 'osm_type': record['osm_type']})
    if record['postcode']:
        doc.update({'postcode': record['postcode']})
    if 'importance' in record:
        doc.update({'importance': record['importance']})
    if record['country_code']:
        doc.update({'country_code': record['country_code']})
    # print(doc)
    return doc

def form_address(connection, record, tags):

    sql = "SELECT * from place_addressline where isaddress=true and place_id = " + str(record['place_id']) + " order by cached_rank_address desc"

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)
    
    address = {}
    for name_tag in record['name']:
        if name_tag in tags:
            address[name_tag.replace("name", "addr")] = record['name'][name_tag]
    for a_record in cursor:
        parent_record = fetch_record(connection, a_record['address_place_id'])
        if not parent_record['name']:
            continue
        for tag in tags:
            if tag in record['name']:
                if tag in parent_record['name']:
                    # print(parent_record['name']['tag'], end=', ')
                    address[tag.replace("name", "addr")] += ", " + parent_record['name'][tag]   
                elif 'name' in parent_record['name']:
                    address[tag.replace("name", "addr")] += ", " + parent_record['name']['name']
    if not address:
        print(record['place_id'], record['name'])
    return address



# Recursively forms address of parent places in the required language
# returns a string containing the address
def form_parent_address(connection, record, tag):
    if record["rank_search"] < 5:
        if record['name'] and record['name']['name']:
            
            return record['name']['name']
        return record['name']
    
    sql = "SELECT * from place_addressline where isaddress=true and place_id = " + str(record['place_id'])

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

# Forms the address of a place in all languages mentioned in the `tag` list
# returns a dictionary with the available tags and the address strings
def form_address1(connection, record, tags):
    if not record['name']:
        return {"addr": ""}
    if record["rank_search"] < 5:
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
                add[tag.replace("name", "addr")] = record['name'][tag] + parent
        return add
    
    sql = "SELECT * from place_addressline where isaddress=true and place_id = " + str(record['place_id'])


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
    return add


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
