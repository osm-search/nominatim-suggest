from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import hug
import json
import re

@hug.response_middleware()
def CORS(request, response, resource):
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'GET')

@hug.get('/autocomplete')
def pref(q, fuzzy=False, limit=10, factor=50):
    '''
    This provides autocomplete suggestions for given query string

        parameters :
            q: accepts UTF-8 characters. The query string to search against the elasticsearch index.
            limit: The number of results to be returned by the API.
            factor: A parameter to modify the search sorting based on
                    the formula factor => Nominatim importance * factor + elasticsearch_score.
            fuzzy: Provides results with typo tolerence.

        returns :
            results: The autocompletion results have the following format
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
    '''
    if q == '':
        return
    es = Elasticsearch()
    # For fuzzy query - For typo tolerence support
    if fuzzy == 'True':
        print("Fuzzy query")
        res = es.search(index="nominatim_sugg", body={
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
        })
        hits = res['hits']['hits']
        results = {}
        for i, hit in enumerate(hits):
            hit['_source'].update({"calculated_score": hit['sort'][0]})
            results[i] = hit['_source']

        return results

    terms = []
    if type(q) is not list:
        q = [q]
    for i, term in enumerate(q):
        terms += term.strip().split(" ")

    # If the query string is a single word, do simple prefix match
    if len(terms) == 1:
        res = es.search(index="nominatim_sugg", body={
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
        })
    # If the query string has more than one word, we use tokenization.
    # first n-1 words are used to get terms_set matching
    # the last word is used to get prefix matching
    else:
        res = es.search(index="nominatim_sugg", body={
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
        })

    # We modify the results appropriately to return in required format
    hits = res['hits']['hits']
    results = {}
    for i, hit in enumerate(hits):
        hit['_source'].update({"calculated_score": hit['sort'][0]})
        results[i] = hit['_source']

    return results


@hug.get('/prefix_match')
def prefix_match(q, limit=10, factor=50):
    '''
    This provides prefix match autocomplete suggestions for given query string

        parameters :
            q: accepts UTF-8 characters. The query string to search against the elasticsearch index.
            limit: The number of results to be returned by the API.
            factor: A parameter to modify the search sorting based on
                    the formula factor => Nominatim importance * factor + elasticsearch_score.

        returns :
            results: The autocompletion results have the following format
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
    '''
    if q == '':
        return
    es = Elasticsearch()

    # Do simple prefix match to fetch suggestions
    res = es.search(index="nominatim_sugg", body={
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
    })

    # We modify the results appropriately to return in required format
    hits = res['hits']['hits']
    results = {}
    for i, hit in enumerate(hits):
        hit['_source'].update({"calculated_score": hit['sort'][0]})
        results[i] = hit['_source']

    return results
