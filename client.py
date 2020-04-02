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
    def __init__(self, ip_add, timeout=-1, history=1):
        self.history = int(history)
        self.kill = True
        self.count = 0
        self.full_add = "tcp://" + str(ip_add)
        self.context = zmq.Context()
        self.sock_sub = self.context.socket(zmq.SUB)
        self.sock_sub.RCVTIMEO = timeout

        # PRESIDENT ZNODE ADDRESS
        self.home = "/president/pres"

        self.zk_driver = KazooClient(hosts='127.0.0.1:2181')
        self.zk_driver.start()

        data, stat = self.zk_driver.get(self.home)
        ports = data.decode('ASCII').split(":")
        self.full_add = "tcp://" + str(ip_add) + ":" + ports[1]
        self.sock_sub.connect(self.full_add)

    def register_sub(self, topics):
        topic_list = topics.split(",")
        topic_list = [topic.strip() for topic in topics.split(',')]
        for topic in topic_list:
            #subscribe to topic
            self.sock_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

    def notify(self, stop=None):
        if stop:
            while (not stop.is_set()):
                # only used for measurements.py
                message = self.sock_sub.recv_string()
                topic, info, id = message.split("||")
                # print("Time received: %.20f" % time.time())  # uncomment for measurements.py purposes
                msgs = info.split("...")
                if len(msgs) < self.history:
                    info = "The publisher's history size is less than the requested history size, so no messages will be played."
                else:
                    msgs = msgs[len(msgs) - self.history:len(msgs)]
                    info = ",".join(msgs)
                print("Topic: %s. Message: %s" % (topic, info))
                self.count = self.count + 1
        else:
            while True:
                @self.zk_driver.DataWatch(self.home)
                def watch_node(data, stat, event):
                    if event is not None and event.type == "CREATED" and self.kill:
                        self.kill = False
                        print("Updated Broker!")
                message = self.sock_sub.recv_string()
                topic, info, id= message.split("||")
                msgs = info.split("...")
                #print("Time received: %.20f" % time.time())  # uncomment for measurements purposes
                if len(msgs) < self.history:
                    info = "The topics' history size is less than the requested history size, so no messages will be played."
                else:
                    msgs = msgs[len(msgs) - self.history:len(msgs)]
                    info = ",".join(msgs)
                print("Topic: %s. Message(s): %s" % (topic, info))
                self.count = self.count + 1

if __name__ == '__main__':
    # handle input
    if len(sys.argv) < 3:
        print("Please provide 2 arguments as specified in the readme")
    else:
        # parse input
        topics = str(sys.argv[1])
        ip_add = sys.argv[2]
        history = 1
        if len(sys.argv) > 3:
            history = int(sys.argv[3])

        sub = Subscriber(ip_add, -1, history)
        sub.register_sub(topics)

        try:
            sub.notify()
        except zmq.error.Again:
            print("Subscriber Timed-out")