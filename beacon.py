from communicator import Communicator
from plot import plot_network
from random import choice, sample
from copy import deepcopy


class Beacon:
    def __init__(s):
        s.communicator = Communicator()
        s.__interval_no_nottaries = 1000
        s.__interval_notarries = 10000
        s.__nodes_per_beacon = 200
        s.__vali_per_rank = 150         ###w eth mowia ze 150 wezlow wystarczy
        s.__notarry_per_rank = 20
        s.__beacon_peers = 3
        s.__nb_val_migrates = 1
        s.__nb_notarry_migrates = 1
        s.__start_money = 100000
        s.__val_acc_info = []
        s.__notarry_acc_info = []
        s.__peers_in_beacon = {}

    def get__peers_in_beacon(s):
        return s.__peers_in_beacon

    def boot_beacon(s):
        beacon_node_ids = sample(range(s.__interval_no_nottaries, 2 * s.__interval_no_nottaries), s.__nodes_per_beacon)
        for node in beacon_node_ids:
            s.__peers_in_beacon[node] = sample((set(beacon_node_ids)-{node}), s.__beacon_peers)
        s.create_val_account_info()
        s.create_notarry_account_info()
        for rank in range(1, s.communicator.nbRanks):
            s.communicator.comm.send(s.__vali_per_rank, dest=rank, tag=111)
            s.communicator.comm.send(s.__notarry_per_rank, dest=rank, tag=222)
            s.communicator.comm.send([i["id"] for i in s.__val_acc_info], dest=rank, tag=1)
            s.communicator.comm.send([i["id"] for i in s.__notarry_acc_info], dest=rank, tag=2)

        # plot_network(s.__peers_in_beacon, s.communicator.rank)


    def create_val_account_info(s):
        for rank in range(1, s.communicator.nbRanks):
            interval = range((rank+1)*s.__interval_no_nottaries, (rank+2)*s.__interval_no_nottaries)
            for id_node in sample(interval, s.__vali_per_rank):
                account = {"id": id_node,
                           "money": s.__start_money,
                           "shard": rank}
                s.__val_acc_info.append(account)

    def create_notarry_account_info(s):
        for rank in range(1, s.communicator.nbRanks):
            interval = range((rank+1)*s.__interval_notarries, (rank+2)*s.__interval_notarries)
            for id_node in sample(interval, s.__notarry_per_rank):
                account = {"id": id_node,
                           "money": s.__start_money,
                           "shard": rank}
                s.__notarry_acc_info.append(account)

    "ROTACJA WEZLAMI"
    def choose_rotated_notarries(s):
        old_rotated_nodes = []
        for rank in range(1, s.communicator.nbRanks): # bez beacon chaina
            new_rotated_nodes = sample([(index, acc['id']) for index, acc in enumerate(s.__notarry_acc_info) if acc["shard"] == rank], s.__nb_notarry_migrates)
            if old_rotated_nodes:
                for node in old_rotated_nodes:
                    s.__notarry_acc_info[node[0]]["shard"] += 1
            old_rotated_nodes = new_rotated_nodes
            if rank == (s.communicator.nbRanks - 1):
                for node in old_rotated_nodes:
                    s.__notarry_acc_info[node[0]]["shard"] = 1
            s.communicator.comm.send([node[1] for node in new_rotated_nodes], dest=rank, tag=3) # wyjdzie jedna lista nodow

    def choose_rotated_validators(s):
        old_rotated_nodes = []
        for rank in range(1, s.communicator.nbRanks): # bez beacon chaina
            new_rotated_nodes = sample([(index, acc['id']) for index, acc in enumerate(s.__val_acc_info) if acc["shard"] == rank], s.__nb_val_migrates)
            if old_rotated_nodes:
                for node in old_rotated_nodes:
                    s.__val_acc_info[node[0]]["shard"] += 1
            old_rotated_nodes = new_rotated_nodes
            if rank == (s.communicator.nbRanks - 1):
                for node in old_rotated_nodes:
                    s.__val_acc_info[node[0]]["shard"] = 1
            s.communicator.comm.send([node[1] for node in new_rotated_nodes], dest=rank, tag=4) # wyjdzie jedna lista nodow

    """TRANSAKCJE"""
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

    def resend_transaction(s, transactions):  # wysylane sa transakcje do shardow, by mogly stworzyc z nich bloki
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
                for index, acc in enumerate(s.__notarry_acc_info):
                    if acc_burned[0] == acc['id']:
                        s.__notarry_acc_info[index]['money'] -= acc_burned[1]


    """USUWAC WEZLY KTORE SA NA MINUSIE i wybierac nowe"""
    def remove_indebted_validators(s):
        list_id = [acc['id'] for acc in s.__val_acc_info]
        change_ids = []
        for index, acc in enumerate(s.__val_acc_info):
            if acc['money'] < 0:
                interval = range(2000, ((s.communicator.nbRanks + 1) * s.__interval_no_nottaries))
                old_id = acc['id']
                new_id = choice(list(set(interval) - {acc['id']} - set(list_id)))
                s.__val_acc_info[index]['id'] = new_id
                s.__val_acc_info[index]['money'] = s.__start_money
                change_ids.append((old_id, new_id))
                list_id[index] = new_id
        for i in range(1, s.communicator.nbRanks):
            s.communicator.comm.send(change_ids, dest=i, tag=11)

    def remove_indebted_notarries(s):
        list_id = [acc['id'] for acc in s.__notarry_acc_info]
        change_ids = []
        for index, acc in enumerate(s.__notarry_acc_info):
            if acc['money'] < 0:
                interval = range(20000, ((s.communicator.nbRanks + 1) * s.__interval_notarries))
                old_id = acc['id']
                new_id = choice(list(set(interval) - {acc['id']} - set(list_id)))
                s.__notarry_acc_info[index]['id'] = new_id
                s.__notarry_acc_info[index]['money'] = s.__start_money
                change_ids.append((old_id, new_id))
                list_id[index] = new_id
        for i in range(1, s.communicator.nbRanks):
            s.communicator.comm.send(change_ids, dest=i, tag=12)





























        #
        #
        #
        #
        #
        #
        #
        # #Dodaje wszystkim po 20 poniewaz beda palone stawki przy tworzeniu zlych BLOKÓW i nie chce zeby ludzie sie wykosztowali
        # for account in s.val_accounts_info:
        #     account["money"] += s.config.added_paid_every_tick

