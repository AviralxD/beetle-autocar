#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class BeetleSerial(Node):
    def __init__(self):
        super().__init__('beetle_serial')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('command_timeout', 0.5)
        self.declare_parameter('publish_rate', 20.0)
        self.declare_parameter('max_throttle', 1.0)
        self.declare_parameter('max_steering', 1.0)

        self.serial_connection = None
        self.last_command = Twist()
        self.last_command_time = self.get_clock().now()
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.command_callback,
            10,
        )
        self.timer = self.create_timer(
            1.0 / self.get_parameter('publish_rate').value,
            self.send_command,
        )

    def command_callback(self, message):
        self.last_command = message
        self.last_command_time = self.get_clock().now()

    def connect_serial(self):
        try:
            import serial

            self.serial_connection = serial.Serial()
            self.serial_connection.port = self.get_parameter('serial_port').value
            self.serial_connection.baudrate = self.get_parameter('baud_rate').value
            self.serial_connection.timeout = 0.1
            self.serial_connection.dsrdtr = False
            self.serial_connection.rtscts = False
            self.serial_connection.dtr = False
            self.serial_connection.rts = False
            self.serial_connection.open()
            self.send_serial_command(0.0, 0.0)
            self.get_logger().info(
                'Connected to motor controller on %s'
                % self.get_parameter('serial_port').value
            )
        except (ImportError, OSError) as error:
            self.serial_connection = None
            self.get_logger().warn('Serial connection unavailable: %s' % error)

    def send_serial_command(self, throttle, steering):
        serial_message = 'T:{:.4f},S:{:.4f}\n'.format(throttle, steering)
        self.serial_connection.write(serial_message.encode('ascii'))
        self.serial_connection.flush()

    def send_command(self):
        if self.serial_connection is None:
            self.connect_serial()
            if self.serial_connection is None:
                return

        age = (self.get_clock().now() - self.last_command_time).nanoseconds / 1e9
        if age > self.get_parameter('command_timeout').value:
            throttle = 0.0
            steering = 0.0
        else:
            throttle = self.last_command.linear.x
            steering = self.last_command.angular.z

        throttle = max(
            -1.0,
            min(1.0, throttle / self.get_parameter('max_throttle').value),
        )
        steering = max(
            -1.0,
            min(1.0, steering / self.get_parameter('max_steering').value),
        )

        try:
            self.send_serial_command(throttle, steering)
        except OSError as error:
            self.get_logger().error('Serial write failed: %s' % error)
            self.serial_connection.close()
            self.serial_connection = None

    def destroy_node(self):
        if self.serial_connection is not None:
            try:
                self.send_serial_command(0.0, 0.0)
            finally:
                self.serial_connection.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BeetleSerial()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()