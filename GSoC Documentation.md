# GSoC Documentation
## API and Server
The suggestions are provided by a hug API, which is usually hosted on port 8000 of the server. These suggestions are provided by using a prefix search on the elasticsearch index.

### Usage
The suggestions can be accessed in the form of json string at http://95.217.117.45:8000/pref?q=. The query parameter `q` accepts UTF-8 characters. The server then queries it against the elasticsearch index. The API currently returns the address in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages. The formation of addresses in these languages is discussed in a later section.

The sample output for http://95.217.117.45:8000/pref?q=vensa%20royal is:


### Installation and setup
Reqirements to provide the suggestions:
* Elasticsearch server should be running.
    Download and run elasticsearch from [here](https://www.elastic.co/downloads/elasticsearch). Version 7.6.2 is used in this project.

    The elasticsearch python client is used in the suggestion API. The client can be installed using

        pip3 install elasticsearch

* HUG rest API
    The search suggestions API for elasticsearch is provided by es.py. It uses hug.rest.

        pip3 install hug -U

    Start hosting the file by using

        hug -f filename

### Running and Debugging

To start the elasticsearch server, run

    cd path/to/elasticsearch-7.6.2/bin
    ./elasticsearch

For our project, we have search.py. This file is currently available [here](https://github.com/krahulreddy/Nominatim/blob/gsoc/search.py). You can host this file from anywhere.

    hug -f search.py -p 8000


The logs from search.py and the elasticsearch logs should be enough for debugging any issues with suggestions. 

## Code

The code is available at [https://github.com/krahulreddy/nominatim-indexing](https://github.com/krahulreddy/nominatim-indexing). All the Classes and methods have comments to give an understanding of how they work. 

## Suggestions setup
### Address formation
Addresses formation has the following algorithm:
For each record in placex sorted by rank_address:
* If rank < 30:
    Use the place_addressline table to recursively form the address of the place.
    The addresses are formed in languages mentioned in the next section. If any of the parent places does not have a name in the required language, we add default name over there.
* Else:
    Address is formed as place name, parent_place name

### Language support
Addresses will being formed only in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages.

### Elasticsearch support and queries

The HUG rest API does a prefix match on all the fields.

The javascript code (available [here]()) fetches the results from the HUG rest API. Once the results are fetched, we display the most relevent language options as an option list. 
