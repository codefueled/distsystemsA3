# Publisher
from __future__ import unicode_literals
import zmq
import time
import sys
from kazoo.client import KazooClient
from kazoo.client import KazooState
import logging
logging.basicConfig()
import random
import string

class Publisher:
    # instantiate variables and connect to broker
    def __init__(self, ip_add, name=""):
        if name == "":
            self.name = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
        else:
            self.name = name
        self.history = ""
        self.kill = True
        self.topic = "Default"
        #self.full_add = "tcp://" + str(ip_add) + ":1234"
        self.context = zmq.Context()
        self.full_add = ""
        self.sock_pub = self.context.socket(zmq.PUB)
        #PRESIDENT ZNODE ADDRESS
        self.home = "/president/pres"

        self.zk_driver = KazooClient(hosts='127.0.0.1:2181')
        self.zk_driver.start()

        data, stat = self.zk_driver.get(self.home)
        ports = data.decode('ASCII').split(":")
        self.full_add = "tcp://" + str(ip_add) + ":" + ports[0]
        self.sock_pub.connect(self.full_add)


    # register a topic for this publisher
    def register_pub(self, topic):
        self.topic = topic
        msg = "REGISTER||" + str(self.topic) + "||" + str(self.name)
        ### CREATE ZNODE
        node_path = '/' + str(self.topic) + '/' + str(self.name)
        self.zk_driver.ensure_path('/' + str(self.topic) + '/')
        if not self.zk_driver.exists(node_path):
            self.zk_driver.create(node_path, b'0')
        time.sleep(1)
        print("Pub ID = ", self.name)
        self.sock_pub.send_string(msg)
        return True

    # publish the given information for pre-registered topic
    def publish(self, info):
        self.history = self.history + str(info) + "..."
        # format for published string is "topic||info"
        msg = str(self.topic) + "||" + self.history + "||" + str(self.name)
        self.sock_pub.send_string(msg)

        @self.zk_driver.DataWatch(self.home)
        def watch_node(data, stat, event):
            if event is not None and event.type == "CREATED" and self.kill:
                # DISCONNECT
                self.sock_pub.close()
                self.context.term()
                self.context = zmq.Context()
                self.sock_pub = self.context.socket(zmq.PUB)

                # RECONNECT WITH NEW PORT
                data, stat = self.zk_driver.get(self.home)
                ports = data.decode('ASCII').split(":")
                self.full_add = "tcp://" + str(ip_add) + ":" + ports[0]
                self.sock_pub.connect(self.full_add)
                self.kill = False
                print("Updated Broker! Input information about your topic and press enter to publish!")
        return True


if __name__ == '__main__':
    # handle input
    if len(sys.argv) != 3:
        print("Please provide 2 arguments as specified in the readme")
    elif "||" in sys.argv[1]:
        print("Please re-run and remove any '||' found in the topic name")
    else:
        # process input arguments
        topic = sys.argv[1]
        ip_add = sys.argv[2]

        # create name
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # create Publisher object
        pub = Publisher(ip_add, name)
        pub.register_pub(topic)

        # wait for inputted information to publish
        while True:
            info = input("Input information about your topic and press enter to publish!\n")
            pub.publish(info)
            print("Success!")