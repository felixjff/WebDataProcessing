import requests
import sys

class ElasticSearch(object):

    def __init__(self):
        self.port = "9200"
        self.ELASTIC_SEARCH_SERVER = None
        self.node = "node001"
        self.DOMAIN = self.node+":"+self.port
        self.st = None

    def search(self, domain, query):
        url = 'http://%s/freebase/label/_search' % domain
        response = requests.get(url, params={'q': query, 'size':1000})
        id_labels = {}
        if response:
            response = response.json()
            for hit in response.get('hits', {}).get('hits', []):
                freebase_label = hit.get('_source', {}).get('label')
                freebase_id = hit.get('_source', {}).get('resource')
                score = hit.get('_score', 0)
                id_labels.setdefault(freebase_id, set()).add( freebase_label )
                id_labels.setdefault(freebase_id).add(score)
        return id_labels