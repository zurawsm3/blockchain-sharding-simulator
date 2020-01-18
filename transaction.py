from random import randrange


class Transaction:
    def __init__(self, sender_id, receiving_id, amount):  #to id_bedzie problem
        self.trans_id = randrange(10**30, 10**31)
        self.sender_id = sender_id
        self.receiving_id = receiving_id
        self.amount = amount
