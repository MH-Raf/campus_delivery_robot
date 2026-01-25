from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description() -> LaunchDescription:
    pkg = "uunit_ros2_demo"
    share_dir = get_package_share_directory(pkg)

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "namespace",
                default_value="demo",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=os.path.join(share_dir, "config", "params.yaml"),
            ),
            DeclareLaunchArgument("use_operator", default_value="true"),
            DeclareLaunchArgument("use_rviz", default_value="false"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=os.path.join(share_dir, "rviz", "demo.rviz"),
            ),

            Node(
                package=pkg,
                executable="robot_node",
                name="robot_node",
                namespace=LaunchConfiguration("namespace"),
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
            ),

            Node(
                package=pkg,
                executable="operator_node",
                name="operator_node",
                namespace=LaunchConfiguration("namespace"),
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
                condition=IfCondition(LaunchConfiguration("use_operator")),
            ),

            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", LaunchConfiguration("rviz_config")],
                condition=IfCondition(LaunchConfiguration("use_rviz")),
            ),
        ]
    )
