"""
Entity Linking class
"""

import csv, codecs, difflib, Levenshtein, distance
from ElasticSearchClass import ElasticSearch 

class Entity():
    def __init__(self, token: str):
        self.token = token
        self.linked_entity = dict()
        self.candidates_entities = []

class EntityLinking(ElasticSearch):
    def __init__(self):    
        self.holder = None
        self.elastic_search = ElasticSearch()
        
    def import_entities(self):
        entities = []
        # Load file with all recognized entity surface forms and the IDs of the documents they were found on.
        with open("data/sample-output.tsv") as tsv:
            for line in csv.reader(tsv, dialect="excel-tab"):
                entities.append(line)
        
        return entities

    def similar(self, method, threshold, string1, string2):
        link = 0
        score = 0

        
        if method == 'Exact Matching':
            score = 1 if string1 == string2 else 0
            link = 1 if score else 0
        elif method ==  'Sequence Matching':
            score = difflib.SequenceMatcher(None, string1, string2).ratio()
            link = 1 if score > threshold else 0
        """
        elif method == 'Levenshtein':
            score = Levenshtein.ratio(string1, string2)
            link = 1 if score > threshold else 0
        elif method == 'Sorensen':
            score = 1 - distLevenshteinance.jaccard(string1, string2)
            link = 1 if score > threshold else 0
        """
        
        if link:
            return link, score 
        else: 
            return None, None
    
    def local_kdb_file_linking(self, entity, method, file = None, threshold = None):
        # Open local KDB file
        with open("data/sample-labels-cheat.txt") as tsv:
            # Extract the candidate entities from the KDB together with their Freebase entity IDs and similarity score
            entity_candidates = []
            for line in csv.reader(tsv, dialect="excel-tab"):
                link, score = self.similar(method, entity, line[0], threshold)
                if link:
                    entity_candidates.append(line.append(score))
        # Get entity with highest score by sorting on ascending order
        entity_candidates.sort(key=lambda x: x[3])
        # Return Freebase ID
        return entity_candidates[-1][1]
    
    def search_elasticsearch(self, query):
        return self.elastic_search.search(self.elastic_search.DOMAIN, query)

    # def write_in_file_single_match_entities(self, )

    # this method reads the parsed tokes from file and
    # searchs for candidates entities in elasticsearch
    # returns two lists:
    #   - single entities match
    #   - multiple entities match [to disambiguate via trident] 
    def get_elasticsearch_candidate_entities(self):
        tokens = self.import_entities()

        unmatched_tokens = []
        single_match_candidate_entities = []
        multiple_match_candidate_entities = []
        
        for token in tokens[0:1000]:
            #print(token[2])
            
            elastic_search_result = self.search_elasticsearch(token[1])
            #print(elastic_search_result)
            
            if len(elastic_search_result) > 1:
                entity = Entity(token[2])
                entity.candidates_entities.append(elastic_search_result)
                multiple_match_candidate_entities.append(entity)
            elif len(elastic_search_result) == 1:

                entity = Entity(token[2])
                entity.linked_entity = elastic_search_result
                single_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 0:
                unmatched_tokens.append(token)
            
        return single_match_candidate_entities,multiple_match_candidate_entities, unmatched_tokens


if __name__ == "__main__" :
    print("--- TESTIN entity linking")
    entity_linking = EntityLinking()
    # entities = entity_linking.import_entities()
    # print("--- looking into elastic search for " + entities[0][1] + " \n")
    # fb_result = self.search_elasticsearch(entities[0][1])
    # print("--- The result is :\n")
    # print(fb_result)
    s, m, u = entity_linking.get_elasticsearch_candidate_entities()

    print("single match found -> ", len(s))
    print("multiple match found -> ", len(s))
    print("unmatch found -> ", len(s))

    if(len(s) > 1):
        print("\ntoken .> ", s[0].token)
        print("\nentity -> ", s[0].linked_entity)

