from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = LaunchConfiguration("params_file")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("obstacle_avoidance"),
                        "config",
                        "avoidance.yaml",
                    ]
                ),
                description="Path to the obstacle avoidance parameter file.",
            ),
            Node(
                package="obstacle_avoidance",
                executable="obstacle_avoidance_node",
                name="obstacle_avoidance_node",
                output="screen",
                parameters=[params_file],
            ),
        ]
    )

