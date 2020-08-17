from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import hug
import json

@hug.response_middleware()
def CORS(request, response, resource):
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.set_header(
        'Access-Control-Allow-Headers',
        'Authorization,Keep-Alive,User-Agent,'
        'If-Modified-Since,Cache-Control,Content-Type'
    )
    response.set_header(
        'Access-Control-Expose-Headers',
        'Authorization,Keep-Alive,User-Agent,'
        'If-Modified-Since,Cache-Control,Content-Type'
    )
    if request.method == 'OPTIONS':
        response.set_header('Access-Control-Max-Age', 1728000)
        response.set_header('Content-Type', 'text/plain charset=UTF-8')
        response.set_header('Content-Length', 0)
        response.status_code = hug.HTTP_204

hug.defaults.cli_output_format = hug.output_format.html

@hug.get('/autocomplete')
def pref(q, limit=10, factor=50):
    if q == '':
        return
    es = Elasticsearch()
    print(q)
    f = factor
    res = es.search(index="nominatim_sugg", body={
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": q,
                        "type": "phrase_prefix"
                    }
                }
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

    return json.dumps(results, ensure_ascii=False)
