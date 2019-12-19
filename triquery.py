import pprint
import requests
import sys
import json

try:
  import trident
except:
  print("run: module load gcc/6.4.0 && module load python/3.5.2 && export PYTHONPATH=/home/jurbani/trident/build-python")




TRIDENT_PATH = "/home/jurbani/data/motherkb-trident"
ELASTIC_SEARCH_HOST = "node001:9200"

PREFIX = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX yago: <http://yago-knowledge.org/resource/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        
        PREFIX fbk: <http://rdf.freebase.com/key/>
        PREFIX fbns: <http://rdf.freebase.com/ns/>
          PREFIX fb_label: <http://www.w3.org/2000/01/rdf-schema#label>
          PREFIX fb_name: <http://rdf.freebase.com/ns/type.object.name>
          PREFIX fb_wiki_key: <http://rdf.freebase.com/key/wikipedia.en>
          PREFIX fb_equiv_webp: <http://rdf.freebase.com/ns/common.topic.topic_equivalent_webpage>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wds: <http://www.wikidata.org/entity/statement/>
        PREFIX wdv: <http://www.wikidata.org/value/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
    """

# Wrapper class to easily make queries to trident
# Queries can either be normal or raw. Normal queries
# have prefixes as defined above included. Raw queries don't.
class triquery(object):
  def __init__(self):
    self.db = trident.Db(TRIDENT_PATH)
  
  #run elastic search query
  def el(self, s : str):
    url = 'http://%s/freebase/label/_search'
    return requests.get(url % ELASTIC_SEARCH_HOST, params={'q' : s, 'size': 1000})

  #run a raw query without any prefixes
  def rq(self, query : str):
      return self.db.sparql(query)

  #run a normal query with standard prefixes
  def q(self, query : str):
      return self.db.sparql(PREFIX + query)

  #pretty print json
  def pp(self, s :str):
      pprint.pprint(json.loads(s))
  
  #run query and pretty print
  def pq(self, query : str):
      self.pp(str(self.q(query)))
  

  def fb_contents(self, fb_id : str):
    qu = """
      SELECT ?1p ?2o
      WHERE {fbns:%s ?1p ?2o.}
    """
    return self.pq(qu % fb_id)

  def fb_names(self, fb_id : str):
    qu = """
      SELECT ?o
      WHERE {
        {fbns:%(fbid)s fbns:type.object.name ?o .}
        UNION
        {fbns:%(fbid)s rdfs:label ?o .} 
        UNION
        { fbns:%(fbid)s fbns:common.notable_for.display_name ?o .
          FILTER (CONTAINS(str(?o),"@en"))
        }
        
      }
    """
    return self.q(qu % {'fbid' : fb_id})
  
  def fb_qknow(self, fb_id : str, prop : str):
    qu = """
     SELECT ?o
     WHERE {
       fbns:%s %s ?o.
     }
    """
    return self.pq(qu % (fb_id, prop))

  def fb_cont_filt(self, fb_id : str, filt : str):
    qu = """
     SELECT ?p ?o
     WHERE {
       fbns:%s ?p ?o.
       %s
     }
    """
    return self.pq(qu % (fb_id, filt))

  def fb_types(self, fb_id : str):
    qu = """
      SELECT ?o
      WHERE {
        {fbns:%s fbns:type.object.type ?o .}
      }
    """
    return self.q(qu % fb_id)
  
  def fb_is_person(self, fb_id : str):
    return "people.person" in self.fb_types(fb_id) 
  
  def fb_for_name(self, name : str):
    qu = """
      SELECT ?s
      WHERE {
        { ?s fbns:type.object.name ?o .}
        UNION
        { ?s rdfs:label ?o .} 
        UNION
        { ?s fbns:common.notable_for.display_name ?o .
        }
        FILTER (CONTAINS(str(?o), "%(n)s"))
      }
    """
    return self.q(qu % {'n' : name})

  def fb_has_name(self, fb_id : str, name : str):
    return name in fb_id 
  
    
  def fb_wiki_links(self, fb_id : str):
    query = """
        SELECT ?o
        WHERE {
            ?s ?p ?o .
            #FILTER(!CONTAINS(str(?s), "http://rdf.freebase.com/ns/"))
            FILTER(CONTAINS(str(?p), "wiki"))
        }
        LIMIT 10
    """
