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

    To start the elasticsearch server, run

        cd path/to/elasticsearch-7.6.2/bin
        ./elasticsearch

* HUG rest API
    The search suggestions API for elasticsearch is provided by es.py. It uses hug.rest.

        pip3 install hug -U

    Start hosting the file by using

        hug -f filename

    For our project, we have search.py. This file is currently available [here](https://github.com/krahulreddy/Nominatim/blob/gsoc/search.py). You can host this file from anywhere.

        hug -f search.py -p 8000


### Running and Debugging
The logs from the 

## Code


## Suggestions setup
### Address formation
Addresses are being formed only in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages.

### Language support

### Elasticsearch support and queries

