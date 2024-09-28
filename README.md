# SpaCy Exploration - POC Stage


## To run the code

Simply run in terminal:

`pip3 install -r requirements.txt`

`spacy download en_core_web_sm` or 
`spacy download en_core_web_md` or
`spacy download en_core_web_lg`

To use the web interface:
`python3 _app.py` and use <http://0.0.0.0:20550/> as the URL in your browser

To visualize the knowledge graph of input file, use the following flag to run init.py

`python3 _init.py -i data.txt -g yes`


## File Description ##

### init.py ###

(Used for command line interface)
To obtain the data from the user, view graphs and solve queries through the command line interface.


### app.py ###

(Used for web interface)
This is for the web interface

### complex.py ###

It does the task of extracting the dependencies such as given below from input text as well as the question with the help of spaCy:
1. Subject
2. Object
3. Time
4. Place
5. Relation between Subject and Object
6. Auxiliary relations (if any)

The dependencies from sentences are extracted using: 
1. **normal_sent(sentence)**
2. **get_time_place_from_sent(sentence)**


The dependencies from questions are extracted using:
1. **question_pairs(question)**
2. **get_time_place_from_sent(sentence)**

### exportPairs.py ###

Entity pairs extracted as pandas dataframe object in the format of (“source”,”relation”,”aux_relation”,”target”,”time”,”place”) are sent to the JSON file using the dumpdata(pairs) function. This JSON file will then be used to extract the answers using entity matching.

### getentitypair.py ###

It performs two tasks:
1. Preprocessing of the text file **preprocess_text(input_file) function)**
Using **resolvedep.py**:
This is to keep a uniformity in the text information. It involves resolution of problems such as that of uppercase and lowercase in the data.
It also involves conversion of complex sentences into simple sentences. For eg: Assigning proper nouns to the pronouns used.

2. Extraction of entity pairs**get_entity(text) function**
This involves conversion of extracted entity pairs into the dataframe which can be dumped in the JSON file. The format is 
(“source”,”relation”,”aux_relation”,”target”,”time”,”place”)

### database.json ###
The extracted entity pairs are stored in database.json file

### database.csv ###
The extracted entity pairs are stored in database.csv file


### graph.py ###
It creates the graph of the information extracted using NetworkX.The source and destination are used as nodes whereas relations are used as the edges.

