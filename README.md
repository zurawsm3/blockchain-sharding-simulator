# Blockchain Sharding Simulator
Sharding make blockchain more scalable, by divide whole network to smaller parts. Every one of them behave like single chain of blocks. Every core of processor is responsible for one shard. They are working parallel. One of shards is special, it's called Beacon chain, which coordinate rest of shards. Communication beetwen them is implemented in mpi4py python package.

## Install dependencies:
sudo apt-get update -y

sudo apt-get install -y mpich

sudo apt install -y python3-pip

pip3 install wheel

pip3 install mpi4py

pip3 install networkx

pip3 install matplotlib

pip install merkletools

# Overviev:
https://www.mpich.org/about/overview/

https://mpi4py.readthedocs.io/en/stable/overview.html

https://networkx.github.io/

https://matplotlib.org/index.html

https://github.com/Tierion/pymerkletools

## Debug
https://stackoverflow.com/questions/57519129/how-to-run-python-script-with-mpi4py-using-mpiexec-from-within-pycharm

## Przykladowe uruchomienie programu

> mpirun -np 4 python3.6 ./main.py

