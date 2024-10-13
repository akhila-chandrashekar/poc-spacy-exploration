import spacy
import coreferee
import networkx as nx
import matplotlib.pyplot as plt

# Load SpaCy's transformer-based model
nlp = spacy.load('en_core_web_trf')

# Add coreferee to the pipeline for coreference resolution
nlp.add_pipe('coreferee')

# Sample text with pronouns
text = "Alice went to the park. She took her dog with her."

# Process the text through SpaCy's pipeline
doc = nlp(text)

# Step 3: Extract Resolved Entities using Coreference Chains
def extract_resolved_entities(doc):
    resolved_entities = {}
    for chain in doc._.coref_chains:
        if not chain.mentions:
            continue
        # Use the first mention's span text as the antecedent
        print('>>>>>>>>>1>>>>>>>', chain)
        print('>>>>>>>2>>>>>>>>>', chain.mentions)
        # antecedent = chain.mentions[0].mention.text  
        for mention in chain.mentions:
            print('>>>>>>>3>>>>>>>>>', mention.mentions, mention.text)
            resolved_entities[mention.mention.text] = antecedent
    return resolved_entities

# Extract resolved entities from the coreference chains
resolved_entities = extract_resolved_entities(doc)
print("Resolved Entities:", resolved_entities)

# Step 4: Extract Named Entities
entities = [(ent.text, ent.label_) for ent in doc.ents]
print("Named Entities:", entities)

# Step 5: Extract Subject-Verb-Object Relations
def extract_relations(doc):
    relations = []
    for sent in doc.sents:
        subject = ""
        obj = ""
        verb = ""
        for token in sent:
            if token.dep_ == "nsubj":  # Subject of the sentence
                subject = token.text
            elif token.dep_ == "dobj":  # Direct object of the sentence
                obj = token.text
            elif token.pos_ == "VERB":  # Verb (action)
                verb = token.lemma_
        if subject and obj and verb:
            relations.append((subject, verb, obj))
    return relations

# Extract relations from the document
relations = extract_relations(doc)
print("Relations (before resolution):", relations)

# Step 6: Replace Pronouns with Resolved Entities in Relations
resolved_relations = []
for subject, verb, obj in relations:
    resolved_subject = resolved_entities.get(subject, subject)  # Replace subject if pronoun
    resolved_obj = resolved_entities.get(obj, obj)  # Replace object if pronoun
    resolved_relations.append((resolved_subject, verb, resolved_obj))

print("Resolved Relations:", resolved_relations)

# Step 7: Build the Knowledge Graph
def build_knowledge_graph(relations):
    G = nx.DiGraph()

    # Add nodes and edges from the resolved relations
    for subject, verb, obj in relations:
        G.add_edge(subject, obj, relation=verb)
    
    return G

# Create the knowledge graph from the resolved relations
G = build_knowledge_graph(resolved_relations)

# Step 8: Visualize the Knowledge Graph
def visualize_graph(G):
    pos = nx.spring_layout(G)  # Define layout for nodes
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold")
    
    # Display edge labels (relations)
    edge_labels = nx.get_edge_attributes(G, 'relation')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Show the graph plot
    plt.show()

# Visualize the knowledge graph
visualize_graph(G)
