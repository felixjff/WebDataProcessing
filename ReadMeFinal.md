Web Data Processing Systems 2019 (VU course XM_40020)
Group: 13 

# Assignment: Large Scale Entity Linking

The assignment consists on developing a program that perfroms entity recognition and entity linking. 
The program should receive in input a gzipped [WARC file](https://en.wikipedia.org/wiki/Web_ARChive),
retrieve entities from records of web content from a variety of sources, generate candidate entities 
from one or multiple knowledge bases and link the entity to the most appropriate candidate. The program 
should return in output a three-column tab-separated file with document IDs, entity surface forms (like
"Berlin"), and Freebase entity IDs (like "/m/03hrz").  


## Set-up

The methods implemented within the program have dependencies. At the moment the program is run we
must ensure these dependencies are available. Therefore, importing, loading and exporting is a part 
of the run.sh program. 

The program is written in Python. All methods and tasks are encapsulated into classes. Methods 
for entity recognition can be found on the EntityRecognition class on the file EntityRecognitionClass.py.
Methods for entity linking can be found on the EntityLinking class on the file EntityLinkingClass.py.
EntityLinking inherits from ElastichSearch class, which graps the methods to request candidate entities 
from FreeBase. The program is put togehter on the file main.py.

## Entitity Recognition

Entity recognition consists of identifying entities within the records of web content stored in the 
WARC file. In order to perform this task, we must first parse the web content into an appropriate
format. Parsing is performed by implementing the parse_warc method from the class EntityRecognition.
The method consists of implementing the binary ArchiveIterator object of the module warcio. This 
object can iterate through the records on the gizzipped WARC file as long as the file is properly
compressed. In case file is not compressed properly, then it should be recompressed using warcio
recompress method. 

For each record on the WARC file we perform the following parsing tasks. First, use BeautifulSoup to 
create an object based that respects the structure of the html code. Second, obtain all the text
in which we will search for entities. This task is performed by extracting text from html elements that 
do not belong to either 'style', 'script', 'document' or 'head'. Third, the text is encoded and decoded
while ignoring errors to drop all strange characters like emojis. Finally, the text extracted from the 
record is stored on an array with it's corresponding record id. 

Once the parsing is concluded, we move on to extracting the entities across all records. This task is 
performed in parallel by assigning the entity recognition task on each record to a different thread
(with a maximum of 500 workers). Entity recognition on each record is performed by using spaCy. 
We decided to perform entity recongnition with the statistical model trained by spaCy and use the 
entities extracted therefrom on the entity linking process. We arrived to this conclusion after noticing 
that using an approach consisting of tokenizing our text, implementing POS tagging and selecting
entities based on trivial rules such as POS tag being "NNP" or entities consisting of at least
three characters wouldn't result in high quality entity recognition. Specially, we noticed that 
spaCy could perform high quality entity recognition across different record types such as Tweets. 
Once the entities are extracted, they are stored into a tab-separated file with their corresponding 
WARC record ID. 
