# distsystemsA3

The following assignment covers the pub-sub pattern with the ability to maintain ownership strength for publishers on a topic as well as the ability to maintain a history for each topic. In addition, this project is able to work with multiples broker using ZMQ and Zookeeper, and it is compatible with mininet.

Please use the python environment used in assignment 1 for testing purposes. The files are logically named the same as they were in assignment 2.

To launch the three brokers: python zookeeper.py 127.0.0.1 

To launch a subscriber: python client.py "sports" 127.0.0.1

To launch a subscriber with a history of 8: python client.py "sports" 127.0.0.1 8

To launch a publisher: python server.py "sports" 127.0.0.1

The 2 scenarios described below contain our unit tests for this project.

# Scenario 1
![Scenario1](/ass3testing/scenario1.png)

# Scenario 2
![Scenario2](/ass3testing/scenario2.png)


