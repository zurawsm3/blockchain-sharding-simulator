from communicator import Communicator
from block import Block
from random import choice, random, sample
from copy import deepcopy
from time import time
from shard import Shard


class Nottaries(Shard):
    def __init__(s):
        s.communicator = Communicator()
        Shard.__init__(s, 2, s.communicator.comm.recv(source=0, tag=222))
        s.__availability_stake = 400

    """DOSTEPNOSC DANYCH"""
    def check_data_availability(s, block_to_checked): # tu bedzie sprawdzana transakcja
        test_block = Block(block_to_checked.get__transactions(), None, time(), None, None)
        test_block.create_tree()
        test_nb_leaves = test_block.get__mt().get_leaf_count()
        number_of_leaves = block_to_checked.get__mt().get_leaf_count()
        staker = choice(list(s._peers_in_shard))
        message = {'notar_staker' : staker}
        message['notar_stake'] = s.__availability_stake
        hostility = random()
        if hostility < 0.5:
            if test_nb_leaves != number_of_leaves:
                message['verdict'] = 'incomplete'
            else:
                message['verdict'] = 'complete'
        else:
            if test_nb_leaves != number_of_leaves:
                message['verdict'] = 'complete'
            else:
                message['verdict'] = 'incomplete'
        return message

    def walidate_challenge(s, message, block_to_checked):
        froud = 'None'
        test_block = Block(block_to_checked.get__transactions(), None, time(), None, None)
        test_block.create_tree()
        test_nb_leaves = test_block.get__mt().get_leaf_count()
        number_of_leaves = block_to_checked.get__mt().get_leaf_count()
        if test_nb_leaves != number_of_leaves:
            if message['verdict'] == 'incomplete':
                s.communicator.comm.send(froud, dest=0, tag=9)
                s.communicator.comm.send([block_to_checked.get__staker(), block_to_checked.get__stake()], dest=0, tag=10)
                return True
            else:
                froud = [message['notar_staker'], message['notar_stake']]
                s.communicator.comm.send(froud, dest=0, tag=9)
                s.communicator.comm.send([block_to_checked.get__staker(), block_to_checked.get__stake()], dest=0, tag=10)
                return True
        else:
            if message['verdict'] == 'complete':
                s.communicator.comm.send(froud, dest=0, tag=9)
                s.communicator.comm.send('None', dest=0, tag=10)
                return False
            else:
                froud = [message['notar_staker'], message['notar_stake']]
                s.communicator.comm.send(froud, dest=0, tag=9)
                s.communicator.comm.send('None', dest=0, tag=10)
                return False
    
    """receive ids to change"""
    def change_notarries_ids(s, change_ids):  # W SUMIE TO SLABE BO ZAMIENIA WEZLAMI ,ALE TAK NAPRAWDE POWINNO BYC USUWANKO I POTEM DOBIOR WEZLOW TAK JAK NA GORZE ROBILEM, ALE JUZ NIE CHCE MI SIE
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

