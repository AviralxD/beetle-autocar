import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    beetle_zed_dir = get_package_share_directory('beetle_zed')
    zed_wrapper_dir = get_package_share_directory('zed_display_rviz2')
    
    custom_params_file = os.path.join(
        beetle_zed_dir,
        'config',
        'zed2i_params_slam.yaml'
    )
    
    zed_camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                zed_wrapper_dir,
                'launch',
                'display_zed_cam.launch.py'
            )
        ),
        launch_arguments={
            'camera_model': 'zed2i',
            'config_path': custom_params_file
        }.items()
    )

    return LaunchDescription([
        zed_camera_launch
    ])