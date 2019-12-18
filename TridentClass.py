import trident

class TridentStub(object):
    def __init__(self):

        self.SPACY_TYPES={ 
        "PERSON" : "PERSON",    #People, including fictional.
        "NORP" : "NORP",        #Nationalities or religious or political groups.
        "FAC" : "FAC",      #Buildings, airports, highways, bridges, etc.
        "ORG" : "ORG",      #Companies, agencies, institutions, etc.
        "GPE" : "GPE",      #Countries, cities, states.
        "LOC" : "LOC",      #Non-GPE locations, mountain ranges
        "PRODUCT" : "PRODUCT",  #Objects, vehicles, foods, etc. (Not ervices.)
        "EVENT" : "EVENT",      #Named hurricanes, battles, wars, sports events
        "WORK_OF_ART" : "WORK_OF_ART",    #Titles of books, songs, etc.
        "LAW" : "LAW",            # documents made into laws.
        "LANGUAGE" : "LANGUAGE",  #Any named language.
        "DATE" : "DATE",          #Absolute or relative dates or periods.
        "TIME" : "TIME",          #Times smaller than a day.
        "PERCENT" : "PERCENT",    #Percentage, including ”%“.
        "MONEY" : "MONEY",        #Monetary values, including unit.
        "QUANTITY" : "QUANTITY",  # Measurements, as of weight or distance.
        "ORDINAL" : "ORDINAL",    #“first”, “second”, etc.
        "CARDINAL" : "CARDINAL"   #Numerals that do not fall under another type
        }

        self.prefix = """
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
        self.TRIDENT_PATH = "/home/jurbani/data/motherkb-trident"
        # self.db = trident.Db(TRIDENT_PATH)

    def compute_query(self, spacy_type: str, freebase_id) -> str:
        
        if spacy_type == self.SPACY_TYPES["PERSON"]:
            query = """
        SELECT ?child
        WHERE
        {
        # ?child  father   Bach
        ?child wdt:P22 wd:Q1339.
        }
        """

        elif spacy_type == self.SPACY_TYPES["NORP"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["FAC"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["ORG"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["GPE"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["LOC"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["EVENT"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["WORK_OF_ART"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["LAW"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["LANGUAGE"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["DATE"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["TIME"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["PERCENT"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["MONEY"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["QUANTITY"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["ORDINAL"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["PERSON"]:
            query = """ insert good query """
        elif spacy_type == self.SPACY_TYPES["CARDINAL"]:
            query = """ insert good query """

        return self.prefix + query

    def run_query(self, query: str ) -> str:
        print(" go query go")
        # result = self.db.sparql(query)  #"SELECT * { ?s ?p ?o .} LIMIT 10")
        return result

    def parse_result(self, result:str):
        print(" nom nom... parsing ...")

if __name__ == "__main__" :
    print("--- TESTIN TRIDENT STUB")
    testTrident = TridentStub()
    query = None #testTrident.compute_query("PERSON")

    result = testTrident.run_query("PERSON")
    print(result)
    