from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = LaunchConfiguration("params_file")
    turtlebot3_model = LaunchConfiguration("turtlebot3_model")

    turtlebot3_gazebo_launch = PathJoinSubstitution(
        [
            FindPackageShare("turtlebot3_gazebo"),
            "launch",
            "empty_world.launch.py",
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "turtlebot3_model",
                default_value="burger",
                description="TurtleBot3 model: burger, waffle, or waffle_pi.",
            ),
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
            SetEnvironmentVariable("TURTLEBOT3_MODEL", turtlebot3_model),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(turtlebot3_gazebo_launch)
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
