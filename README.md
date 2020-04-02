# distsystemsA3

The following assignment covers the pub-sub pattern with the ability to maintain ownership strength for publishers on a topic as well as the ability to maintain a history for each topic. In addition, this project is able to work with multiples broker using ZMQ and Zookeeper, and it is compatible with mininet.

Please use the python environment used in assignment 1 for testing purposes. The files are logically named the same as they were in assignment 2.

To launch the three brokers: python zookeeper.py 127.0.0.1 

To launch a subscriber: python client.py "sports" 127.0.0.1

To launch a subscriber with a history of 8: python client.py "sports" 127.0.0.1 8

To launch a publisher: python server.py "sports" 127.0.0.1

The 2 scenarios described below contain our 6 unit tests for this project.

# Scenario 1
![Scenario1](/ass3testing/scenario1.png)

In this scenario, there is a broker (top-left), three publishers (in the middle vertical row), and a subscriber (top-right). The publishers are registered with the broker for the same topic (sports) in order from top to bottom, and priority is based upon registration time (earlier registration with broker means higher priority for a topic). First, each publisher attempts to send a message with 'Lakers' in it, but only the topmost publisher's message (Lakers 1) is received by the subscriber since it is the highest priority publisher for sports. Then, that publisher is deleted. Next, each publisher attempts to send a message with 'Spurs' in it, but only the middle publisher's message (Spurs 2) is received by the subscriber since it is the highest priority publisher for sports left. Then, that publisher is deleted. Finally, each publisher attempts to send a message with 'Warriors' in it, but only the bottom-most publisher's message (Warriors 3) is received by the subscriber since it is the last publisher for sports left.

There are 3 tests from this scenario.
- Test 1: Confirms that only highest priority publisher can publish on a topic
- Test 2: Confirms that once the highest priority publisher is deleted, the next highest priority publisher is successfully made the highest priority publisher
- Test 3: Confirms that deleted publishers can no longer publish successfully

Note: This scenario can be conducted with the introduction and exit of subscribers and publishers at different times.

# Scenario 2
![Scenario2](/ass3testing/scenario2.png)

In this scenario, there is a broker (top-left), 2 publishers (in the middle vertical row), and 2 subscribers (in the rightmost vertical row). The publishers are registered from top-to-bottom with the topic of sports, and the subscribers are registered such that the topmost subscriber is asking for a history of 3 messages for the topic of sports while the bottommost subscriber is asking for a history of 5 messages for the topic of sports. The topmost publisher pubslishes 3 messages consecutively (Lakers, Spurs, Warriors). When the first two messages are sent, the topmost subscriber does not recieve any messages since it is demanding a history of length 3. Once the third message is sent, the topmost subscriber receievs a history of length 3 from order of oldest to newest going from left to right. Next, the bottom-most publisher attempts to send a message (Patriots), but this is not passed to any subscriber since the publisher does not have the highest priority. Importantly, when the topmost publisher sends another message (Raptors), Patriots does not appear in the newest history for the topmost subscriber, indicating that non-highest priority messages are not stored in the history for a topic. Also, the history appears to update correctly after each message. At this point, the topmost publisher is deleted and the bottom-most publisher is now the highest-priority publisher. It then sends two messages (Eagles, 49ers), which makes it to both the topmost subscriber and bottommost subscriber (since the history length for the topic sports is finally at least 5 messages long).

There are 3 tests from this scenario.
- Test 4: Confirms that a history is accuractely maintained and updated
- Test 5: Confirms that a history is accurately maintained for a topic rather than for a specific publisher
- Test 6: Confirms that messages published by a low-priority publisher are not stored in the history for that topic

Note: This scenario can be conducted with the introduction and exit of subscribers and publishers at different times.

Finally, all the unit tests specified in in assignment 2 as well as assignment 1 should also work (just substitute zookeeper.py for broker.py in assignment 1).

# Measurements

All raw measurements of this system's performance are available in the excel document measurements.xlsx, and they are summarized and analyzed in Measurements.docx. To replicate our measurements, please comment out the specifcied lines in client.py, zookeeper.py, and server.py

