"""
Entity Linking class
"""

import csv, codecs, difflib
from pyjarowinkler import distance as jaro
from ElasticSearchClass import ElasticSearch
import statistics
import triquery


class Entity():
    def __init__(self, doc_id: str, surface_form: str, spacy_type: str, context = ""):
        self.surface_form = surface_form
        self.doc_id = doc_id
        self.spacy_type = spacy_type
        self.context = context

        self.linked_entity = ""
        self.candidates_entities = dict()

        self.elasticsearch_score = 0            # to tune
        self.similarity_score = 0               # to tune
        


class EntityLinking(ElasticSearch):
    def __init__(self):    
        self.holder = None
        self.elastic_search = ElasticSearch()
        self.unmatched_entities = []
        self.single_match_candidate_entities = []
        self.multiple_match_candidate_entities = []

        self.elastic_search_threshold = 4.0
        self.similarity_threshold = 0.8

    def import_entities(self):
        entities = list()
        # Load file with all recognized entity surface forms and the IDs of the documents they were found on.
        with open("intermediate-output.tsv") as tsv:
            for line in csv.reader(tsv, dialect="excel-tab"):
                if len(line) == 4:
                    entity = Entity(line[0], line[1],  line[2], line[3])
                    entities.append(entity)
                elif len(line) == 3:
                    entity = Entity(line[0], line[1],  line[2])
                    entities.append(entity)
                    
        return entities

    def similar(self, string1, string2, method = 'Jaro') -> float:
        score = 0
        
        if method == 'Exact Matching':
            score = 1 if string1 == string2 else 0
        elif method ==  'Sequence Matching':
            score = difflib.SequenceMatcher(None, string1, string2).ratio()
        elif method == 'Jaro':
            score = jaro.get_jaro_distance(string1, string2, winkler=True, scaling=0.1)
        
        return score
    
    def search_elasticsearch(self, query):
        return self.elastic_search.search(self.elastic_search.DOMAIN, query)

    # this method reads the parsed tokes from file and
    # searchs for candidates entities in elasticsearch
    # returns two lists:
    #   - single entities match
    #   - multiple entities match [to disambiguate via trident] 
    def get_elasticsearch_candidate_entities(self):
        entities = self.import_entities()
        
        for entity in entities[0:50]:  
            elastic_search_result = self.search_elasticsearch(entity.surface_form)
            
            if len(elastic_search_result) > 1:
                entity.candidates_entities = elastic_search_result
                self.multiple_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 1:
                entity.linked_entity = list(elastic_search_result.keys())[0]
                self.single_match_candidate_entities.append(entity)

            elif len(elastic_search_result) == 0:
                self.unmatched_entities.append(entity)

    def file_write_entities(self, entities: list(), file_path: str):   
        with open(file_path, 'w', newline='') as myfile:
            for ent in entities:
                try:
                    myfile.write(str(ent.doc_id) + "\t" + str(ent.surface_form) + "\t" + ent.linked_entity + "\n")
                except Exception as e:
                    print(e)
    
    def print_matched_entities(self, entities: list):
        for ent in entities:
            print(str(ent.doc_id) + "\t" + str(ent.surface_form) + "\t" + str(ent.linked_entity) + "\n")

    # returns a list of the entities that can be matched with a candidates
    # based on the criterias decided (elastic search scors ans similarity)
    def get_disambiguable_multiple_match_entities(self) -> list:
        def avg(my_list :list ) -> float: 
            return sum(my_list) / len(my_list)

        def avg_similarity(my_list: list, method: str) -> float:
            sum = 0
            for string in my_list:
                sum = sum + self.similar(entity.surface_form, string, method)
            avg_similarity = sum/ len(my_list)
            return avg_similarity

        #returns a dictionary with fb_id and elastic search avg score and
        # a tuple with only the fb_id and similarity score of the best candidate
        def get_candidates_score( entity):
            keys = list( entity.candidates_entities.keys() )

            max_similarity = 0
            best_candidate_by_similariry = (keys[0], max_similarity)

            candidates_elastic_scores = {}
            
            #loop on all the freebase id returned by elasticsearch
            for key in keys:
                values = list ( entity.candidates_entities[key])
                # filter only the numbers in elastic search return stuff
                string_values = [ x for x in values if type(x) is str ]
                float_values = [ x for x in values if type(x) is not str ]

                avg_elastic_score = avg(float_values)
                candidates_elastic_scores[key] = avg_elastic_score

                avg_similarity_score = avg_similarity(string_values, 'Jaro')
                if(avg_similarity_score > max_similarity):
                    max_similarity = avg_similarity_score
                    best_candidate_by_similariry = (key, max_similarity)

            return candidates_elastic_scores, best_candidate_by_similariry
        
        

        matched_entities = []

        for entity in self.multiple_match_candidate_entities:
            candidates_elastic_scores, best_candidate_by_similariry = get_candidates_score(entity)

            best_elastic_cand_key = max(candidates_elastic_scores, key=candidates_elastic_scores.get)

            entity.elasticsearch_score = candidates_elastic_scores[best_elastic_cand_key]
            entity.similarity_score = best_candidate_by_similariry[1]
            if (candidates_elastic_scores[best_elastic_cand_key] >= self.elastic_search_threshold):
                entity.linked_entity = str(best_elastic_cand_key)
                matched_entities.append(entity)
            elif best_candidate_by_similariry[1] >= self.similarity_threshold:
                entity.linked_entity = str(best_candidate_by_similariry[0])
                matched_entities.append(entity)
            else:
                #print("Checking %s" % entity.surface_form)
                cand = triquery.t.fb_wiki(entity.surface_form.replace(" ", "_"))
                if cand:
                    entity.linked_entity = cand
                    #print("%s\t%s" % (entity.surface_form, cand))
                    matched_entities.append(entity)
        
        return matched_entities