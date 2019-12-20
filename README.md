# Web Data Processing Systems 2019 (VU course XM_40020)
Group: 13 
Felix Farias Fueyo - ffo250 - 2631203

Aleksandar Markovic - amc340 - 2651539

Andrea Rossi - ari720 - 2651310

Svava Bjarnadottir - sbr444 - 2640598

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
for the purpose of querying Trident.

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

We decided to use both the score returned by Elastic Search and string similarity measures to rank the candidate entities. For both, we decided on some threshold. First we rank entities by the ES score, if no candidate reaches the threshold we rank them by string similarities. If neither score reaches the respective threshold, we use Trident.

### Elastic Search Score Disambiguation
For every surface form found in the raw file, an elastic search query is performed. For a single Freebase ID returned by Elastic Search, multiple scores can be returned (for the many documents analyzed), so the average of these scores is used (per candidate). After every query, we construct a dictionary of Freebase_IDs : elastic_search_score.

Firstly, we check whether the maximum score value of this dictionary (containing all the candidates entity from Elastic Search) is greater than the threshold or not. This threshold has been tuned by our empirical observations of the candidates entities resulting from the sample file we used for testing. The mean of the ES scores was 4.4, the median 4.9 and the standard deviation was 2.1. Based on those results and the entities matched observed, the threshold was set to 4.0. 

### String Similarity Disambiguation
If no entity can reach the ES threshold, an approach based on string similarity analysis is applied. After some [research](https://www.cs.cmu.edu/~wcohen/postscript/ijcai-ws-2003.pdf) on different similarity algorithms, we found that Jaro-Winkler was, in our case study, the best tradeoff for recall/precision score. Once again, due to the fact that Elastic Search might return various strings associated with a single Freebase ID, the overall similarity score considered is the average of the single comparisons between the surface form and all the strings associated with the Freebase entity. The acceptance threshold for string similarity was set to 0.8. The statistical properties of the sample analyzed to tune this parameter are: mean=0.93, median=0.96, stdev=0.1

### Trident Disambiguation
In the case an entity does not meet either threshold, we query Trident by matching on Wikipedia article titles, and optimistically return that entity as a match.

### Final output
Finally, the matched entities are written out to stdout, as well as to a file called final-output.tsv in the same folder as the run.sh script is located.

# Running Instructions:
- Bash Run run.sh warc-file-name > output-file-name
