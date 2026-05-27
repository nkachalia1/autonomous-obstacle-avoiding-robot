# Demo Checklist

Use this when turning the project into a GitHub portfolio piece.

## Before Recording

- Build with `colcon build --symlink-install`.
- Source the workspace with `source install/setup.bash`.
- Start the simulation with `ros2 launch obstacle_avoidance simulation.launch.py`.
- Confirm `/scan` is publishing.
- Confirm `/cmd_vel` changes when obstacles are near.
- Open RViz and add `LaserScan`, `RobotModel`, and `TF`.

## Shots To Capture

- Gazebo view of the robot driving around obstacles.
- RViz view with LiDAR points visible.
- Terminal showing `ros2 topic echo /cmd_vel`.
- A quick config edit showing parameter tuning.

## README Assets

- Put short GIFs or compressed clips in `videos/`, or link to YouTube.
- Put screenshots in a future `images/` folder.
- Keep the README focused on the result, setup, architecture, and lessons.

## Suggested Demo Script

1. Show Gazebo with the robot spawned.
2. Show RViz LiDAR points.
3. Place or approach an obstacle.
4. Show the robot turning away.
5. Show `/cmd_vel` updating in the terminal.

