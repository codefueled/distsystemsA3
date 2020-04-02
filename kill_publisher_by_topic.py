from kazoo.client import KazooClient
import logging

zk = KazooClient(hosts='127.0.0.1:2181')
logging.basicConfig()
zk.start()
topic = input("Enter the Publisher's topic: ")
id = input("Enter the Publisher's ID: ")
print("Deleting that publisher.")
path = "/" + str(topic) + "/" + str(id)
zk.delete(path)