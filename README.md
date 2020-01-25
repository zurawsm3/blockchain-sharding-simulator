# Blockchain Sharding Simulator
Sharding make blockchain more scalable, by divide whole network to smaller parts. Every one of them behave like single chain of blocks. Every core of processor is responsible for one shard. They are working parallel. One of shards is special, it's called Beacon chain, which coordinate rest of shards. Communication beetwen them is implemented in mpi4py python package.

## Debug
https://stackoverflow.com/questions/57519129/how-to-run-python-script-with-mpi4py-using-mpiexec-from-within-pycharm

## przykladowe uruchomienie programu

> mpirun -np 4 python3.6 ./main.py

