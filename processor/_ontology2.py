import spacy
from neo4j import GraphDatabase

def extract_entities_and_relationships(text):
    nlp = spacy.load("en_core_web_sm")

     # Add custom entities from ontology
    # ruler = nlp.add_pipe("entity_ruler", before="ner")
    # patterns = []
    # for entity_type, terms in ontology.items():
    #     for term in terms:
    #         patterns.append({"label": entity_type, "pattern": term})
    # ruler.add_patterns(patterns)

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

def store_in_neo4j(entity_pairs, neo4j_uri, neo4j_user, neo4j_password):
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        for entity1, relation, entity2 in entity_pairs:
            session.run("MERGE (a:Entity {name: $entity1})", entity1=entity1)
            session.run("MERGE (b:Entity {name: $entity2})", entity2=entity2)
            
            # Construct the query for relationships
            query = (
                f"MATCH (a:Entity {{name: $entity1}}), (b:Entity {{name: $entity2}}) "
                f"MERGE (a)-[:{relation.capitalize()}]->(b)"
            )
            
            # Run the constructed query
            session.run(query, entity1=entity1, entity2=entity2)

    driver.close()

def main():

    text = "Leonardo DiCaprio was born on November 11, 1974. He can do acting and producing. He has acted in biopics.\
     His films have earned US$7.2 billion. He has won an Academy Award and three Golden Globe Awards. \
     He was born in Los Angeles." 
    # Manchester City Football Club is based in Manchester. It competes in the Premier League. It was known as Ardwick Association Football Club. Manchester City Football Club is referred as The Centurions and The Fourmidables. Its home ground is located in east Manchester. Its home ground is also known as CityofManchesterStadium."

    # Neo4j connection details
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    # Extract relationships
    entity_pairs = extract_entities_and_relationships(text)

    # Debug: Print the extracted entity relationships
    print(f"Extracted entity pairs: {entity_pairs}")

    # Store in Neo4j
    # store_in_neo4j(entity_pairs, neo4j_uri, neo4j_user, neo4j_password)

if __name__ == "__main__":
    main()
