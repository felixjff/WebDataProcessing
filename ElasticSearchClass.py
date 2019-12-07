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
                id_labels.setdefault(freebase_id, set()).add( freebase_label )
        return id_labels

    def get_entities_labels(self, query: str):

        try:
            query
        except Exception as e:
            print('Usage: python elasticsearch.py DOMAIN QUERY :' + e.__getattribute__)
            sys.exit(0)

        for entity, labels in self.search(self.DOMAIN, query).items():
            print(entity, labels)
