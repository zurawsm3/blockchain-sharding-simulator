from communicator import Communicator
from block import Block
from random import choice, random, sample
from copy import deepcopy
from time import time
from shard_node import ShardNode


class Nottaries(ShardNode):
    def __init__(s):
        super().__init__(2, 222)
        s.__availability_stake = 400

    """DOSTEPNOSC DANYCH"""
    def check_data_availability(s, block_to_checked): # tu bedzie sprawdzana transakcja
        test_block = Block(block_to_checked.get__transactions(), None, time(), None, None)
        test_block.create_tree()
        test_nb_leaves = test_block.get__mt().get_leaf_count()
        number_of_leaves = block_to_checked.get__mt().get_leaf_count()
        staker = choice(list(s._peers_in_shard))
        message = {'notar_staker': staker,
                   'notar_stake': s.__availability_stake}
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
