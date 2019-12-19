"""
Entity Linking class
"""

import csv, codecs, difflib, distance
from pyjarowinkler import distance as jaro
from ElasticSearchClass import ElasticSearch
import statistics

class Entity():
    def __init__(self, doc_id: str, surface_form: str, spacy_type: str, context = ""):
        self.surface_form = surface_form
        self.doc_id = doc_id
        self.spacy_type = spacy_type
        self.context = context

        self.linked_entity = ""
        self.candidates_entities = dict()

        self.elasticsearch_score = 0            # to tune
        self.linked_entity_similarity = dict()  # to tune
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
        with open("data/sample-output.tsv") as tsv:
            for line in csv.reader(tsv, dialect="excel-tab"):
                if len(line) == 4:
                    entity = Entity(line[0], line[1],  line[2], line[3])
                    entities.append(entity)
                elif len(line) == 3:
                    entity = Entity(line[0], line[1],  line[2])
                    entities.append(entity)
                else:
                    print("FOUND LINE OF SIZE " + str(len(line)))
        
        return entities

    def similar(self, string1, string2, method = 'Jaro') -> float:
        score = 0
        
        if method == 'Exact Matching':
            score = 1 if string1 == string2 else 0
        elif method ==  'Sequence Matching':
            score = difflib.SequenceMatcher(None, string1, string2).ratio()
        elif method == 'Sorensen':
            score = 1 - distance.jaccard(string1, string2)
        elif method == 'Jaro':
            score = jaro.get_jaro_distance(string1, string2, winkler=True, scaling=0.1)
        
        return score 
    
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

                entity.elasticsearch_score = max# to tune
            return entity.candidates_entities[max_key]

        for entity in entities:
            entity.linked_entity = get_candidate_entity_with_higher_avg_score(entity)

    def discriminate(self, entities: list):
        def avg(my_list :list ) -> float: 
            return sum(my_list) / len(my_list)

        def avg_similarity(my_list: list, method: str) -> float:
            sum = 0
            for string in my_list:
                sum = sum + self.similar(entity.surface_form, string, method)
            avg_similarity = sum/ len(my_list)
            return avg_similarity

        #returns a dictionary with fb_id and elastic search avg score and
        # a dctionary with only the fb_id and similarity score of the best candidate
        def get_candidates_score( entity) -> dict:
            keys = list( entity.candidates_entities.keys() )
            max = 0
            max_key = keys[0]

            max_similarity = 0

            candidates_elastic_scores = {}
            best_candidate_by_similariry = ()

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

        for entity in entities:
            candidates_elastic_scores, best_candidate_by_similariry = get_candidates_score(entity)

            best_elastic_cand = max(candidates_elastic_scores, key=candidates_elastic_scores.get)

            if (candidates_elastic_scores[best_elastic_cand] >= self.elastic_search_threshold):
                entity.linked_entity = best_elastic_cand
            elif best_candidate_by_similariry[1] >= self.similarity_threshold:
                entity.linked_entity = best_candidate_by_similariry[0]        

    def discriminate_on_elasticsearch_score_and_similarity(self, entities: list, method = "Jaro"):
        def avg(my_list :list ) -> float: 
            return sum(my_list) / len(my_list)

        def get_candidate_entity_with_higher_avg_score( entity) -> dict:
            keys = list( entity.candidates_entities.keys() )
            #max = 0
            max_key = keys[0]
            max_similarity = 0

            #loop on all the freebase id returned by elasticsearch
            for key in keys:
                values = list ( entity.candidates_entities[key])
                # filter only the numbers in elastic search return stuff
                #float_values = [ x for x in values if type(x) is not str ]
                #if avg( float_values ) > max:
                #    max = avg( float_values )
                #    max_key = key

                string_values = [ x for x in values if type(x) is str ]
                sum = 0
                for string in string_values:
                    sum = sum + self.similar(entity.surface_form, string, method)
                avg_similarity = sum/ len(string_values)
                if(avg_similarity > max_similarity):
                    max_similarity = avg_similarity
                    max_key = key
                
                entity.similarity_score = max_similarity # to tune
            return entity.candidates_entities[max_key]

        for entity in entities:
            entity.linked_entity_similarity = get_candidate_entity_with_higher_avg_score(entity)     # to tune          

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

    #entity_linking.discriminate_on_elasticsearch_score(entity_linking.multiple_match_candidate_entities)

    #entity_linking.discriminate_on_elasticsearch_score_and_similarity(    entity_linking.multiple_match_candidate_entities)

    entity_linking.discriminate(entity_linking.multiple_match_candidate_entities)

    sum_similarity_score = 0
    sum_elastic_score = 0
    max_similarity = 0
    max_elastic_score = 0
    elastic_score_list =[]
    similarity_score_list = []

    
    for entity in entity_linking.multiple_match_candidate_entities:
        """
        print("NAME: " + entity.surface_form + " TYPE "  + entity.spacy_type + " SC SCORE " + str(entity.elasticsearch_score) + " SIM SCORE " + str(entity.similarity_score) + " EL LINK " + str(entity.linked_entity) + " SM LINK " + str(entity.linked_entity_similarity) + " CONTEXT " + str(entity.context) + "\n CANDIDATES ENTITY: \n" + str(entity.candidates_entities) + "\n")
        """
        similarity_score_list.append(entity.similarity_score)
        elastic_score_list.append(entity.elasticsearch_score)
        

    avg_similarity_score = statistics.mean(similarity_score_list)
    avg_elastic_score = statistics.mean(elastic_score_list)

    median_similarity = statistics.median(similarity_score_list)
    median_elastic =  statistics.median(elastic_score_list)

    std_similarity = statistics.stdev(similarity_score_list)
    std_elastic = statistics.stdev(elastic_score_list)

    print("AVG similarity: " + str(avg_similarity_score))
    print("MEDIAN similarity: " + str(median_similarity))
    print("STD similarity: " + str(std_similarity))
    print("AVG elasticsearch " + str(avg_elastic_score))
    print("MEDIAN elasticsearch " + str(median_elastic))
    print("STD elastic: " + str(std_elastic))

    #entity_linking.file_write_entities(s, "test/multi-output.tsv")

