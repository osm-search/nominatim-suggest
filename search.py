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
    if q == '':
        return
    es = Elasticsearch()
    print(fuzzy)
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
            }
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

    print(terms)
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
    hits = res['hits']['hits']
    results = {}
    for i, hit in enumerate(hits):
        hit['_source'].update({"calculated_score": hit['sort'][0]})
        results[i] = hit['_source']

    return results
