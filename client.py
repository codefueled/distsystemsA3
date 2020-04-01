# Subscriber
from __future__ import unicode_literals
from kazoo.client import KazooClient
import zmq
import sys
import threading
import time
import logging
logging.basicConfig()

class Subscriber:

    # instantiate variables and connect to broker
    def __init__(self, ip_add, port_num, timeout=-1):
        self.count = 0
        self.full_add = "tcp://" + str(ip_add)
        self.port = port_num
        self.context = zmq.Context()
        self.sock_sub = self.context.socket(zmq.SUB)
        self.sock_sub.RCVTIMEO = timeout

        # PRESIDENT ZNODE ADDRESS
        self.home = "/president/pres"

        self.zk_driver = KazooClient(hosts='127.0.0.1:2181')
        self.zk_driver.start()

        #GET HISTORY IF NEW SUBSCRIBER
        if self.port:
            self.history_home = "/history/"
            self.history_znode = "/history/his"
            if not self.zk_driver.exists(self.history_znode):
                self.zk_driver.ensure_path(self.history_home)
                self.zk_driver.create(self.history_znode, ephemeral=True)
            self.zk_driver.set(self.history_znode, ip_add + ":" + self.port)
            self.full_add = "tcp://" + str(ip_add) + ":" + str(self.port)
            self.sock_sub.connect(self.full_add)
        else:
            # WAIT FOR ZOOKEEPER TO BE READY
            @self.zk_driver.DataWatch(self.home)
            def watch_node(data, stat, event):
                if event is None:
                    data, stat = self.zk_driver.get(self.home)
                    ports = data.decode('ASCII').split(":")
                    self.full_add = "tcp://" + str(ip_add) + ":" + ports[1]
                    self.sock_sub.connect(self.full_add)
                else:
                    print("Zookeeper is not ready yet, try again later")


    def register_sub(self, topics):
        topic_list = topics.split(",")
        topic_list = [topic.strip() for topic in topics.split(',')]
        for topic in topic_list:
            #subscribe to topic
            self.sock_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

    def notify(self, stop=None):
        if stop:
            while (not stop.is_set()):
                @self.zk_driver.DataWatch(self.home)
                def watch_node(data, stat, event):
                    if event is not None and event.type == "CHANGED":
                        # DISCONNECT
                        self.sock_sub.close()
                        self.context.term()
                        time.sleep(2)
                        self.context = zmq.Context()
                        self.sock_sub = self.context.socket(zmq.SUB)

                        # RECONNECT WITH NEW PORT
                        data, stat = self.zk_driver.get(self.home)
                        ports = data.decode('ASCII').split(":")
                        self.full_add = "tcp://" + str(ip_add) + ":" + ports[1]
                        self.sock_sub.connect(self.full_add)

                message = self.sock_sub.recv_string()
                topic, info = message.split("||")
                print("Topic: %s. Message: %s" % (topic, info))
                # print("Time received: %.20f" % time.time())  # uncomment for measurements.py purposes
                self.count = self.count + 1
        else:
            while True:
                @self.zk_driver.DataWatch(self.home)
                def watch_node(data, stat, event):
                    if event is not None and event.type == "CHANGED":
                        # DISCONNECT
                        self.sock_sub.close()
                        self.context.term()
                        time.sleep(2)
                        self.context = zmq.Context()
                        self.sock_sub = self.context.socket(zmq.SUB)

                        # RECONNECT WITH NEW PORT
                        data, stat = self.zk_driver.get(self.home)
                        ports = data.decode('ASCII').split(":")
                        self.full_add = "tcp://" + str(ip_add) + ":" + ports[1]
                        self.sock_sub.connect(self.full_add)

                message = self.sock_sub.recv_string()
                topic, info = message.split("||")
                print("Topic: %s. Message: %s" % (topic, info))
                self.count = self.count + 1

if __name__ == '__main__':
    # handle input
    if len(sys.argv) < 3:
        print("Please provide 2 arguments as specified in the readme")
    else:
        # parse input
        topics = str(sys.argv[1])
        ip_add = sys.argv[2]
        port = sys.argv[3] if len(sys.agrv) > 3 else ""
        sub = Subscriber(ip_add, port)
        sub.register_sub(topics)

        try:
            sub.notify()
        except zmq.error.Again:
            print("Subscriber Timed-out")