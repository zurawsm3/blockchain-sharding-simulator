from merkletools import MerkleTools

class Block:
    def __init__(s, transactions, parent, time, staker, stake):
        s.__transaction_per_block = 500  ### 127 transakcji w bloku. tyle wyszlo z danych. daje mniej bo potem beacon wysyla jeszcze innym
        s.__transactions = transactions
        s.__time = time
        s.__parent = parent
        s.__staker = staker
        s.__stake = stake
        s.__blockchain = []
        s.__mt = MerkleTools(hash_type="md5")
        s.__block_id = 0

    """GETTERY"""
    def get__trans_per_block(s):
        return s.__transaction_per_block

    def get__parent(s):
        return s.__parent

    def get__block_id(s):
        return s.__block_id

    def get__staker(s):
        return s.__staker

    def get__stake(s):
        return s.__stake

    def get__transactions(s):
        return s.__transactions

    def get__time(s):
        return s.__time

    def get__mt(s):
        return s.__mt

    def create_tree(s):
        if s.__transactions is not None:
            for tran in s.__transactions:
                tran_string = f"{tran.trans_id} {tran.sender_id} {tran.receiving_id} {tran.amount}"
                s.__mt.add_leaf(tran_string, True)
        s.__mt.make_tree()
        s.__block_id = hash((s.__mt.get_merkle_root(), s.__time, s.__parent))
