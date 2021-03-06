from communicator import Communicator
from shard_node import ShardNode
from transaction import Transaction
from block import Block
from plot import plot_network
from random import choice, random, sample
from copy import deepcopy
from time import time, sleep
import csv


class Validator(ShardNode):
    def __init__(s):
        super().__init__(1, 111)
        s.__tran_max_pay = 100
        s.__max_stake = 400000
        s.__shard_blockchain = [Block(None, None, time(), None, None)]
        # plot_network(s.peers_in_shard, s.communicator.rank)

    @property
    def shard_blockchain(s):
        return s.__shard_blockchain

    """TRANSAKCJE"""
    def send_trans_to_beacon(s, nodes_in_shard, node_ids):
        shard_transactions = []
        for i in range(s.__shard_blockchain[0].trans_per_block):
            sender = choice(nodes_in_shard)
            receiver = choice(list((set(node_ids) - {sender})))
            amount = choice(range(1, s.__tran_max_pay))
            shard_transactions.append(Transaction(sender, receiver, amount))
        s.communicator.comm.send(shard_transactions, dest=0, tag=6)

    """ZLE UCZYNKI"""
    def crate_ramification(s, nodes_in_shard, blockchain):
        ramification = []
        finally_transactions = s.communicator.comm.recv(source=0, tag=7)  # these transactions are good
        money_in_block = 0
        for tran in finally_transactions:
            money_in_block += tran.amount
        while True:
            staker = choice(nodes_in_shard)
            stake = choice(list(range(money_in_block, s.__max_stake + 1)))
            block = Block(finally_transactions, blockchain[-1].block_id, time(), staker, stake)
            block.create_tree()
            ramification.append(block)
            if random() < 0.4:
                break
        return ramification

    @staticmethod
    def check_block_time(ramification):
        early = min([block.time for block in ramification])
        return next(block for block in ramification if block.time == early)
    
    def approve_block(s, correct_block, nodes_in_shard):
        sleep(1)
        hostility = random()
        if hostility < 0.8:
            s.__shard_blockchain.append(correct_block)
        else:
            money_in_block = 0
            for tran in correct_block.transactions:
                money_in_block += tran.amount
            staker = choice(nodes_in_shard)
            stake = choice(list(range(money_in_block, s.__max_stake + 1)))
            block = Block(correct_block.transactions, hash("whatever"), time(), staker, stake)
            block.create_tree()
            s.__shard_blockchain.append(block)

    """AKA RYBAK COS ZROBIC Z 2/3"""
    def walidate_blockchain(s, correct_block): # the last one is checked, beacuseevery turn everything changes Its' status is only good or not
        fraud = "None"
        if s.__shard_blockchain[-1].parent is not None: # unnecesary. First block protected
            if s.__shard_blockchain[-1].parent != s.__shard_blockchain[-2].block_id:
                fraud = [s.__shard_blockchain[-1].staker, s.__shard_blockchain[-1].stake]
                del s.__shard_blockchain[-1]
                s.__shard_blockchain.append(correct_block)  # add corect
        s.communicator.comm.send(fraud, dest=0, tag=8)  # we can't send None

    def hide_transactions(s):  # remove part of transactions. One exactly
        [index] = sample(range(len(s.__shard_blockchain[-1].transactions)), k=1)
        del s.__shard_blockchain[-1].transactions[index]

    def recognized_hider(s, correct_block):
        del s.__shard_blockchain[-1]
        s.__shard_blockchain.append(correct_block)
