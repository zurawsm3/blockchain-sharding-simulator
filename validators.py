from communicator import Communicator
from shard import Shard
from transaction import Transaction
from block import Block
from plot import plot_network
from random import choice, random, sample
from copy import deepcopy
from time import time, sleep
import csv


class Validator(Shard):
    def __init__(s):
        s.communicator = Communicator()
        Shard.__init__(s, 1, s.communicator.comm.recv(source=0, tag=111))
        s.__transaction_per_block = 500               ### 127 transakcji w bloku. tyle wyszlo z danych. daje mniej bo potem beacon wysyla jeszcze innym
        s.__tran_max_pay = 100
        s.__max_stake = 400000
        s._shard_blockchain = [Block(None, None, time(), None, None)]   ##tu moze sie zmieni dla publicznych
        # plot_network(s._peers_in_shard, s.communicator.rank)           ### notariusze tego nie maja
    
    """Gettery"""
    def get__vali_peers_in_shard(s):
        return s._peers_in_shard

    def get__all_val_ids(s):
        return s._all_ids

    def get__trans_per_block(s):
        return s.__transaction_per_block

    @property
    def shard_blockchain(s):
        return s._shard_blockchain

    """TRANSAKCJE"""
    def send_trans_to_beacon(s, nodes_in_shard, node_ids):
        shard_transactions = []
        for i in range(s.__transaction_per_block):
            sender = choice(nodes_in_shard)
            receiver = choice(list((set(node_ids) - {sender})))
            amount = choice(range(1, s.__tran_max_pay))
            shard_transactions.append(Transaction(sender, receiver, amount))
        s.communicator.comm.send(shard_transactions, dest=0, tag=6)

    """ZLE UCZYNKI"""
    def crate_ramification(s, nodes_in_shard, blockchain):
        ramification = []
        finally_transactions = s.communicator.comm.recv(source=0, tag=7)  # TE TRANSAKCJE SA DOBRE.
        # print(len(finally_transactions))
        money_in_block = 0
        for tran in finally_transactions:
            money_in_block += tran.amount
        while True:
            staker = choice(nodes_in_shard)
            stake = choice(list(range(money_in_block, s.__max_stake + 1)))
            block = Block(finally_transactions, blockchain[-1].get__block_id(), time(), staker, stake)
            block.create_tree()
            ramification.append(block)
            if random() < 0.4:  # randomowo tworzone sa rozgalezienia, czyli nowe bloki.Dobre, sa zle czasy
                break
        return ramification

    def check_block_time(s, ramification):
        early = min([block.get__time() for block in ramification])
        return next(block for block in ramification if block.get__time() == early)
    
    def approve_block(s, correct_block, nodes_in_shard):
        sleep(1)          # wczesniej bylo 1.5
        hostility = random()
        if hostility < 0.8:
            s._shard_blockchain.append(correct_block)
        else:
            money_in_block = 0
            for tran in correct_block.get__transactions():
                money_in_block += tran.amount
            staker = choice(nodes_in_shard)
            stake = choice(list(range(money_in_block, s.__max_stake + 1)))
            block = Block(correct_block.get__transactions(), hash("whatever"), time(), staker, stake)
            block.create_tree()
            s._shard_blockchain.append(block)

    """AKA RYBAK COS ZROBIC Z 2/3"""
    def walidate_blockchain(s, correct_block): # Sprawdzany jest ostatni, bo i tak co ture sie sprawdza. I JEST ZAWSZE ich dwa. Albo dobry albo zly
        fraud = "None"
        if s._shard_blockchain[-1].get__parent() is not None: # niepotrzebne. zabezpieczenie przed pierwszym blokiem
            if s._shard_blockchain[-1].get__parent() != s._shard_blockchain[-2].get__block_id():
                fraud = [s._shard_blockchain[-1].get__staker(), s._shard_blockchain[-1].get__stake()]
                del s._shard_blockchain[-1]
                s._shard_blockchain.append(correct_block)  # dodawanie poprawnego
        s.communicator.comm.send(fraud, dest=0, tag=8)  # none nie mozna wysylac . dzieki temu bedziemy karac

    def hide_transactions(s): # usuwa czesc transakcji. Dokladnie jedna
        [index] = sample(range(len(s._shard_blockchain[-1].get__transactions())), k=1)
        del s._shard_blockchain[-1].get__transactions()[index]

    def recognized_hider(s, correct_block):
        del s._shard_blockchain[-1]
        s._shard_blockchain.append(correct_block)
        
    """receive ids to change"""
    def change_validators_ids(s, change_ids):  # W SUMIE TO SLABE BO ZAMIENIA WEZLAMI ,ALE TAK NAPRAWDE POWINNO BYC USUWANKO I POTEM DOBIOR WEZLOW TAK JAK NA GORZE ROBILEM, ALE JUZ NIE CHCE MI SIE
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
