import networkx as nx
import matplotlib.pyplot as plt
import warnings
from communicator import Communicator
# import tkinter


def plot_network(peers_shard, rank):
    comm = Communicator()
    g = nx.Graph()
    plt.figure(figsize=(15, 15))
    # plt.axis('off')
    fig = plt.gcf()
    if rank == 0:
        fig.canvas.set_window_title("Łańcuch sygnalizacyjny")
    # elif rank == (comm.nbRanks-1):
    #     fig.canvas.set_window_title("Notariusze")
    else:
        fig.canvas.set_window_title(f"shard {rank}")
    node_ids = list(peers_shard)
    g.add_nodes_from(node_ids)
    g.add_edges_from([[k, i] for k, v in peers_shard.items() for i in v])

    pos = nx.kamada_kawai_layout(g)
    warnings.filterwarnings("ignore")
    nx.draw(g, pos, with_labels=True, node_size=1200, node_color='y')
    warnings.resetwarnings()
    plt.show()
