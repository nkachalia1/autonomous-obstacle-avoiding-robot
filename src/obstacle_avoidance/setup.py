import glob
import os

from setuptools import setup

package_name = "obstacle_avoidance"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "config"),
            glob.glob("config/*.yaml"),
        ),
        (
            os.path.join("share", package_name, "launch"),
            glob.glob("launch/*.launch.py"),
        ),
        (
            os.path.join("share", package_name, "worlds"),
            glob.glob("worlds/*.world"),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Neel Kachalia",
    maintainer_email="nkachalia1@gmail.com",
    description="Reactive LiDAR obstacle avoidance for a simulated TurtleBot3 robot.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "obstacle_avoidance_node = obstacle_avoidance.obstacle_avoidance_node:main",
        ],
    },
)
