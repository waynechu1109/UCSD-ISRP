#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class MyNode(Node):

    def __init__(self):                  # this is constructor 

        super().__init__("first_node")   # node name, super() give access to 
                                         # methods and properties of a parent or sibling class.
        #self.get_logger().info("ROS")
        self.counter_ = 0
        self.create_timer(1.0, self.timer_callback)  # create a timer callback every 1 sec

    def timer_callback(self):
        self.get_logger().info("Hello" + str(self.counter_))
        self.counter_ += 1                                 


def main(args=None):
    rclpy.init(args=args) # initialize rclpy
    ##(node)##
    node = MyNode()       # create node
    rclpy.spin(node)      # node will be kept alive until ^C
    rclpy.shutdown()
