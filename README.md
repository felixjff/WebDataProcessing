# wdps2019
Web Data Processing Systems 2019 (VU course XM_40020)
Group: 13 

# Assignment: Large Scale Entity Linking

The assignment consists of developing a program that performs entity recognition and entity linking. 
The program should receive in input a gzipped [WARC file](https://en.wikipedia.org/wiki/Web_ARChive),
retrieve entities from records of web content from a variety of sources, generate candidate entities 
from one or multiple knowledge bases and link the entity to the most appropriate candidate. The program 
should return in output a three-column tab-separated file with document IDs, entity surface forms (like
"Berlin"), and Freebase entity IDs (like "/m/03hrz").  

## Set-up

The methods implemented within the program have dependencies. At the moment the program is run we
must ensure these dependencies are available. Therefore, importing, loading and exporting is a part 
of the setup.sh script, which is invoked by the run.sh script.

The program is written in Python. All methods and tasks are encapsulated into classes. Methods 
for entity recognition can be found on the EntityRecognition class on the file EntityRecognitionClass.py.
Methods for entity linking can be found on the EntityLinking class on the file EntityLinkingClass.py.
EntityLinking inherits from ElastichSearch class, which contains the methods to request candidate entities 
from FreeBase. Everything is then put together in the main.py file.
The submission also contain a file called triquery.py. This file contains some methods and code intended
for the purpose of querying Trident. Unfortunately, we did not have time to finish implementing this functionality
in combination with the rest of our entity linking.

## Entitity Recognition

Entity recognition consists of identifying entities within the records of web content stored in the 
WARC file. In order to perform this task, we must first parse the web content into an appropriate
format. Parsing is performed by implementing the parse_warc method from the class EntityRecognition.
The method consists of using the binary ArchiveIterator object of the module warcio. This 
object can iterate through the records on the gzipped WARC file as long as the file is properly
compressed. In case file is not compressed properly, then it should be recompressed using the warcio
recompress method. 

For each record on the WARC file we perform the following parsing tasks. First, we use BeautifulSoup to 
create an object representing the tree-like structure of HTML documents. Second, we obtain all the text
in which we will search for entities. This task is performed by extracting text from HTML elements that 
do not belong to either 'style', 'script', 'document' or 'head'. Third, the text is encoded and decoded
while ignoring errors to drop all non-ascii characters (e.g. Emojis). Finally, the text extracted from the 
record is stored in an array with its corresponding record id. 

Once the parsing is concluded, we move on to extracting the entities across all records. This task is 
performed in parallel by assigning the entity recognition task on each record to a different thread 
with a maximum of 500 workers. This number was chosen by random, and we stuck with it since it performed well
even on a normal laptop (so on the DAS-4 it should run fine). Entity recognition on each record is performed 
by using spaCy, a free open-source Natural Language Processing tool. We decided to perform entity recognition 
with the statistical model trained by spaCy and use the entities extracted from it in the entity linking process. 
We arrived to this conclusion after noticing that using an approach consisting of tokenizing our text, 
implementing POS tagging and selecting entities based on trivial rules such as POS tag being "NNP" or 
entities consisting of at least three characters wouldn't result in high quality entity recognition. Specifically, 
we noticed that spaCy could perform high quality entity recognition across different record types such as Tweets. 
In addition spaCy has the useful advantage of being completely thread-safe. 

Once the entities are extracted, they are stored into a tab-separated file with their corresponding WARC record ID. 
The file is named intermediate-output.tsv and is the primary input for the next step, entity linking. 


## Entitity Linking
Like other groups, we ran into some issue with this portion of our assignment. We had trouble setting up the Elastic Search and Trident instances. Once we had been supplied with the global Elastic Search instance, usable by all groups, our development went smoother.
The first thing we do is to read the file intermediate-output.tsv into memory. For each entity mention, we then query Elastic Search for candidate entities. Entity mentions with a single match are considered to be immediately correctly matched, and put into a list. Entities with no matches are put into another list (which is ignored in the final version of our submission, but we used it for some rudimentary analysis of our performance). Finally, entity mentions with multiple matches are put into a list.
We then go through all the multiple match entity mentions, and for each one we analyze the candidates. 

The priority decided for the disambiguations have been: the Elastic Search score, the string similarity and then, in case the results of these two steps were below the required standards, a further disambiguation step based on trident was planned (but, due to time constraints, never implemented).

### Elastic Search Score Disambiguation
For every surface form found in the raw file, an elastic search query is performed. Because for a single Freebase ID returned by Elastic Search, many scores can be provided (for the many documents analyzed) the average of these scores is considered. After every query is calculated a dictionary of Freebase_ID : elastic_search_score.

Firstly, it is compared wheater the maximum score value of this dictionary (containing all the candidates entity from Elastic Search) is greater than a threshold or not. This threshold has been tune by empirical observation of the candidates entities resulting from the sample file available. The average Elastic Search score mean was 4.4, the median 4.9 and the standard deviation was 2.1. Based on those results and the entities matched observed, the threshold was set to 4.0. 

### String Similarity Disambiguation
If no entity can reach the threshold, an approach based on string similarity analysis is applied. After some research on different similarity algorithms, the team found that Jaro-Winkler was, in our case study, the best tradeoff for recall/precision score. Once again, due to the fact that Elastic Search might return various string associated with a single Freebase ID, the overall similarity score considered is the average of the single comparisons between the surface form in analysis and all the strings associated with the Freebase entity. The acceptance threshold for string similarity was set to 0.8. The statistical properties of the sample analyzed to tune this parameter are: mean=0.93, median=0.96, stdev=0.1

### Trident Disambiguation
In the case an entity does not meet either threshold, our plan was then to select the top 5-10 candidates (based on the ElasticSearch score) and query Trident based on the respective Freebase IDs and use the label supplied by spaCy (person/location/organization/etc) to select the best candidate. As said before, we, unfortunately, did not have time to do this. Instead, when neither threshold is reached, we optimistically select the candidate with the best ElasticSearch score and determine that to be the entity match.


# Running Instructions:
- Bash Run run.sh <warc-file-name>
