import spacy
import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase

class OntologyGraph:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.nlp = spacy.load("en_core_web_sm")
        self.ruler = self.nlp.add_pipe("entity_ruler")
    
    def close(self):
        self.driver.close()
        print('DB connection closed')

    def add_patterns(self, ontology):
        patterns = [{"label": concept, "pattern": term} for concept, terms in ontology.items() for term in terms]
        self.ruler.add_patterns(patterns)

    def print_dependency_tree(self, doc):
        for sent in doc.sents:
            print(f"\nDependency Tree for: '{sent.text}'")
            for token in sent:
                print(f"{token.text:10} -> {token.dep_:10} | Head: {token.head.text}")

    def extract_entities_and_relationships(self, text):
        doc = self.nlp(text)
        print("Recognized entities:")
        for ent in doc.ents:
            print(f"{ent.text} ({ent.label_})")
        
        entity_pairs = []
        for sent in doc.sents:
            print(f"\nAnalyzing sentence: {sent.text}")
            for token in sent:
                if token.dep_ == "ROOT":
                    print(f"Found verb: {token.text}")
                    subjects = [w for w in token.children if w.dep_ in ("nsubj", "nsubjpass")]
                    direct_objects = [w for w in token.children if w.dep_ in ("dobj", "xcomp")]
                    prepositional_entities = {w: pobj for w in token.children if w.dep_ == "prep" for pobj in w.children if pobj.dep_ == "pobj"}
                    
                    for subject in subjects:
                        related_entities = {subject.text}
                        related_entities.update(obj.text for obj in direct_objects)
                        related_entities.update(pobj.text for pobj in prepositional_entities.values())

                        for related in related_entities:
                            if related != subject.text:
                                entity_pairs.append((subject.text, token.lemma_, related))
        
        print("\nEntity pairs identified:")
        for pair in entity_pairs:
            print(pair)
        
        return entity_pairs

    def store_in_neo4j(self, entity_pairs):
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    for entity1, rel, entity2 in entity_pairs:
                        print(f"Storing entities: {entity1}, {entity2} with relationship {rel}")
                        tx.run("MERGE (a:Entity {name: $entity1})", entity1=entity1)
                        tx.run("MERGE (b:Entity {name: $entity2})", entity2=entity2)
                        tx.run(
                            f"MATCH (a:Entity {{name: $entity1}}), (b:Entity {{name: $entity2}}) "
                            f"MERGE (a)-[:{rel.capitalize()}]->(b)",
                            entity1=entity1,
                            entity2=entity2
                        )
                        print(f"Successfully stored: {entity1} -[{rel}]-> {entity2}")
        except Exception as e:
            print(f"Error while connecting to Neo4j: {e}")

    def draw_graph(self, entity_pairs):
        G = nx.DiGraph()
        for entity1, rel, entity2 in entity_pairs:
            G.add_node(entity1, type='Entity')
            G.add_node(entity2, type='Entity')
            G.add_edge(entity1, entity2, label=rel)
        
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_color='black', font_weight='bold')
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title("Entity Relationship Graph")
        plt.show()


# Example usage
if __name__ == "__main__":
    ontology = {
        "Disease": ["diabetes", "cancer", "hypertension", "heart disease"],
        "Medication": ["insulin", "metformin", "aspirin", "lisinopril"],
        "Symptom": ["headache", "fever", "nausea", "fatigue"]
    }

    text = "The patient was diagnosed with diabetes and prescribed insulin. " \
           "He also reported experiencing fatigue and headache."

    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    ontology_graph = OntologyGraph(neo4j_uri, neo4j_user, neo4j_password)
    ontology_graph.add_patterns(ontology)

    entity_pairs = ontology_graph.extract_entities_and_relationships(text)
    
    if entity_pairs:
        ontology_graph.store_in_neo4j(entity_pairs)
        ontology_graph.draw_graph(entity_pairs)
        ontology_graph.close()
    else:
        print("No entity pairs found.")

    ontology_graph.close()
