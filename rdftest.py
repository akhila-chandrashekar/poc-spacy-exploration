import spacy
from rdflib import Graph, URIRef, Namespace

def extract_entities_and_relationships(text):
    nlp = spacy.load("en_core_web_sm")

    # Process the text
    doc = nlp(text)
    entity_pairs = []
    date_entities = []

    for ent in doc.ents:
        # Check for date entities and store them separately
        if ent.label_ == "DATE":
            date_entities.append(ent.text)

    for sent in doc.sents:
        print('Analysing sentence: ', sent)
        subjects = []
        verbs = []
        objects = []
        prepositional_objects = []
        indirect_objects = []
        indirect_subjects = []

        # Identify subjects, verbs, and objects
        for token in sent:
            print(token, token.dep_)
            # Identify subjects (including passive subjects)
            if token.dep_ in ("nsubj", "nsubjpass"):
                for child in token.children:
                    if child.dep_ == "compound":
                        subjects.append(f"{child.text} {token.text}")
                    else:
                        subjects.append(token.text)

            # Identify direct objects and complements
            if token.dep_ in ("dobj", "xcomp"):
                objects.append(token.text)

            # Capture root verbs
            if token.dep_ in ("ROOT", "amod"):
                print(token.lemma_)
                verbs.append(token.text)  # Store root verb
            
            if token.dep_ in ("dative", "iobj", "prep"):
                for child in token.children:
                    if child.dep_ == "pobj":
                        prepositional_objects.append((token.text, child.text))

            if token.dep_ == "agent":
                for child in token.children:
                    if child.dep_ == "pobj":
                        prepositional_objects.append((token.text, child.text))

            if(token.dep_ == "pobj"):
                for child in token.children:
                    if child.dep_ == "det":
                        indirect_objects.append((child.text, token.text))
                   
            # Handling conjunctions for subjects
            if token.dep_ == "conj": 
                if token.head.dep_ in ("nsubj", "nsubjpass"):
                    subjects.append(token.text)
                elif token.head.dep_ in ("dobj", "xcomp"):
                    objects.append(token)

        print('subjects: ', subjects)
        print('verbs: ', verbs)
        print('objects: ', objects)
        print('indirect_objects: ', indirect_objects)
        print('indirect_subjects: ', indirect_subjects)
        print('-------------------------------------------------')
        # Create relationships based on identified subjects and verbs
        for verb in verbs:
            for subject in subjects:
                # Handle relationships with in direct objects
                    # if indirect_objects:
                    #     for prep, iobj in indirect_objects:
                    #         entity_pairs.append((subject, f"{verb}", iobj))

                # Handle relationships with direct objects
                for obj in objects:
                    entity_pairs.append((subject, verb, obj))
                # Handle relationships with prepositional objects
                for prep, pobj in prepositional_objects:
                    entity_pairs.append((subject, f"{verb}_{prep}", pobj))
                
                # for prep, sub in indirect_subjects:
                #     entity_pairs.append((subject, verb, sub))

    # Remove duplicates by converting to a set and back to a list
    entity_pairs = list(set(entity_pairs))       
    return entity_pairs

def load_rdf(rdf_input):
    g = Graph()
    g.parse(rdf_input, format='xml')
    EX = Namespace("http://example.org/")
    
    rdf_entities = {}
    rdf_relationships = []

    for subj, pred, obj in g:
        subject = subj.split("/")[-1].replace("_", " ")  # Get a readable name
        predicate = pred.split("/")[-1]
        object_ = obj.split("/")[-1].replace("_", " ")  # Get a readable name

        rdf_entities[subject] = True
        rdf_entities[object_] = True
        rdf_relationships.append((subject, predicate, object_))

    return rdf_entities, rdf_relationships

def replace_entities(entity_pairs, rdf_entities, rdf_relationships):
    mapped_pairs = []
    print('entity_pairs', entity_pairs)

    for subject, verb, obj in entity_pairs:
        # Replace subjects and objects with RDF entities if they exist
        new_subject = next((r for r in rdf_entities if r.lower() == subject.lower()), subject)
        new_object = next((r for r in rdf_entities if r.lower() == obj.lower()), obj)

        # Check if the verb matches any predicates in RDF
        new_verb = next((rel[1] for rel in rdf_relationships if rel[0].lower() == subject.lower() and rel[2].lower() == obj.lower()), verb)

        mapped_pairs.append((new_subject, new_verb, new_object))

    return mapped_pairs

def main():
    text = "Leonardo DiCaprio was born on November 11, 1974. He can do acting and producing."

    # Load RDF input from a file or string
    rdf_input = "sample.rdf"  # Change this to your RDF file path

    # Load RDF data
    rdf_entities, rdf_relationships = load_rdf(rdf_input)

    # Extract relationships from the text
    entity_pairs = extract_entities_and_relationships(text)

    # Replace entities and relationships with RDF ones
    mapped_pairs = replace_entities(entity_pairs, rdf_entities, rdf_relationships)

    # Debug: Print the mapped entity relationships
    print(f"Mapped entity pairs: {mapped_pairs}")

if __name__ == "__main__":
    main()
