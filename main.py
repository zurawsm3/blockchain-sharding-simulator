from beacon import Beacon
from validators import Validator
from notarries import Nottaries
from communicator import Communicator
from plot import plot_network


class Main:
    def __init__(s):
        s.__sim_time = 10

    def get__sim_time(s):
        return s.__sim_time


if __name__ == "__main__":
    main = Main()
    communicator = Communicator()
    # import pydevd
    # port_mapping = [43777, 42797, 40239, 43883]
    # pydevd.settrace('localhost', port=port_mapping[communicator.rank], stdoutToServer=True, stderrToServer=True)

    if communicator.comm.rank == 0:
        beacon = Beacon()
        beacon.boot_beacon()
        beacon.send_acc_info()
    communicator.comm.barrier()
    if communicator.comm.rank != 0:
        validators = Validator()
        notarries = Nottaries()
    if communicator.rank == 1:  # one rank works as timer. First one, beacouse 0-th is more busy. Needed for examination
        time_list = [0]
        transactions_nb = [0]
        gg = True
    for tick in range(main.get__sim_time()):
        if communicator.rank == 0:
            if tick % 10 == 0:
                beacon.choose_rotated_nodes(beacon.notary_acc_info, beacon.nb_notary_migrates, 3)
            if tick % 25 == 0:
                beacon.choose_rotated_nodes(beacon.val_acc_info, beacon.nb_val_migrates, 4)
        communicator.comm.barrier()
        if communicator.rank != 0:
            if tick % 10 == 0:
                l = communicator.comm.recv(source=0, tag=3)
                notarries.shuffle_nodes(l)
            if tick % 25 == 0:
                validators.shuffle_nodes(communicator.comm.recv(source=0, tag=4))
            validators.send_trans_to_beacon(list(validators.peers_in_shard), validators.all_ids)
        communicator.comm.barrier()
        if communicator.rank == 0:
            trans_received = []
            for rank in range(1, communicator.nbRanks):
                trans_received.append(communicator.comm.recv(source=rank, tag=6))
            trans_after_del = beacon.tran_acc_balance(trans_received)
            beacon.resend_transaction(trans_after_del)
        communicator.comm.barrier()
        if communicator.rank != 0:
            ramificat = validators.crate_ramification(validators.all_ids, validators.shard_blockchain)
            correct_block = validators.check_block_time(ramificat)
            validators.approve_block(correct_block, validators.all_ids)
            validators.walidate_blockchain(correct_block)
            validators.hide_transactions()
            message = notarries.check_data_availability(validators.shard_blockchain[-1])
            verdict = notarries.walidate_challenge(message, validators.shard_blockchain[-1])
            if verdict:
                validators.recognized_hider(correct_block)
        communicator.comm.barrier()
        if communicator.rank == 0:
            beacon.burn_stake_bad_commit_availability(8)
            beacon.burn_stake_notarry()
            beacon.burn_stake_bad_commit_availability(10)
            beacon.remove_indebted_nodes(beacon.val_acc_info, beacon.lower_limit_vali_id, beacon.pool_vali, 11)
            beacon.remove_indebted_nodes(beacon.notary_acc_info, beacon.lower_limit_notaries_id, beacon.pool_notaries, 12)
        communicator.comm.barrier()
        if communicator.rank != 0:
            validators.change_ids(communicator.comm.recv(source=0, tag=11))
            notarries.change_ids(communicator.comm.recv(source=0, tag=12))
    if communicator.rank == 0:
        pass
        plot_network(beacon.peers_in_beacon, communicator.rank)
    else:
        plot_network(validators.peers_in_shard, communicator.rank)
