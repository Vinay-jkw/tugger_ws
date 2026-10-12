import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory(
        'tugger_description'
    )
    gazebo_share = get_package_share_directory('ros_gz_sim')

    pkg_share_parent = os.path.dirname(description_share)

    # Allow Gazebo to resolve model://tugger_description/...
    ign_resource_path = AppendEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=pkg_share_parent
    )
    gz_resource_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=pkg_share_parent
    )
    sdf_model_path = AppendEnvironmentVariable(
        name='SDFORMAT_MODEL_PATH',
        value=pkg_share_parent
    )

    xacro_file = os.path.join(
        description_share, 'urdf', 'tugger.urdf.xacro'
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': '-r empty.sdf',
            'on_exit_shutdown': 'true',
        }.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='tugger_robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file]),
            'use_sim_time': True,
        }],
    )

    spawn_tugger = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'tugger',
            '-allow_renaming', 'true',
        ],
        output='screen',
    )

    return LaunchDescription([
        ign_resource_path,
        gz_resource_path,
        sdf_model_path,
        gazebo_launch,
        robot_state_publisher,
        spawn_tugger,
    ])
