from psycopg2.extras import RealDictCursor, DictCursor, register_hstore
from ESConnection import ESConnection

def form_doc(db_connection, record, tags, index_name='nonminatim'):
    '''
    It forms a doc that can be indexed in elasticsearch

        Parameters:
            connection : postgresql connection to fetch data
            record : The record whose address is to be formed
            tags : list of tags which need to be formed
            index_name (not used) : Nominatim index name can be used to fetch parent addresses

        Returns:
            doc : a dictioanary which needs to be indexed in elasticsearch

    '''
    formed_address = form_address(db_connection, record, tags, index_name)
    doc = formed_address
    doc.update({'place_id': record['place_id']})
    doc.update({'category': record['class']})
    doc.update({'type': record['type']})
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
    return doc

def form_address(connection, record, tags, index_name='nominatim'):
    '''
    Forms addresses for given record with provided tags

        Parameters:
            connection : postgresql connection to fetch data
            record : The record whose address is to be formed
            tags : list of tags which need to be formed
            index_name (not used) : Nominatim index name can be used to fetch parent addresses

        Returns:
            address : dictionary with names using `tags` list elements as keys

    '''
    if not record or not record['name']:
        return {}

    # For places with rank > 29
    if record['rank_search'] > 29:
        parent_address = form_address(connection, fetch_record(connection, record['parent_place_id']), tags)
        address = {}
        for name_tag in record['name']:
            if name_tag in tags:
                address[name_tag.replace("name", "addr")] = record['name'][name_tag]
        for tag in tags:
            if tag.replace("name", "addr") in address and tag.replace("name", "addr") in parent_address:
                address[tag.replace("name", "addr")] += ", " + parent_address[tag.replace("name", "addr")]
        return address

    # For places with rank <= 29
    sql = "SELECT p.name from place_addressline a, placex p\
 where a.isaddress=true and a.place_id = " + str(record['place_id']) + " \
   and a.address_place_id = p.place_id \
	 order by cached_rank_address desc"
    
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)
    
    address = {}
    for name_tag in record['name']:
        if name_tag in tags:
            address[name_tag.replace("name", "addr")] = record['name'][name_tag]

    for parent_record in cursor:
        if not parent_record['name']:
            continue
        for tag in tags:
            if tag in record['name']:
                if tag in parent_record['name']:
                    address[tag.replace("name", "addr")] += ", " + parent_record['name'][tag]   
                elif 'name' in parent_record['name']:
                    address[tag.replace("name", "addr")] += ", " + parent_record['name']['name']
    return address

# Fetches a single record with given place_id
def fetch_record(connection, place_id):
    '''
    Fetches a single record with given place_id
    
        Parameters:
            connection : postgresql connection to fetch data
            place_id : place_id of the place whose record is required

        Returns:
            record : record fetched from DB
    
    '''
    if not place_id:
        return None

    sql = "SELECT place_id, parent_place_id, name, address, country_code,\
         housenumber, postcode, rank_search, rank_address from placex \
              where place_id=" + str(place_id)

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql)

    record = cursor.fetchone()
    return record
