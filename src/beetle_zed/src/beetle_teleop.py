#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Joy


class BeetleTeleop(Node):
    def __init__(self):
        super().__init__('beetle_teleop')

        self.declare_parameter('throttle_axis', 1)
        self.declare_parameter('steering_axis', 3)
        self.declare_parameter('deadman_button', 4)
        self.declare_parameter('require_deadman', True)
        self.declare_parameter('max_throttle', 1.0)
        self.declare_parameter('max_steering', 1.0)

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10,
        )

    def joy_callback(self, message):
        throttle_axis = self.get_parameter('throttle_axis').value
        steering_axis = self.get_parameter('steering_axis').value
        deadman_button = self.get_parameter('deadman_button').value
        require_deadman = self.get_parameter('require_deadman').value

        enabled = not require_deadman
        if require_deadman and 0 <= deadman_button < len(message.buttons):
            enabled = message.buttons[deadman_button] == 1

        command = Twist()
        if enabled:
            if 0 <= throttle_axis < len(message.axes):
                command.linear.x = (
                    message.axes[throttle_axis]
                    * self.get_parameter('max_throttle').value
                )
            if 0 <= steering_axis < len(message.axes):
                command.angular.z = (
                    message.axes[steering_axis]
                    * self.get_parameter('max_steering').value
                )

        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = BeetleTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()