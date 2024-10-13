from rdflib import Graph, Namespace, Literal

def load_rdf(rdf_input):
    g = Graph()
    g.parse(rdf_input, format='xml')
    EX = Namespace("http://example.org/")
    
    cities = []
    for subj in g.subjects():
        name = str(subj).split("/")[-1].replace("_", " ")
        population = g.value(subj, EX.population)
        
        # Convert population from Literal to int
        if isinstance(population, Literal):
            population = int(population)  # Convert Literal to int

        is_capital = g.value(subj, EX.isCapital)
        
        cities.append({
            'name': name,
            'population': population,
            'is_capital': is_capital
        })

    return cities

def evaluate_rules(cities, rule):
    matched_cities = []
    
    for city in cities:
        # Ensure population is compared correctly
        if city['population'] > 1000000:  # Condition from the rule
            matched_cities.append(city['name'])
            print(rule['actions'][0]['message'].format(city_name=city['name']))

    return matched_cities

def main():
    rdf_input = "sample2.rdf"  # Path to your RDF file
    cities = load_rdf(rdf_input)

    rule = {
        "name": "Identify Major Cities",
        "conditions": {
            "type": "City",
            "population": "> 1000000"
        },
        "actions": [
            {
                "type": "notify",
                "message": "Major city identified: {city_name}"
            }
        ]
    }

    evaluate_rules(cities, rule)

if __name__ == "__main__":
    main()
