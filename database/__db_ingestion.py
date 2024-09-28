import csv
from neo4j import GraphDatabase

# Connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test1234"

# CSV file path
CSV_FILE_PATH = "extra/database.csv"

class Neo4jDBHandler:

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def create_dynamic_nodes_and_relationships(self, source_label, source_name, target_label, target_name, rel_type, rel_property, aux_relation, time, place):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_link, source_label, source_name, target_label, target_name, rel_type, rel_property, aux_relation, time, place)

    @staticmethod
    def _create_and_link(tx, source_label, source_name, target_label, target_name, rel_type, rel_property, aux_relation, time, place):
        query = (
            f"""
            MERGE (source:{source_label} {{name: $source_name}})
            MERGE (target:{target_label} {{name: $target_name}})
            MERGE (source)-[rel:{rel_type}]->(target)
            ON CREATE SET 
                rel.since = $rel_property,
                rel.aux_relation = $aux_relation,
                rel.time = $time,
                rel.place = $place
            RETURN source, target, rel
            """
        )
        tx.run(query, source_label=source_label, source_name=source_name,
            target_label=target_label, target_name=target_name,
            rel_type=rel_type, rel_property=rel_property,
            aux_relation=aux_relation, time=time, place=place)



    def load_csv_and_create_relations(self, csv_file_path):
        print('here**********')
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                source_label = row['source_label']
                source_name = row['source']
                # source_age = int(row['source_age']) if row['source_age'] else None
                target_label = row['target_label']
                target_name = row['target']
                # target_age = int(row['target_age']) if row['target_age'] else None
                relationship_type = row['relation_type']
                relationship_property = row['relation']
                aux_relation= row['aux_relation']
                time = row['time']
                place = row['place']

                # Create nodes and relationships dynamically
                self.create_dynamic_nodes_and_relationships(
                    source_label, source_name, target_label, target_name, relationship_type, relationship_property, aux_relation, time, place
                )

    def selectAll(self, input_node_name, input_relationship):
        # Prepare the base query
        base_query = "MATCH (n)-[r]->(m) "
        conditions = []

        # Add conditions based on the presence of query parameters
        if input_node_name:
            conditions.append("n.name = $input_node_name")
        if input_relationship:
            conditions.append("type(r) = $input_relationship")

        # If there are conditions, add them to the query
        if conditions:
            base_query += "WHERE " + " AND ".join(conditions)

        base_query += " RETURN n, r, m"

        # Execute the query with parameters if any
        parameters = {}
        if input_node_name:
            parameters["input_node_name"] = input_node_name
        if input_relationship:
            parameters["input_relationship"] = input_relationship

        # query = """
        #     MATCH (n)-[r]->(m) 
        #     WHERE n.name = $input_node_name AND type(r) = $input_relationship 
        #     RETURN n, r, m
        # """
        persons = self.query(base_query, parameters)
        return persons


# if __name__ == "__main__":
#     # Initialize the Neo4j handler
#     neo4j_handler = Neo4jDBHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

#     try:
#         # Load CSV and create nodes/relationships
#         load_csv_and_create_relations(CSV_FILE_PATH, neo4j_handler)
#     finally:
#         # Close the connection
#         neo4j_handler.close()
