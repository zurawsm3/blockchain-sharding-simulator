from mpi4py import MPI


class Communicator:
    """
    Reprents mpi4py Message Passing Interface

    Attributes
    ----------
    comm : MPI communicator
        predefined intracommunicator instance
    rank : int
        show actual rank of process
    nbRanks : int
        number of processes
    """

    def __init__(self):
        """
        Parameters
        ----------
        comm : MPI communicator
            predefined intracommunicator instance
        rank : int
            show actual rank of process
        nbRanks : int
            number of processes
        """

        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.nbRanks = self.comm.Get_size()
