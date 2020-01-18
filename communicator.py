from mpi4py import MPI


class Communicator:
    def __init__(self):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.nbRanks = self.comm.Get_size()
