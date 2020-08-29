# GSoC Documentation

This document contains instructions about how to use and setup suggestions for your Nominatim database.

## Suggestions setup

### Elasticsearch indexing

To index your nominatim DB on elasticsearch to avail suggestions, do the following:

* Run `Application.py` with necessary parameters:
    * psql username
    * psql password
    * `mapping.json` can be modified if required.
    * languages to be indexed.
    * other tags to be indexed. (Append into `tags` list)
    * Name your Elasticsearch index (default: nominatim_sugg; search.py also needs to be updated if index name is changed)

This creates the elasticsearch index with addresses.

### Address formation
Addresses formation has the following algorithm:
For each record in placex sorted by rank_address:
* If rank < 30:
    Use the place_addressline table to form the address of the place.
    The addresses are formed in languages mentioned in the next section. If any of the parent places does not have a name in the required language, we add default name over there.
* Else:
    Address is formed as place name, parent_place name

### Language support
Addresses will being formed only in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages.

### Elasticsearch support and queries

The HUG rest API does a prefix match on all the fields.

The javascript code (available [here](https://github.com/krahulreddy/nominatim-ui/blob/suggestions/dist/assets/js/suggest.js)) fetches the results from the HUG rest API. Once the results are fetched, we display the most relevent language options as a list. The language list needs to be updated in the js code as well to get appropriate suggestions. 


## API and Server
The suggestions are provided by a hug API, which is usually hosted on port 8000 of the server. These suggestions are provided by using a prefix search on the elasticsearch index.

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


### Usage
The suggestions can be accessed in the form of json string at https://localhost:8000/autocomplete?q=. The API currently returns the address in zh, sp, en, ar, fr, ru, pt, de, ja and ko languages. The formation of addresses in these languages is discussed in a later section.

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

## Code

The code is available at [https://github.com/krahulreddy/nominatim-indexing](https://github.com/krahulreddy/nominatim-indexing). All the Classes and methods have comments to give an understanding of how they work. 
