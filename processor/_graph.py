import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from processor._getentitypair import GetEntity


class GraphEnt:
    """docstring for graphEnt."""

    def __init__(self):
        super(GraphEnt, self).__init__()
        self.x = GetEntity()

    def createGraph(self, dataEntities):
        # Convert the DataFrame to a list of values
        entity_list = dataEntities.values.tolist()
        source, relations, target = [], [], []

        # Extract data from the list
        for i in entity_list:
            source.append(i[0])  # First column as source
            relations.append(i[1])  # Second column as relation
            target.append(i[3])  # Fourth column as target

        # Create a DataFrame for the edges
        kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})

        # Create a MultiDiGraph from the DataFrame
        G = nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr="edge", create_using=nx.MultiDiGraph())

        # Set up the plot
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G, k=2)  # Positions for all nodes
        
        # Draw the nodes and edges
        nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_color='lightgray', pos=pos)

        # Draw edge labels (relations)
        edge_labels = nx.get_edge_attributes(G, 'edge')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

        # Show the plot
        plt.title('Graph with Edge Attributes')
        plt.show()

if __name__ == '__main__':
    test = GraphEnt()
    print("Can't Test directly")
