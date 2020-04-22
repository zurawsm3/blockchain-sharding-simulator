from communicator import Communicator
from plot import plot_network
from random import choice, sample
from copy import deepcopy


class Beacon:
    """
    A class represent Beacon chain

    Attributes
    ----------
    communicator : Communicator class instance
        Beacon chain communicates with Shards chain
    __pool_vali : int
        Number of available ids for Validators
    __lower_limit_vali_id : int
        Lower limit of Validators ids
    __pool_notaries : int
        Number of available ids for Notarries
    __lower_limit_notaries_id : int
        Lower limit of Notaries ids
    __nodes_per_beacon : int
        Number of Nodes in Beacon chain
    __vali_per_rank : int
        Number of Validators in Shard chain
    __notaries_per_rank : int
        Number of Notaries in Shard chain
    __beacon_peers : int
        Number of connected nodes to another node
    __nb_val_migrates : int
        Number of rotated Validators
    __nb_notary_migrates : int
        Number of rotated Notaries
    __start_money : int
        Number of tokens had by Node in Shard chain
    __val_acc_info : list
        List of dictionaries. Dictionary of id, money and shard Validators
    __notary_acc_info : list
        List of dictionaries. Dictionary of id, money and shard Notaries
    __peers_in_beacon : dictionary
        Connections of Nodes in Beacon chain

    Methods
    -------
    boot_beacon()
        Create Beacon chain initial infastructure
    create_accounts_info(pool_ids, account_info, ids_per_rank)
        Create initial info about id, money and Shard of Shard nodes
    send_acc_info()
        Sends initial info about Nodes to Shard chains
    choose_rotated_nodes(acc_info, num_migrates, tag)
        Randomly choose nodes which will be move to another Shard chain
    tran_acc_balance(transactions)
        Modify money account status based on transactions made
    resend_transaction(transactions)
        Resend transactions to Shard chains. They will proceed with transactions
    burn_stake_bad_commit_availability(tag)
        Delete Validator's money who made block unavailable
    burn_stake_notarry()
        Delete Notary's money who made the wrong decision
    remove_indebted_nodes(acc_info, lower_limit, pool, tag)
        Get rid of nodes in debt
    """

    def __init__(s):
        s.communicator = Communicator()
        s.__pool_vali = 1000
        s.__lower_limit_vali_id = 2000
        s.__pool_notaries = 10000
        s.__lower_limit_notaries_id = 20000
        s.__nodes_per_beacon = 200
        s.__vali_per_rank = 150
        s.__notaries_per_rank = 20
        s.__beacon_peers = 3
        s.__nb_val_migrates = 1
        s.__nb_notary_migrates = 1
        s.__start_money = 100000
        s.__val_acc_info = []
        s.__notary_acc_info = []
        s.__peers_in_beacon = {}

    @property
    def pool_vali(s):
        return s.__pool_vali

    @property
    def pool_notaries(s):
        return s.__pool_notaries

    @property
    def lower_limit_vali_id(s):
        return s.__lower_limit_vali_id

    @property
    def lower_limit_notaries_id(s):
        return s.__lower_limit_notaries_id

    @property
    def nb_val_migrates(s):
        return s.__nb_val_migrates

    @property
    def nb_notary_migrates(s):
        return s.__nb_notary_migrates

    @property
    def val_acc_info(s):
        return s.__val_acc_info

    @property
    def notary_acc_info(s):
        return s.__notary_acc_info

    @property
    def peers_in_beacon(s):
        return s.__peers_in_beacon

    def boot_beacon(s):
        beacon_node_ids = sample(range(s.__pool_vali, 2 * s.__pool_vali), s.__nodes_per_beacon)
        for node in beacon_node_ids:
            s.__peers_in_beacon[node] = sample((set(beacon_node_ids)-{node}), s.__beacon_peers)
        s.create_accounts_info(s.__pool_vali, s.__val_acc_info, s.__vali_per_rank)
        s.create_accounts_info(s.__pool_notaries, s.__notary_acc_info, s.__notaries_per_rank)

    def create_accounts_info(s, pool_ids, account_info, ids_per_rank):
        for rank in range(1, s.communicator.nbRanks):
            pool = range((rank + 1) * pool_ids, (rank + 2) * pool_ids)
            for id_node in sample(pool, ids_per_rank):
                account = {"id": id_node,
                           "money": s.__start_money,
                           "shard": rank}
                account_info.append(account)

    def send_acc_info(s):
        for rank in range(1, s.communicator.nbRanks):
            s.communicator.comm.send(s.__vali_per_rank, dest=rank, tag=111)
            s.communicator.comm.send(s.__notaries_per_rank, dest=rank, tag=222)
            s.communicator.comm.send([acc["id"] for acc in s.__val_acc_info], dest=rank, tag=1)
            s.communicator.comm.send([acc["id"] for acc in s.__notary_acc_info], dest=rank, tag=2)

    def choose_rotated_nodes(s, acc_info, num_migrates, tag):
        old_rotated_nodes = []
        for rank in range(1, s.communicator.nbRanks):  # without beacon chain
            node_id_pair = [(index, acc['id']) for index, acc in enumerate(acc_info) if acc["shard"] == rank]
            new_rotated_nodes = sample(node_id_pair, num_migrates)
            if old_rotated_nodes:
                for node in old_rotated_nodes:
                    acc_info[node[0]]["shard"] += 1
            old_rotated_nodes = new_rotated_nodes
            if rank == (s.communicator.nbRanks - 1):
                for node in old_rotated_nodes:
                    acc_info[node[0]]["shard"] = 1
            s.communicator.comm.send([node[1] for node in new_rotated_nodes], dest=rank, tag=tag) # one node list

    def tran_acc_balance(s, transactions):
        transactions_removed = deepcopy(transactions)
        for index, shard_trans in enumerate(transactions_removed):
            indexes = []
            for ind, trans in enumerate(shard_trans):
                sacc = next((ind, acc) for ind, acc in enumerate(s.__val_acc_info) if acc["id"] == trans.sender_id)
                racc = next((ind, acc) for ind, acc in enumerate(s.__val_acc_info) if acc["id"] == trans.receiving_id)
                if trans.amount <= sacc[1]["money"]:
                    s.__val_acc_info[sacc[0]]["money"] -= trans.amount
                    s.__val_acc_info[racc[0]]["money"] += trans.amount
                else:
                    indexes.append(ind)
            for i in indexes[::-1]:
                del transactions[index][i]
        return transactions

    def resend_transaction(s, transactions):  # transaction are send to Shard chain to make block from them
        send_transactions = deepcopy(transactions)
        for index, shard_trans in enumerate(transactions):
            for tran in shard_trans:
                receiving_shard = next(
                    acc["shard"] for acc in s.__val_acc_info if acc["id"] == tran.receiving_id)
                if receiving_shard != index + 1:
                    send_transactions[receiving_shard - 1].append(tran)
        for index, shard_trans in enumerate(send_transactions):
            s.communicator.comm.send(shard_trans, dest=index + 1, tag=7)

    def burn_stake_bad_commit_availability(s, tag):
        for rank in range(1, s.communicator.nbRanks):
            acc_burned = s.communicator.comm.recv(source=rank, tag=tag)
            if acc_burned != "None":
                for index, acc in enumerate(s.__val_acc_info):
                    if acc_burned[0] == acc['id']:
                        s.__val_acc_info[index]['money'] -= acc_burned[1]

    def burn_stake_notarry(s):
        for rank in range(1, s.communicator.nbRanks):
            acc_burned = s.communicator.comm.recv(source=rank, tag=9)
            if acc_burned != "None":
                for index, acc in enumerate(s.__notary_acc_info):
                    if acc_burned[0] == acc['id']:
                        s.__notary_acc_info[index]['money'] -= acc_burned[1]

    def remove_indebted_nodes(s, acc_info, lower_limit, pool, tag):
        list_id = [acc['id'] for acc in acc_info]
        change_ids = []
        for index, acc in enumerate(acc_info):
            if acc['money'] < 0:
                interval = range(lower_limit, ((s.communicator.nbRanks + 1) * pool))
                old_id = acc['id']
                new_id = choice(list(set(interval) - {acc['id']} - set(list_id)))
                acc_info[index]['id'] = new_id
                acc_info[index]['money'] = s.__start_money
                change_ids.append((old_id, new_id))
                list_id[index] = new_id
        for i in range(1, s.communicator.nbRanks):
            s.communicator.comm.send(change_ids, dest=i, tag=tag)
