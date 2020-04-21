# Blockchain Sharding Simulator
Sharding make blockchain more scalable, by divide whole network to smaller parts. Every one of them behave like single chain of blocks. Every core of processor is responsible for one shard. They are working parallel. One of shards is special, it's called Beacon chain, which coordinate rest of shards. Communication beetwen them is implemented in mpi4py python package.

## Install dependencies:
sudo apt-get update -y <br />
sudo apt-get install -y mpich <br />
sudo apt install -y python3-pip <br />
pip3 install wheel <br />
pip3 install mpi4py <br />
pip3 install networkx <br />
pip3 install matplotlib <br />
pip3 install merkletools <br />
sudo apt-get -y install python3-tk <br />

# Overview:
https://www.mpich.org/about/overview/ <br />
https://mpi4py.readthedocs.io/en/stable/overview.html <br />
https://networkx.github.io/ <br />
https://matplotlib.org/index.html <br />
https://github.com/Tierion/pymerkletools <br />

## Debug
https://stackoverflow.com/questions/57519129/how-to-run-python-script-with-mpi4py-using-mpiexec-from-within-pycharm

## Przykladowe uruchomienie programu

> mpirun -np 4 python3.6 ./main.py

