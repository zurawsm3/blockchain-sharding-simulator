from communicator import Communicator
from copy import deepcopy
from random import choice, sample


class Shard:
    def __init__(s, tag, nodes_per_rank):                   ####### 1-walidatorzy 2-notariusze
        s.communicator = Communicator()
        s._peers_in_shard = {}
        s._nodes_peers = 2
        s._all_ids = s.communicator.comm.recv(source=0, tag=tag)
        shard_nodes_ids = []
        ####### s.beacon.get__vali_per_rank()
        for i in range((s.communicator.rank - 1) * nodes_per_rank, s.communicator.rank * nodes_per_rank):
            shard_nodes_ids.append(s._all_ids[i])
        for node in shard_nodes_ids:
            s._peers_in_shard[node] = sample((set(shard_nodes_ids)-{node}), s._nodes_peers)

    """ROTACJA VALIDATORIAMI"""
    def shuffle_nodes(s, migrant_ids):
        # usuwanie perrow poprzez rotowane wezly
        for m in migrant_ids:
            del s._peers_in_shard[m]
        p_o_n = deepcopy(s._peers_in_shard)
        for peer in p_o_n.items():
            indexes = []
            for index, val, in enumerate(peer[1]):
                if val in migrant_ids:
                    indexes.append(index)
            for i in indexes[::-1]:
                del s._peers_in_shard[peer[0]][i]
        s.send_recv_migrants(migrant_ids)

    def send_recv_migrants(s, migrant_ids): # tu nie daje do wszystkich tagow, bo sie to zmienia
        if s.communicator.rank == 1:
            s.communicator.comm.send(migrant_ids, dest=2)
            s.supp_peers(s.communicator.comm.recv(source=s.communicator.nbRanks - 1))
        elif s.communicator.rank == (s.communicator.nbRanks-1):
            s.communicator.comm.send(migrant_ids, dest=1)
            s.supp_peers(s.communicator.comm.recv(source=s.communicator.rank-1))
        else:
            s.communicator.comm.send(migrant_ids, dest=s.communicator.rank+1)
            s.supp_peers(s.communicator.comm.recv(source=s.communicator.rank - 1))

    def supp_peers(s, recv_migrant_id):
        for i in recv_migrant_id:
            s._peers_in_shard[i] = []
        keys = list(s._peers_in_shard.keys())
        for u in keys:
            while len(s._peers_in_shard[u]) < s._nodes_peers:
                s._peers_in_shard[u].append(choice(list(set(keys) - {u} - set(s._peers_in_shard[u]))))
