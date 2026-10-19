from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'joy_device_id',
            default_value='0',
            description='Joystick device id; 0 selects /dev/input/js0',
        ),
        DeclareLaunchArgument(
            'throttle_axis',
            default_value='1',
            description='Joy axis used for forward and reverse throttle',
        ),
        DeclareLaunchArgument(
            'steering_axis',
            default_value='3',
            description='Joy axis used for left and right steering',
        ),
        DeclareLaunchArgument(
            'deadman_button',
            default_value='4',
            description='Joy button held while driving is enabled',
        ),
        DeclareLaunchArgument(
            'require_deadman',
            default_value='true',
            description='Require the deadman button to be held while driving',
        ),
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/ttyACM0',
            description='Serial device connected to the motor controller',
        ),
        DeclareLaunchArgument(
            'baud_rate',
            default_value='115200',
            description='Serial baud rate for the motor controller',
        ),
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[{
                'device_id': LaunchConfiguration('joy_device_id'),
                'deadzone': 0.05,
                'autorepeat_rate': 20.0,
            }],
        ),
        Node(
            package='beetle_zed',
            executable='beetle_teleop',
            name='beetle_teleop',
            parameters=[{
                'throttle_axis': LaunchConfiguration('throttle_axis'),
                'steering_axis': LaunchConfiguration('steering_axis'),
                'deadman_button': LaunchConfiguration('deadman_button'),
                'require_deadman': LaunchConfiguration('require_deadman'),
            }],
        ),
        Node(
            package='beetle_zed',
            executable='beetle_serial',
            name='beetle_serial',
            parameters=[{
                'serial_port': LaunchConfiguration('serial_port'),
                'baud_rate': LaunchConfiguration('baud_rate'),
            }],
        ),
    ])