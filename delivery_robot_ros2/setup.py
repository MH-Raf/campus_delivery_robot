from glob import glob
from setuptools import find_packages, setup

package_name = "uunit_ros2_demo"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/rviz", glob("rviz/*.rviz")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Course Staff",
    maintainer_email="course@example.com",
    description="Учебный демо-пакет ROS 2 (Jazzy) для ЛР4: cmd_vel -> odom/path/marker + сервисы сценариев.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "robot_node = uunit_ros2_demo.robot_node:main",
            "operator_node = uunit_ros2_demo.operator_node:main",
        ],
    },
)

