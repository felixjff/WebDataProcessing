"""
Entity Linking class
"""

import csv, codecs, difflib, Levenshtein, distance
from ElasticSearchClass import ElasticSearch 

class Entity():
    def __init__(self, doc_id: str, surface_form: str, spacy_type: str):
        self.surface_form = surface_form
        self.doc_id = doc_id
        self.spacy_type = spacy_type
        self.linked_entity = dict()
        self.candidates_entities = []        

class EntityLinking(ElasticSearch):
    def __init__(self):    
        self.holder = None
        self.elastic_search = ElasticSearch()
        
    def import_entities(self):
        entities = list()
        # Load file with all recognized entity surface forms and the IDs of the documents they were found on.
        with open("data/sample-output.tsv") as tsv:
            for line in csv.reader(tsv, dialect="excel-tab"):
                entity = Entity(line[0], line[1],  line[2])
                entities.append(entity)
        
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
        entities = self.import_entities()

        unmatched_tokens = []
        single_match_candidate_entities = []
        multiple_match_candidate_entities = []
        
        for entity in entities[0:1000]:
            #print(token[2])
            
            elastic_search_result = self.search_elasticsearch(entity.surface_form)
            #print(elastic_search_result)
            
            if len(elastic_search_result) > 1:
                #entity = Entity(token[0], token[1], token[2])
                entity.candidates_entities.append(elastic_search_result)
                multiple_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 1:
                #entity = Entity(token[0], token[1], token[2])
                entity.linked_entity = elastic_search_result
                single_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 0:
                #entity = Entity(token[0], token[1],  token[2])
                unmatched_tokens.append(entity)
            
        return single_match_candidate_entities,multiple_match_candidate_entities, unmatched_tokens

    def file_write_entities(self, entities: list(), file_path: str):   
        with open(file_path, 'a', newline='') as myfile:
            for ent in entities:
                try:
                    myfile.write(str(ent.doc_id) + "\t" + str(ent.surface_form) +"\n")
                except Exception as e:
                    print(e)


if __name__ == "__main__" :
    print("--- TESTIN entity linking")
    entity_linking = EntityLinking()
    # entities = entity_linking.import_entities()
    # print("--- looking into elastic search for " + str(entities[0]) + " \n")
    # fb_result = self.search_elasticsearch(entities[0][1])
    # print("--- The result is :\n")
    # print(fb_result)
    
    s, m, u = entity_linking.get_elasticsearch_candidate_entities()

    print("single match found -> ", len(s))
    print("multiple match found -> ", len(m))
    print("unmatch found -> ", len(u))

    if(len(s) > 1):
        print("\nsurface_form .> ", s[0].surface_form)
        print("\nlinked_entity -> ", s[0].linked_entity)
        

