# GSoC Documentation

This document contains instructions about how to use and setup suggestions for your Nominatim database.

## Elasticsearch indexing

To index your nominatim DB on elasticsearch to avail suggestions, do the following:

* Make sure elasticsearch is running (setup instructions in next sections)
* Run `Application.py` with necessary parameters:
    * psql username
    * psql password
    * `mapping.json` can be modified if required.
    * languages to be indexed.
    * other tags to be indexed. (Append into `tags` list)
    * Name your Elasticsearch index (default: nominatim_sugg; search.py also needs to be updated if index name is changed)

This creates the elasticsearch index with addresses.

### Debugging the indexing process

There are debug statements in the code made by `logging.debug`, `looging.info`. Currently, these are being redirected to `output.log`. You can change the file name or redirect to stdout my modifying the line

    logging.basicConfig(filename='output.log',level=logging.INFO)

in `Application.py`.

Elasticsearch bulk indexing is performed after every 10000 docs are formed. This size can be modified by changing the bucket_size parameter in `Application.py`.

## How are addresses formed?

Addresses formation has the following algorithm:
For each record in placex sorted by rank_address:
* If rank < 30:
    Use the place_addressline table to form the address of the place.
    The addresses are formed in languages mentioned in the next section. If any of the parent places does not have a name in the required language, we add default name over there.
* Else:
    Address is formed as place name, parent_place name

## Language support
<table>
<tr><td>Language Code</td><td>Language</td></tr>
<tr><td>zh</td><td>Chinese</td></tr>
<tr><td>sp</td><td>Spanisn</td></tr>
<tr><td>en</td><td>English</td></tr>
<tr><td>ar</td><td>Arabic</td></tr>
<tr><td>fr</td><td>French</td></tr>
<tr><td>ru</td><td>Russian</td></tr>
<tr><td>pt</td><td>Portugese</td></tr>
<tr><td>de</td><td>German</td></tr>
<tr><td>ja</td><td>Japanese</td></tr>
<tr><td>ko</td><td>Korean</td></tr>
</table>
Addresses are formed in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages in the hosted server. For changing this language set, just add the language code into the `languages` list in `Appliction.py`. To add extra tags for indexing(ex: house_name), simply append it to the `tags` list in `Application.py`.

> **Note:** You need not add these new tags/languages in `mapping.json`, since we are relying on the default mapping provided by elasticsearch.


## API and Server
The suggestions are provided by a hug API, which is usually hosted on port 8000 of the server. These suggestions are provided by using a prefix search on the elasticsearch index.

> **Important:** Hug only provides http endpoint. If you need to access these suggestions on a https site, you need to manually set up forwarding of the API endpoint.

