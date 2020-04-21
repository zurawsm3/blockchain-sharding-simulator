from communicator import Communicator
from copy import deepcopy
from random import choice, sample


class ShardNode:
    def __init__(s, tag1, tag2):  #nodes_per_rank):                   ####### 1-walidatorzy 2-notariusze
        s.communicator = Communicator()
        s._peers_in_shard = {}
        s._nodes_peers = 2
        s._all_ids = s.communicator.comm.recv(source=0, tag=tag1)
        nodes_per_rank = s.communicator.comm.recv(source=0, tag=tag2)
        shard_nodes_ids = []
        for i in range((s.communicator.rank - 1) * nodes_per_rank, s.communicator.rank * nodes_per_rank):
            shard_nodes_ids.append(s._all_ids[i])
        for node in shard_nodes_ids:
            s._peers_in_shard[node] = sample((set(shard_nodes_ids)-{node}), s._nodes_peers)

    """ROTACJA WEZLAMI"""
    def shuffle_nodes(s, rotated_ids):
        # usuwanie perrow poprzez rotowane wezly
        s.main_delete_rotated_ids(rotated_ids)
        peers_in_shard_copy = deepcopy(s._peers_in_shard)
        for peer in peers_in_shard_copy.items():
            indexes = []
            for index, val, in enumerate(peer[1]):
                if val in rotated_ids:
                    indexes.append(index)
            for i in indexes[::-1]:
                del s._peers_in_shard[peer[0]][i]
        s.send_recv_migrants(rotated_ids)

    def main_delete_rotated_ids(s, rotated_ids):
        for rotated_id in rotated_ids:
            del s._peers_in_shard[rotated_id]

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


    """receive ids to change"""
    def change_ids(s, change_ids):  # W SUMIE TO SLABE BO ZAMIENIA WEZLAMI ,ALE TAK NAPRAWDE POWINNO BYC USUWANKO I POTEM DOBIOR WEZLOW TAK JAK NA GORZE ROBILEM, ALE JUZ NIE CHCE MI SIE
        new_val_peers_in_shard = deepcopy(s._peers_in_shard)
        for key, val in new_val_peers_in_shard.items():
            for change in change_ids:
                for index, vali in enumerate(val):
                    if vali == change[0]:
                        s._peers_in_shard[key][index] = change[1]
        for key in new_val_peers_in_shard:
            for change in change_ids:
                if key == change[0]:
                    s._peers_in_shard[change[1]] = s._peers_in_shard[change[0]]
        for change in change_ids:
            if change[0] in s._peers_in_shard.keys():
                s._peers_in_shard.pop(change[0])
        for change in change_ids:
            for index, node in enumerate(s._all_ids):
                if node == change[0]:
                    s._all_ids[index] = change[1]