import spacy
from rdflib import Graph, Namespace

def load_rdf(rdf_input):
    g = Graph()
    g.parse(rdf_input, format='xml')
    EX = Namespace("http://example.org/")
    
    rdf_entities = {}
    name_mapping = {}

    for subj, pred, obj in g:
        subject = subj.split("/")[-1].replace("_", " ")  # Get a readable name
        predicate = pred.split("/")[-1]
        object_ = obj.split("/")[-1].replace("_", " ")  # Get a readable name

        rdf_entities[subject] = True
        
        # Map full name to short name
        if predicate == "shortName":
            name_mapping[obj] = subject  # obj is the short name
        elif predicate == "fullName":
            name_mapping[subject] = obj  # subject is the full name

    return rdf_entities, name_mapping

def replace_entities(entity_pairs, name_mapping):
    mapped_pairs = []

    for subject, verb, obj in entity_pairs:
        # Replace subjects and objects with RDF entities if they exist
        new_subject = name_mapping.get(subject, subject)
        new_object = name_mapping.get(obj, obj)

        mapped_pairs.append((new_subject, verb, new_object))

    return mapped_pairs

def main():
    text = "Leonardo DiCaprio was born on November 11, 1974."

    # Load RDF input from a file or string
    rdf_input = "sample.rdf"  # Change this to your RDF file path

    # Load RDF data
    rdf_entities, name_mapping = load_rdf(rdf_input)

    # Extract relationships from the text (placeholder)
    entity_pairs = [("Leonardo DiCaprio", "was born", "November 11, 1974")]

    # Replace entities with mapped names
    mapped_pairs = replace_entities(entity_pairs, name_mapping)

    # Debug: Print the mapped entity relationships
    print(f"Mapped entity pairs: {mapped_pairs}")

if __name__ == "__main__":
    main()