### Installation and setup
Reqirements to provide the suggestions:
* Elasticsearch server should be running.
    Download and run elasticsearch from [here](https://www.elastic.co/downloads/elasticsearch). Version 7.8 is used in this project.

    The elasticsearch python client is used in the suggestion API. The client can be installed using

        pip3 install elasticsearch

* HUG rest API
    The search suggestions API for elasticsearch is provided by es.py. It uses hug.rest.

        pip3 install hug -U

    Start hosting the file by using

        hug -f filename

### Running and Debugging

To start the elasticsearch server, run

    cd path/to/elasticsearch-7.8.0/bin
    ./elasticsearch

For our project, we have `search.py`. This file is currently available [here](https://github.com/krahulreddy/nominatim-indexing/blob/master/search.py).

    hug -f search.py -p 8000

The logs from search.py and the elasticsearch logs should be enough for debugging any issues with suggestions.

### Usage
The suggestions can be accessed in the form of json string at https://localhost:8000/autocomplete?q=. The API currently returns the address in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages.

The sample output format is:

        {
            "0": {
                    "addr": "",
                    ...
                    "place_id": ,
                    "postcode": ,
                    "importance": ,
                    "country_code": ,
                    "calculated_score": 
            },
            "1": {
                ...
            },
            ...
        } 

#### API Parameters

- `q`: accepts UTF-8 characters. The query string to search against the elasticsearch index.
- `limit`: The number of results to be returned by the API.
- `factor`: A paramaeter to modify the search sorting based on the formula factor => Naminatim importance * factor + elasticsearch_score. This can be modified to get appropriate results. This is not required after finalizing the appropriate factor value.
- `fuzzy`: Provides results with typo tolerence.

### Elasticsearch queries

For all the queries, we sort the results based on the importance score calculated by [wiki importance or {0.75 - record['rank_search'] / 40}] * factor + elasticsearch score.

The HUG rest API has two suggestion endpoints:

1. `autocomplete`: Provides tokenized suggestions.

    Query body for Fuzzy query (For typo tolerence):

        {
            "query": {
                "fuzzy": {
                    "addr": {
                        "value": q
                    }
                }
            },
            "sort": {
                "_script": {
                    "type": "number",
                    "script": {
                        "source": "doc[\"importance\"].value * params.factor + _score",
                        "params": {
                            "factor": 50
                        }
                    },
                "order": "desc"
                }
            },
            "size": limit
        }

    Query for single word queries (Direct prefix match)

        {
            "query": {
                "multi_match": {
                    "query": terms[-1],
                    "type": "phrase_prefix"
                }
            },
            "sort": {
                "_script": {
                    "type": "number",
                    "script": {
                        "lang": "painless",
                        "source": "doc[\"importance\"].value * " + str(factor) + " + _score",
                        "params": {
                            "factor": factor
                        }
                    },
                "order": "desc"
                }
            },
            "size": limit
        }

    If the query string has more than one word, we use tokenization. First n-1 words are used to get terms_set matching. The last word is used to get prefix matching.

        {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": terms[-1],
                                "type": "phrase_prefix"
                            }
                        },
                        {
                            "terms_set": {
                                "addr": {
                                    "terms": terms[:-1],
                                    "minimum_should_match_script": {
                                        "source": "params.num_terms"
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            "sort": {
                "_script": {
                    "type": "number",
                    "script": {
                        "lang": "painless",
                        "source": "doc[\"importance\"].value * " + str(factor) + " + _score",
                        "params": {
                            "factor": factor
                        }
                    },
                "order": "desc"
                }
            },
            "size": limit
        }

2. `prefix_match`: Provides suggestions based on prefix match
    
    The search term `q` is used to get prefix_match from the elasticsearch index.

        {
            "query": {
                "multi_match": {
                    "query": q,
                    "type": "phrase_prefix"
                }
            },
            "sort": {
                "_script": {
                    "type": "number",
                    "script": {
                        "lang": "painless",
                        "source": "doc[\"importance\"].value * " + str(factor) + " + _score",
                        "params": {
                            "factor": factor
                        }
                    },
                "order": "desc"
                }
            },
            "size": limit
        }

### Elasticsearch support and queries

The javascript code (available [here](https://github.com/krahulreddy/nominatim-ui/blob/suggestions/dist/assets/js/suggest.js)) fetches the results from the HUG rest API. Once the results are fetched, we display the most relevent language options as a list. The language list needs to be updated in the js code as well to get appropriate suggestions.

The javascript code makes sure the results are formatted

#### For reusing the suggestions setup

Make sure [suggestions.js](https://github.com/krahulreddy/nominatim-ui/blob/suggestions/dist/assets/js/suggest.js) and [suggestions.css](https://github.com/krahulreddy/nominatim-ui/blob/suggestions/dist/assets/css/suggest.css) are included in your setup. The search division must be similar to the search bar [here](https://github.com/krahulreddy/nominatim-ui/blob/suggestions/dist/search.html#L149). That exact division can be used along with the two files to start getting suggestions.

## Code

The code is available at [https://github.com/krahulreddy/nominatim-indexing](https://github.com/krahulreddy/nominatim-indexing). All the Classes and methods have comments to give an understanding of how they work. 
