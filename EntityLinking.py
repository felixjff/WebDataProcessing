"""
Entity linking workflow
"""

# Import entity linking class with methods
from WebDataProcessing import EntityLinking

#Initialize entity linking class to utilize it's methods
entity_linking = EntityLinking()

#Import entities recognized on NLP preprocessing (entity recognition) stage
entities = entity_linking.import_entities()

#Query candidate Freebase matches using ElasticSearch server
candidates = {}
for e in entities:
    # Dictionary stores all candidates and their scores found on Freebase per entity
    candidates[e[1]] = entity_linking.search_freebase()
    print('Found '+str(len(candidates[e[1]]))+" candidates for entity "+ e[1])
    