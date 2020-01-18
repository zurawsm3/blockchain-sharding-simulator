# Blockchain Sharding Simulator
Sharding make blockchain more scalable, by divide whole network to smaller parts. Every one of them behave like normal blockchain. Every core of processor is responsible for one shard. They are working parallel. One of shards is special, it's called Beacon chain, wchich coordinate rest of shards. Communication beetwen them is implemented in mpi4py python package.

## przykladowe uruchomienie programu

> mpirun -np 4 python3.6 ./main.py

