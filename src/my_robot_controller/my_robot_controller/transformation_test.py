import rclpy
from rclpy.node import Node
import tf2_ros
import numpy as np
import tf2_py
import tf2_msgs.msg
import asyncio
import time
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R
from rclpy.qos import QoSProfile, ReliabilityPolicy

class TFListenerNode(Node):

    # static transform data
    base_link__shell_link = [[0., 0., 0.0942], [0., 0., 0., 1.]]
    shell_link__oakd_camera_bracket = [[-0.118, 0., 0.05257], [0., 0., 0., 1.]]
    oakd_camera_bracket__oakd_link = [[0.0584, 0., 0.9676], [0., 0., 0., 1.]]
    oakd_link__oakd_rgb_camera_frame = [[0., 0., 0.], [0., 0., 0., 1.]]
    oakd_rgb_camera_frame__oakd_rgb_camera_optical_frame = [[0., 0., 0.], [0.5, -0.5, 0.5, -0.5]]

    def __init__(self):
        super().__init__('tf_listener_node')
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.get_logger().info("start!#@!")
        
        qos_profile = QoSProfile(
            depth = 10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        # Subscribe to the /odom topic to get transformation related to odom 
        self.tf_subscriber = self.create_subscription(
            Odometry,
            '/arches/odom',
            self.do_odom_transform_callback,
            qos_profile)
        
        # Subscribe to the /tf topic to get transformation related to tf


    def do_odom_transform_callback(self, msg):
        # Process the TF data here
        # You can access the transformations using msg.transforms

        # Wait for 2 seconds to give tf_buffer some time to fill up
        self.get_logger().info("Received TF data. Waiting for 2 seconds to process.")
        self.do_static_transform()
        time.sleep(2.0)

        print('source: odom')
        print('child: base_link')

        translation = msg.pose.pose.position
        rotation = msg.pose.pose.orientation
        transform_matrix = self.odom_get_transform_matrix(translation, rotation)
        print(transform_matrix)
        print()

    def do_static_transform(self):
        print('now do static transform...')
        translation = self.base_link__shell_link[0]
        rotation = self.base_link__shell_link[1]
        transform_matrix = self.static_get_transform_matrix(translation, rotation)
        print('base_link => shell_link')
        print(transform_matrix)

        translation = self.shell_link__oakd_camera_bracket[0]
        rotation = self.shell_link__oakd_camera_bracket[1]
        transform_matrix = self.static_get_transform_matrix(translation, rotation)
        print('shell_link => oakd_camera_bracket')
        print(transform_matrix)

        translation = self.oakd_camera_bracket__oakd_link[0]
        rotation = self.oakd_camera_bracket__oakd_link[1]
        transform_matrix = self.static_get_transform_matrix(translation, rotation)
        print('oakd_camera_bracket => oakd_link')
        print(transform_matrix)

        translation = self.oakd_link__oakd_rgb_camera_frame[0]
        rotation = self.oakd_link__oakd_rgb_camera_frame[1]
        transform_matrix = self.static_get_transform_matrix(translation, rotation)
        print('oakd_link => oakd_rgb_camera_frame')
        print(transform_matrix)

        translation = self.oakd_rgb_camera_frame__oakd_rgb_camera_optical_frame[0]
        rotation = self.oakd_rgb_camera_frame__oakd_rgb_camera_optical_frame[1]
        transform_matrix = self.static_get_transform_matrix(translation, rotation)
        print('oakd_rgb_camera_frame => oakd_rgb_camera_optical_frame')
        print(transform_matrix)

        print()


    def odom_get_transform_matrix(self, translation ,rotation):
        print('translation x:', translation.x)
        print('translation y:', translation.y)
        print('translation z:', translation.z)

        print('rotation x:', rotation.x)
        print('rotation y:', rotation.y)
        print('rotation z:', rotation.z)
        print('rotation w:', rotation.w)

        # convert rotation data into matrix
        r = R.from_quat([rotation.x, rotation.y, 
                         rotation.z, rotation.w])
        rotation_matrix = r.as_matrix()
        
        # create new ones column
        zero_row = np.zeros((1, 3))
        transform_matrix = np.vstack((rotation_matrix, zero_row))
        
        # create new zero row
        ones_column = np.ones((4, 1))
        transform_matrix = np.hstack((transform_matrix, ones_column))

        transform_matrix[0][3] = translation.x
        transform_matrix[1][3] = translation.y
        transform_matrix[2][3] = translation.z

        return transform_matrix
    
    def static_get_transform_matrix(self, translation, rotation):
        print('translation x:', translation[0])
        print('translation y:', translation[1])
        print('translation z:', translation[2])

        print('rotation x:', rotation[0])
        print('rotation y:', rotation[1])
        print('rotation z:', rotation[2])
        print('rotation w:', rotation[3])

        # convert rotation data into matrix
        r = R.from_quat([rotation[0], rotation[1], 
                         rotation[2], rotation[3]])
        rotation_matrix = r.as_matrix()
        
        # create new ones column
        zero_row = np.zeros((1, 3))
        transform_matrix = np.vstack((rotation_matrix, zero_row))
        
        # create new zero row
        ones_column = np.ones((4, 1))
        transform_matrix = np.hstack((transform_matrix, ones_column))

        transform_matrix[0][3] = translation[0]
        transform_matrix[1][3] = translation[1]
        transform_matrix[2][3] = translation[2]

        return transform_matrix


def main(args=None):
    rclpy.init(args=args)

    tf_listener_node = TFListenerNode()
    rclpy.spin(tf_listener_node)
    tf_listener_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

