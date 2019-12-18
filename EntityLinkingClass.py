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
        self.candidates_entities = dict()

class EntityLinking(ElasticSearch):
    def __init__(self):    
        self.holder = None
        self.elastic_search = ElasticSearch()
        self.unmatched_entities = []
        self.single_match_candidate_entities = []
        self.multiple_match_candidate_entities = []
        
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

    # this method reads the parsed tokes from file and
    # searchs for candidates entities in elasticsearch
    # returns two lists:
    #   - single entities match
    #   - multiple entities match [to disambiguate via trident] 
    def get_elasticsearch_candidate_entities(self):
        entities = self.import_entities()
        
        for entity in entities[0:100]:
            #print(token[2])
            
            elastic_search_result = self.search_elasticsearch(entity.surface_form)
            #print(elastic_search_result)
            
            if len(elastic_search_result) > 1:
                #entity = Entity(token[0], token[1], token[2])
                entity.candidates_entities = elastic_search_result
                self.multiple_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 1:
                #entity = Entity(token[0], token[1], token[2])
                entity.linked_entity = elastic_search_result
                self.single_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 0:
                #entity = Entity(token[0], token[1],  token[2])
                self.unmatched_entities.append(entity)

    def file_write_entities(self, entities: list(), file_path: str):   
        with open(file_path, 'a', newline='') as myfile:
            for ent in entities:
                try:
                    myfile.write(str(ent.doc_id) + "\t" + str(ent.surface_form) + "\t" + list(ent.linked_entity.keys())[0] + "\n")
                except Exception as e:
                    print(e)

    #it is meant to have in input the multiple match from elastic search
    #a and to select the entity from them based on elastic search avg score
    def discriminate_on_elasticsearch_score(self, entities: list):

        def avg(my_list :list ) -> float: 
            return sum(my_list) / len(my_list)

        def get_candidate_entity_with_higher_avg_score( entity) -> dict:
            keys = list( entity.candidates_entities.keys() )
            max = 0
            max_key = keys[0]

            #loop on all the freebase id returned by elasticsearch
            for key in keys:
                values = list ( entity.candidates_entities[key])
                # filter only the numbers in elastic search return stuff
                float_values = [ x for x in values if type(x) is not str ]
                if avg( float_values ) > max:
                    max = avg( float_values )
                    max_key = key
            return entity.candidates_entities[max_key]

        for entity in entities:
            entity.linked_entity = get_candidate_entity_with_higher_avg_score(entity)
                

if __name__ == "__main__" :
    print("--- TESTIN entity linking")
    entity_linking = EntityLinking()
    # entities = entity_linking.import_entities()
    # print("--- looking into elastic search for " + str(entities[0]) + " \n")
    # fb_result = self.search_elasticsearch(entities[0][1])
    # print("--- The result is :\n")
    # print(fb_result)
    
    entity_linking.get_elasticsearch_candidate_entities()

    print("single match found -> ", len(entity_linking.single_match_candidate_entities))
    print("multiple match found -> ", len(entity_linking.multiple_match_candidate_entities))
    print("unmatch found -> ", len(entity_linking.unmatched_entities))

    """
    if(len(s) > 1):
        print("\nsurface_form .> ", s[0].surface_form)
        print("\nlinked_entity -> ", s[0].linked_entity)
    """
    """
    if(len(u) > 1):
        print("\n----------------UNMATCHED:\n")
        for un in u:
            print("\nsurface_form .> ", un.surface_form)
    """
    """
    if(len(ms) > 1):
        print("\n----------------multi matched:\n")
        for m in ms:
            print("\nsurface_form .> ", m.surface_form)
            print("candidates_entity -> ", m.candidates_entities)
            print("\n")
    """

    #entity_linking.file_write_entities(s, "test/test-output.tsv")

    entity_linking.discriminate_on_elasticsearch_score(entity_linking.multiple_match_candidate_entities)